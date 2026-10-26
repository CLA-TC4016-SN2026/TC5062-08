from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.settings import settings

JWT_ALGORITHM = "HS256"


def error_body(code: str, message: str) -> dict[str, Any]:
    return {"codigo": code, "mensaje": message}


def create_access_token(cuenta_id: uuid.UUID | str, tipo: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(cuenta_id),
        "tipo": tipo,
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
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail=error_body("token_expirado", "La sesión venció. Inicia sesión de nuevo."),
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401, detail=error_body("token_invalido", "El token no es válido.")
        ) from exc

    cuenta_id, tipo = payload.get("sub"), payload.get("tipo")
    if not cuenta_id or not tipo:
        raise HTTPException(status_code=401, detail=error_body("token_invalido", "El token no es válido."))
    try:
        return {"id": uuid.UUID(cuenta_id), "tipo": tipo}
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=401, detail=error_body("token_invalido", "El token no es válido.")
        ) from exc


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
) -> str:
    """Returns 'operador' or 'medico' depending on how the caller is allowed in, else 403.

    Médico access requires a 'vigente' vinculación that hasn't expired. This enforces
    repository-level access only; it does not yet apply the finer-grained document
    'alcance' (date range / document type / explicit document list) stored in
    alcances_vinculacion — see revision_seguridad.md for that known limitation.
    """
    operator_id = _repository_operator(connection, repositorio_id)
    if operator_id == current["id"]:
        return "operador"
    if current["tipo"] == "medico":
        linked = connection.execute(
            text(
                """
                SELECT 1 FROM vinculaciones
                WHERE repositorio_id = :repo AND medico_cuenta_id = :doctor
                  AND estado = 'vigente' AND (vence_en IS NULL OR vence_en > now())
                """
            ),
            {"repo": repositorio_id, "doctor": current["id"]},
        ).first()
        if linked is not None:
            return "medico"
    raise HTTPException(
        status_code=403, detail=error_body("sin_permiso", "No tienes acceso a este repositorio.")
    )
