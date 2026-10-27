from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.database import engine
from src.settings import settings

JWT_ALGORITHM = "HS256"
REQUIRED_CLAIMS = ["exp", "iat", "sub", "jti"]


def error_body(code: str, message: str) -> dict[str, Any]:
    return {"codigo": code, "mensaje": message}


def create_access_token(cuenta_id: uuid.UUID | str, tipo: str, jti: uuid.UUID | str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(cuenta_id),
        "tipo": tipo,
        "jti": str(jti),
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expiration),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def get_current_account(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail=error_body("no_autenticado", "Falta el encabezado Authorization: Bearer <token>."),
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[JWT_ALGORITHM],
            options={"require": REQUIRED_CLAIMS},
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail=error_body("token_expirado", "La sesión venció. Inicia sesión de nuevo."),
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401, detail=error_body("token_invalido", "El token no es válido.")
        ) from exc

    cuenta_id, tipo, jti = payload.get("sub"), payload.get("tipo"), payload.get("jti")
    if not cuenta_id or not tipo or not jti:
        raise HTTPException(status_code=401, detail=error_body("token_invalido", "El token no es válido."))
    try:
        account_id = uuid.UUID(cuenta_id)
        session_id = uuid.UUID(jti)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=401, detail=error_body("token_invalido", "El token no es válido.")
        ) from exc

    with engine.begin() as connection:
        active_session = connection.execute(
            text(
                """
                UPDATE sesiones
                SET ultima_actividad_en = now(), expira_en = now() + interval '720 hours'
                WHERE id = :session_id AND cuenta_id = :account_id
                  AND revocada_en IS NULL AND expira_en > now()
                RETURNING id
                """
            ),
            {"session_id": session_id, "account_id": account_id},
        ).first()
    if active_session is None:
        raise HTTPException(
            status_code=401,
            detail=error_body("token_invalido", "La sesión ya no es válida. Inicia sesión de nuevo."),
        )

    return {"id": account_id, "tipo": tipo}


CurrentAccount = Annotated[dict[str, Any], Depends(get_current_account)]


def require_roles(*roles: str):
    def dependency(current: CurrentAccount) -> dict[str, Any]:
        if current["tipo"] not in roles:
            raise HTTPException(
                status_code=403,
                detail=error_body("sin_permiso", "Tu cuenta no tiene permiso para esta acción."),
            )
        return current

    return dependency


def _repository_operator(connection: Connection, repositorio_id: uuid.UUID) -> uuid.UUID:
    operator_id = connection.execute(
        text("SELECT operador_cuenta_id FROM repositorios WHERE id = :id AND eliminado_en IS NULL"),
        {"id": repositorio_id},
    ).scalar_one_or_none()
    if operator_id is None:
        raise HTTPException(
            status_code=404,
            detail=error_body("repositorio_no_encontrado", "No se encontró el repositorio."),
        )
    return operator_id


def require_repository_operator(
    connection: Connection, repositorio_id: uuid.UUID, current: dict[str, Any]
) -> None:
    operator_id = _repository_operator(connection, repositorio_id)
    if operator_id != current["id"]:
        raise HTTPException(
            status_code=403,
            detail=error_body(
                "sin_permiso", "Esta acción solo la puede realizar quien administra el repositorio."
            ),
        )


def require_repository_access(
    connection: Connection, repositorio_id: uuid.UUID, current: dict[str, Any]
) -> tuple[str, uuid.UUID | None]:
    """Returns (tier, vinculacion_id): tier is 'operador' or 'medico', else 403.

    vinculacion_id is only set for 'medico' and identifies which vinculación granted
    access, so callers can apply that vinculación's document-level 'alcance' (date
    range / document type / explicit document list) via medico_document_allowed /
    medico_document_sql_filter below. Repository-level access only requires a
    'vigente', non-expired vinculación; it says nothing about which documents within
    the repository that vinculación actually covers.
    """
    operator_id = _repository_operator(connection, repositorio_id)
    if operator_id == current["id"]:
        return "operador", None
    if current["tipo"] == "medico":
        linked = connection.execute(
            text(
                """
                SELECT id FROM vinculaciones
                WHERE repositorio_id = :repo AND medico_cuenta_id = :doctor
                  AND estado = 'vigente' AND (vence_en IS NULL OR vence_en > now())
                """
            ),
            {"repo": repositorio_id, "doctor": current["id"]},
        ).scalar_one_or_none()
        if linked is not None:
            return "medico", linked
    raise HTTPException(
        status_code=403, detail=error_body("sin_permiso", "No tienes acceso a este repositorio.")
    )


def _vinculacion_alcance(connection: Connection, vinculacion_id: uuid.UUID) -> dict[str, Any]:
    row = connection.execute(
        text(
            "SELECT tipo, fecha_desde, fecha_hasta FROM alcances_vinculacion WHERE vinculacion_id = :id"
        ),
        {"id": vinculacion_id},
    ).mappings().first()
    return dict(row) if row is not None else {"tipo": "total", "fecha_desde": None, "fecha_hasta": None}


def medico_document_sql_filter(
    connection: Connection, vinculacion_id: uuid.UUID
) -> tuple[str, dict[str, Any]]:
    """Extra SQL WHERE fragment (+ params) restricting a documentos query to a médico's alcance."""
    alcance = _vinculacion_alcance(connection, vinculacion_id)
    if alcance["tipo"] == "total":
        return "TRUE", {}
    if alcance["tipo"] == "rango_fechas":
        return "fecha_documento BETWEEN :alcance_desde AND :alcance_hasta", {
            "alcance_desde": alcance["fecha_desde"],
            "alcance_hasta": alcance["fecha_hasta"],
        }
    if alcance["tipo"] == "tipos":
        return (
            "tipo IN (SELECT tipo_documento FROM alcances_vinculacion_tipos WHERE vinculacion_id = :alcance_vinc)",
            {"alcance_vinc": vinculacion_id},
        )
    if alcance["tipo"] == "documentos":
        return (
            "id IN (SELECT documento_id FROM vinculaciones_documentos WHERE vinculacion_id = :alcance_vinc)",
            {"alcance_vinc": vinculacion_id},
        )
    return "FALSE", {}


def medico_document_allowed(
    connection: Connection,
    vinculacion_id: uuid.UUID,
    documento_id: uuid.UUID,
    tipo_documento: str,
    fecha_documento: date | str | None,
) -> bool:
    """Whether a single document falls within a médico's vinculación alcance."""
    alcance = _vinculacion_alcance(connection, vinculacion_id)
    if alcance["tipo"] == "total":
        return True
    if isinstance(fecha_documento, str):
        fecha_documento = date.fromisoformat(fecha_documento)
    if alcance["tipo"] == "rango_fechas":
        if fecha_documento is None:
            return False
        return alcance["fecha_desde"] <= fecha_documento <= alcance["fecha_hasta"]
    if alcance["tipo"] == "tipos":
        return (
            connection.execute(
                text(
                    "SELECT 1 FROM alcances_vinculacion_tipos WHERE vinculacion_id = :vinc AND tipo_documento = :tipo"
                ),
                {"vinc": vinculacion_id, "tipo": tipo_documento},
            ).first()
            is not None
        )
    if alcance["tipo"] == "documentos":
        return (
            connection.execute(
                text(
                    "SELECT 1 FROM vinculaciones_documentos WHERE vinculacion_id = :vinc AND documento_id = :doc"
                ),
                {"vinc": vinculacion_id, "doc": documento_id},
            ).first()
            is not None
        )
    return False
