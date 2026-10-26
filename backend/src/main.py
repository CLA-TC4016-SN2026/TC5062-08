from __future__ import annotations

import hashlib
import hmac
import io
import logging
import secrets
import uuid
import zipfile
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from functools import lru_cache
from typing import Annotated, Any, Literal

import yaml
from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.auth import (
    CurrentAccount,
    create_access_token,
    require_repository_access,
    require_repository_operator,
    require_roles,
)
from src.database import assert_database_ready, db_error_to_http, engine
from src.settings import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("repossalud.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    assert_database_ready()
    yield


app = FastAPI(
    title="RepoSalud API",
    version="1.0.0",
    description=(
        "Servicios CRUD de desarrollo basados en S04_A3/openapi_equipo.yaml. "
        "Autenticación JWT (Authorization: Bearer <token>) y control de acceso por rol/"
        "titularidad del repositorio."
    ),
    servers=[{"url": "http://localhost:8000/api/v1", "description": "Desarrollo local"}],
    lifespan=lifespan,
)
def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Could not locate repository root (no .git found above src/).")


def _find_contract_path() -> Path:
    repo_root = _find_repo_root(Path(__file__).resolve())
    nested = repo_root / "S05_S06_A1" / "S04_A3" / "openapi_equipo.yaml"
    if nested.exists():
        return nested
    return repo_root / "S05_S06_A1" / "openapi_equipo.yaml"


API_PREFIX = "/api/v1"
CONTRACT_PATH = _find_contract_path()
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "application/pdf": "pdf",
}
DEV_OTP_CODE = "000000"


@lru_cache(maxsize=1)
def contract_openapi() -> dict[str, Any]:
    with CONTRACT_PATH.open(encoding="utf-8") as contract_file:
        schema = yaml.safe_load(contract_file)
    schema["servers"] = [{"url": API_PREFIX, "description": "Desarrollo local"}]
    return schema


app.openapi = contract_openapi


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class RegistrationRequest(RequestModel):
    nombre: Annotated[str, StringConstraints(min_length=1)]
    correo: EmailStr
    contrasena: Annotated[str, StringConstraints(min_length=10)]
    tipoCuenta: Literal["paciente", "cuidador", "medico"]
    avisoPrivacidadAceptado: Literal[True]
    consentimientoDatosSalud: Literal[True]


class LoginRequest(RequestModel):
    correo: EmailStr
    contrasena: str


class LoginCodeRequest(RequestModel):
    desafioId: uuid.UUID
    codigo: Annotated[str, StringConstraints(pattern=r"^[0-9]{6}$")]


class RepositoryCreateRequest(RequestModel):
    titularNombreCompleto: Annotated[str, StringConstraints(min_length=1)]
    titularEsOperador: bool
    declaracionAutorizacion: bool | None = None
    tamanoTexto: Literal["normal", "grande"] = "normal"


class PreferencesPatchRequest(RequestModel):
    tamanoTexto: Literal["normal", "grande"] | None = None


class DocumentMetadataPatchRequest(RequestModel):
    fecha: date | None = None
    tipo: Literal["laboratorio", "informe_imagen", "receta", "otro"] | None = None


class DocumentConfirmRequest(RequestModel):
    fecha: date
    tipo: Literal["laboratorio", "informe_imagen", "receta", "otro"]


class SearchCreateRequest(RequestModel):
    consulta: Annotated[str, StringConstraints(min_length=1, max_length=500)]


class AccessScope(RequestModel):
    tipo: Literal["total", "rango_fechas", "tipos", "documentos"]
    fechaDesde: date | None = None
    fechaHasta: date | None = None
    tipos: list[Literal["laboratorio", "informe_imagen", "receta", "otro"]] | None = None
    documentoIds: list[uuid.UUID] | None = None


class LinkCreateRequest(RequestModel):
    correoMedico: EmailStr
    alcance: AccessScope
    vigenciaDias: int | None = Field(default=None, ge=1, le=365)
    sinVencimiento: bool = False


class AccountRecoveryRequest(RequestModel):
    correo: EmailStr


class AccountResetRequest(RequestModel):
    token: str
    contrasenaNueva: Annotated[str, StringConstraints(min_length=10)]


class VerifyEmailRequest(RequestModel):
    token: str


def error_body(code: str, message: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"codigo": code, "mensaje": message}
    if details is not None:
        result["detalles"] = details
    return result


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "campo": ".".join(str(part) for part in error["loc"] if part != "body"),
            "problema": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=error_body("datos_invalidos", "La solicitud contiene datos inválidos.", details),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if isinstance(exc.detail, dict) and {"codigo", "mensaje"} <= exc.detail.keys():
        body = exc.detail
    else:
        defaults = {
            400: ("datos_invalidos", "La solicitud contiene datos inválidos."),
            401: ("no_autenticado", "La solicitud no es válida."),
            403: ("sin_permiso", "La operación no está disponible en esta actividad."),
            404: ("recurso_no_encontrado", "El recurso solicitado no existe."),
            413: ("archivo_demasiado_grande", "El archivo supera los 10 MB."),
            422: ("datos_invalidos", "La solicitud contiene datos inválidos."),
            429: ("demasiadas_solicitudes", "Demasiadas solicitudes."),
            500: ("error_interno", "Ocurrió un error interno."),
            503: ("base_no_disponible", "La base de datos no está disponible."),
        }
        code, message = defaults.get(
            exc.status_code, ("error_solicitud", str(exc.detail))
        )
        body = error_body(code, message)
    return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database operation failed", exc_info=exc)
    mapped = db_error_to_http(exc)
    return JSONResponse(status_code=mapped.status_code, content=mapped.detail)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def hash_secret(value: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_secret(value: str, encoded: str) -> bool:
    try:
        algorithm, salt_hex, expected = encoded.split("$", maxsplit=2)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", value.encode("utf-8"), bytes.fromhex(salt_hex), 310_000
        )
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


def as_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        return None


def repository_row(connection: Any, repository_id: uuid.UUID) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT r.id, r.creado_en, r.titular_es_operador, r.autorizacion_declarada_en,
                   r.autorizacion_declarada_por_cuenta_id, t.nombre_completo,
                   p.tamano_texto
            FROM repositorios AS r
            JOIN titulares_paciente AS t ON t.id = r.titular_paciente_id
            JOIN preferencias_accesibilidad AS p ON p.repositorio_id = r.id
            WHERE r.id = :id AND r.eliminado_en IS NULL
            """
        ),
        {"id": repository_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=error_body("no_encontrado", "No se encontró el repositorio."))
    declaration = None
    if row["autorizacion_declarada_en"] is not None:
        declaration = {
            "declaradaEn": row["autorizacion_declarada_en"].isoformat(),
            "declaradaPorUsuarioId": str(row["autorizacion_declarada_por_cuenta_id"]),
        }
    return {
        "id": str(row["id"]),
        "creadoEn": row["creado_en"].isoformat(),
        "titular": {"nombreCompleto": row["nombre_completo"]},
        "titularEsOperador": row["titular_es_operador"],
        "declaracionAutorizacion": declaration,
        "tamanoTexto": row["tamano_texto"],
    }


def my_repository_id(connection: Any, actor_id: uuid.UUID) -> uuid.UUID:
    repository_id = connection.execute(
        text(
            "SELECT id FROM repositorios WHERE operador_cuenta_id = :actor "
            "AND eliminado_en IS NULL"
        ),
        {"actor": actor_id},
    ).scalar_one_or_none()
    if repository_id is None:
        raise HTTPException(status_code=404, detail=error_body("repositorio_no_encontrado", "La cuenta no tiene repositorio."))
    return repository_id


def document_row(
    connection: Any, repository_id: uuid.UUID, document_id: uuid.UUID
) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT id, nombre_archivo, formato, tamano_bytes, hash_sha256, estado,
                   fecha_documento, tipo, sugerencia_fecha, sugerencia_tipo,
                   deteccion_disponible, subido_en
            FROM documentos
            WHERE id = :id AND repositorio_id = :repository AND eliminado_en IS NULL
            """
        ),
        {"id": document_id, "repository": repository_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=error_body("documento_no_encontrado", "No se encontró el documento."))
    return {
        "id": str(row["id"]),
        "nombreArchivo": row["nombre_archivo"],
        "formato": row["formato"],
        "tamanoBytes": row["tamano_bytes"],
        "hashSha256": row["hash_sha256"].strip(),
        "estado": row["estado"],
        "fechaDocumento": row["fecha_documento"].isoformat() if row["fecha_documento"] else None,
        "tipo": row["tipo"],
        "sugerenciaFecha": row["sugerencia_fecha"].isoformat() if row["sugerencia_fecha"] else None,
        "sugerenciaTipo": row["sugerencia_tipo"],
        "deteccionDisponible": row["deteccion_disponible"],
        "subidoEn": row["subido_en"].isoformat(),
    }


def document_summary(row: Any) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "nombreArchivo": row["nombre_archivo"],
        "fechaDocumento": row["fecha_documento"].isoformat(),
        "tipo": row["tipo"],
    }


def link_scope(connection: Any, link_id: uuid.UUID) -> dict[str, Any]:
    scope = connection.execute(
        text(
            "SELECT tipo, fecha_desde, fecha_hasta FROM alcances_vinculacion "
            "WHERE vinculacion_id = :id"
        ),
        {"id": link_id},
    ).mappings().first()
    if scope is None:
        raise HTTPException(status_code=404, detail=error_body("alcance_no_encontrado", "No se encontró el alcance."))
    result: dict[str, Any] = {"tipo": scope["tipo"]}
    if scope["tipo"] == "rango_fechas":
        result.update(
            fechaDesde=scope["fecha_desde"].isoformat(),
            fechaHasta=scope["fecha_hasta"].isoformat(),
        )
    elif scope["tipo"] == "tipos":
        result["tipos"] = connection.execute(
            text(
                "SELECT tipo_documento FROM alcances_vinculacion_tipos "
                "WHERE vinculacion_id = :id ORDER BY tipo_documento"
            ),
            {"id": link_id},
        ).scalars().all()
    elif scope["tipo"] == "documentos":
        result["documentoIds"] = [
            str(item)
            for item in connection.execute(
                text(
                    "SELECT documento_id FROM vinculaciones_documentos "
                    "WHERE vinculacion_id = :id ORDER BY documento_id"
                ),
                {"id": link_id},
            ).scalars().all()
        ]
    return result


def link_row(connection: Any, repository_id: uuid.UUID, link_id: uuid.UUID) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT v.id, v.repositorio_id, v.medico_cuenta_id, c.nombre, c.correo,
                   v.estado, v.vigencia_dias, v.sin_vencimiento, v.solicitada_en,
                   v.aceptada_en, v.vence_en, v.aviso_enviado_en
            FROM vinculaciones AS v
            JOIN cuentas AS c ON c.id = v.medico_cuenta_id
            WHERE v.id = :id AND v.repositorio_id = :repository
            """
        ),
        {"id": link_id, "repository": repository_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=error_body("vinculacion_no_encontrada", "No se encontró la vinculación."))
    return {
        "id": str(row["id"]),
        "repositorioId": str(row["repositorio_id"]),
        "medico": {
            "id": str(row["medico_cuenta_id"]),
            "nombre": row["nombre"],
            "correo": row["correo"],
        },
        "estado": row["estado"],
        "alcance": link_scope(connection, link_id),
        "vigenciaDias": row["vigencia_dias"],
        "sinVencimiento": row["sin_vencimiento"],
        "solicitadaEn": row["solicitada_en"].isoformat(),
        "aceptadaEn": row["aceptada_en"].isoformat() if row["aceptada_en"] else None,
        "venceEn": row["vence_en"].isoformat() if row["vence_en"] else None,
        "avisoEnviado": row["aviso_enviado_en"] is not None,
    }


def received_link_row(connection: Any, link_id: uuid.UUID) -> dict[str, Any]:
    row = connection.execute(
        text(
            """
            SELECT v.id, v.repositorio_id, r.titular_paciente_id, t.nombre_completo,
                   o.nombre AS operador_nombre, v.estado, v.vigencia_dias,
                   v.sin_vencimiento, v.vence_en
            FROM vinculaciones AS v
            JOIN repositorios AS r ON r.id = v.repositorio_id
            JOIN titulares_paciente AS t ON t.id = r.titular_paciente_id
            JOIN cuentas AS o ON o.id = r.operador_cuenta_id
            WHERE v.id = :id
            """
        ),
        {"id": link_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=error_body("vinculacion_no_encontrada", "No se encontró la vinculación."))
    return {
        "id": str(row["id"]),
        "repositorioId": str(row["repositorio_id"]),
        "nombrePaciente": row["nombre_completo"],
        "solicitadaPor": row["operador_nombre"],
        "estado": row["estado"],
        "alcance": link_scope(connection, link_id),
        "vigenciaDias": row["vigencia_dias"],
        "sinVencimiento": row["sin_vencimiento"],
        "venceEn": row["vence_en"].isoformat() if row["vence_en"] else None,
    }


def insert_scope(
    connection: Any,
    link_id: uuid.UUID,
    repository_id: uuid.UUID,
    scope: AccessScope,
) -> None:
    values = scope.model_dump()
    connection.execute(
        text(
            """
            INSERT INTO alcances_vinculacion
                (vinculacion_id, repositorio_id, tipo, fecha_desde, fecha_hasta)
            VALUES (:link, :repository, :tipo, :start_date, :end_date)
            """
        ),
        {
            "link": link_id,
            "repository": repository_id,
            "tipo": scope.tipo,
            "start_date": values.get("fechaDesde"),
            "end_date": values.get("fechaHasta"),
        },
    )
    if scope.tipo == "rango_fechas":
        if scope.fechaDesde is None or scope.fechaHasta is None or scope.fechaDesde > scope.fechaHasta:
            raise HTTPException(status_code=400, detail=error_body("alcance_invalido", "El rango de fechas no es válido."))
    elif scope.tipo == "tipos":
        if not scope.tipos or len(set(scope.tipos)) != len(scope.tipos):
            raise HTTPException(status_code=400, detail=error_body("alcance_invalido", "Selecciona tipos únicos."))
        for document_type in scope.tipos:
            connection.execute(
                text(
                    "INSERT INTO alcances_vinculacion_tipos "
                    "(vinculacion_id, tipo_documento) VALUES (:link, :type)"
                ),
                {"link": link_id, "type": document_type},
            )
    elif scope.tipo == "documentos":
        if not scope.documentoIds or len(set(scope.documentoIds)) != len(scope.documentoIds):
            raise HTTPException(status_code=400, detail=error_body("alcance_invalido", "Selecciona documentos únicos."))
        for document_id in scope.documentoIds:
            connection.execute(
                text(
                    """
                    INSERT INTO vinculaciones_documentos
                        (vinculacion_id, documento_id, repositorio_id)
                    SELECT :link, d.id, :repository FROM documentos AS d
                    WHERE d.id = :document AND d.repositorio_id = :repository
                      AND d.estado = 'confirmado' AND d.eliminado_en IS NULL
                    """
                ),
                {
                    "link": link_id,
                    "document": document_id,
                    "repository": repository_id,
                },
            )
            if connection.execute(
                text(
                    "SELECT 1 FROM vinculaciones_documentos "
                    "WHERE vinculacion_id = :link AND documento_id = :document"
                ),
                {"link": link_id, "document": document_id},
            ).first() is None:
                raise HTTPException(status_code=400, detail=error_body("alcance_invalido", "Un documento no pertenece al repositorio o no está confirmado."))


def user_response(row: Any) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "nombre": row["nombre"],
        "correo": row["correo"],
        "tipoCuenta": row["tipo"],
        "correoVerificado": row["correo_verificado_en"] is not None,
    }


@app.get(f"{API_PREFIX}/health", operation_id="verificarConexionBase")
def health() -> dict[str, str]:
    with engine.connect() as connection:
        version = connection.execute(text("SELECT version()")).scalar_one()
    return {"estado": "ok", "baseDatos": "PostgreSQL", "version": version}


@app.post(f"{API_PREFIX}/cuentas", status_code=201, operation_id="registrarCuenta", responses={400: {}, 429: {}, 500: {}, 503: {}})
def registrar_cuenta(body: RegistrationRequest) -> dict[str, Any]:
    with engine.begin() as connection:
        password_hash = hash_secret(body.contrasena)
        account_id = connection.execute(
            text(
                """
                INSERT INTO cuentas (nombre, correo, hash_contrasena, tipo)
                VALUES (:nombre, :correo, :password, :tipo)
                RETURNING id
                """
            ),
            {
                "nombre": body.nombre,
                "correo": str(body.correo).lower(),
                "password": password_hash,
                "tipo": body.tipoCuenta,
            },
        ).scalar_one()
        connection.execute(
            text(
                """
                INSERT INTO consentimientos_cuenta
                    (cuenta_id, version_aviso_privacidad, aviso_privacidad_aceptado,
                     consentimiento_datos_salud)
                VALUES (:account, 'v1', true, true)
                """
            ),
            {"account": account_id},
        )
        account = connection.execute(
            text("SELECT id, nombre, correo, tipo, correo_verificado_en FROM cuentas WHERE id = :id"),
            {"id": account_id},
        ).mappings().one()
    return user_response(account)


@app.post(f"{API_PREFIX}/cuentas/verificacion-correo", operation_id="verificarCorreo", responses={400: {}, 401: {}, 429: {}, 500: {}})
def verificar_correo(body: VerifyEmailRequest) -> dict[str, Any]:
    account_id = as_uuid(body.token)
    if account_id is None:
        raise HTTPException(status_code=401, detail=error_body("token_invalido", "El código de verificación no es válido."))
    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                UPDATE cuentas SET correo_verificado_en = COALESCE(correo_verificado_en, now())
                WHERE id = :id
                RETURNING id, nombre, correo, tipo, correo_verificado_en
                """
            ),
            {"id": account_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=401, detail=error_body("token_invalido", "El código de verificación no es válido."))
    return user_response(row)


@app.post(f"{API_PREFIX}/auth/desafios", status_code=201, operation_id="solicitarDesafioCodigo", responses={400: {}, 401: {}, 429: {}, 500: {}, 503: {}})
def solicitar_desafio(body: LoginRequest) -> dict[str, Any]:
    failure: tuple[int, dict[str, str]] | None = None
    challenge_id: Any = None
    with engine.begin() as connection:
        account = connection.execute(
            text(
                "SELECT id, nombre, correo, tipo, correo_verificado_en, hash_contrasena, "
                "intentos_contrasena_fallidos, bloqueada_hasta FROM cuentas WHERE lower(correo) = :email"
            ),
            {"email": str(body.correo).lower()},
        ).mappings().first()
        if account is None:
            failure = (401, error_body("credenciales_invalidas", "Correo o contraseña incorrectos"))
        elif account["bloqueada_hasta"] and account["bloqueada_hasta"] > now_utc():
            failure = (429, error_body("cuenta_bloqueada", "La cuenta está bloqueada temporalmente."))
        elif account["bloqueada_hasta"] and account["bloqueada_hasta"] <= now_utc():
            connection.execute(
                text(
                    "UPDATE cuentas SET intentos_contrasena_fallidos = 0, "
                    "bloqueada_desde = NULL, bloqueada_hasta = NULL WHERE id = :id"
                ),
                {"id": account["id"]},
            )
            account = dict(account)
            account["intentos_contrasena_fallidos"] = 0
            account["bloqueada_hasta"] = None

        if account is not None and failure is None and not verify_secret(body.contrasena, account["hash_contrasena"]):
            failed_attempts = min(account["intentos_contrasena_fallidos"] + 1, 5)
            connection.execute(
                text(
                    """
                    UPDATE cuentas SET
                        intentos_contrasena_fallidos = :attempts,
                        bloqueada_desde = CASE WHEN :attempts = 5 THEN now() ELSE NULL END,
                        bloqueada_hasta = CASE
                            WHEN :attempts = 5 THEN now() + interval '15 minutes'
                            ELSE NULL
                        END
                    WHERE id = :id
                    """
                ),
                {"attempts": failed_attempts, "id": account["id"]},
            )
            if failed_attempts >= 5:
                failure = (429, error_body("cuenta_bloqueada", "La cuenta está bloqueada temporalmente."))
            else:
                failure = (401, error_body("credenciales_invalidas", "Correo o contraseña incorrectos"))
        elif account is not None and failure is None:
            connection.execute(
                text(
                    "UPDATE cuentas SET intentos_contrasena_fallidos = 0, "
                    "bloqueada_desde = NULL, bloqueada_hasta = NULL WHERE id = :id"
                ),
                {"id": account["id"]},
            )
            if account["correo_verificado_en"] is None:
                failure = (401, error_body("cuenta_sin_verificar", "Verifica tu correo antes de iniciar sesión."))
            else:
                challenge_id = connection.execute(
                    text(
                        """
                        INSERT INTO desafios_otp (cuenta_id, codigo_hash, expira_en)
                        VALUES (:account, :code, now() + interval '5 minutes')
                        RETURNING id, expira_en
                        """
                    ),
                    {"account": account["id"], "code": hash_secret(DEV_OTP_CODE)},
                ).mappings().one()
    if failure is not None:
        raise HTTPException(status_code=failure[0], detail=failure[1])
    logger.info("Development OTP for challenge %s is %s", challenge_id["id"], DEV_OTP_CODE)
    return {"desafioId": str(challenge_id["id"]), "venceEn": challenge_id["expira_en"].isoformat()}


@app.post(f"{API_PREFIX}/auth/sesiones", status_code=201, operation_id="crearSesion", responses={400: {}, 401: {}, 429: {}, 500: {}})
def crear_sesion(body: LoginCodeRequest) -> dict[str, Any]:
    with engine.begin() as connection:
        challenge = connection.execute(
            text(
                """
                SELECT c.id, d.cuenta_id, d.codigo_hash, d.expira_en, d.usado_en,
                       c.nombre, c.correo, c.tipo, c.correo_verificado_en
                FROM desafios_otp AS d JOIN cuentas AS c ON c.id = d.cuenta_id
                WHERE d.id = :id
                """
            ),
            {"id": body.desafioId},
        ).mappings().first()
        if (
            challenge is None
            or challenge["usado_en"] is not None
            or challenge["expira_en"] <= now_utc()
            or not verify_secret(body.codigo, challenge["codigo_hash"])
        ):
            raise HTTPException(status_code=401, detail=error_body("codigo_invalido", "El código es incorrecto, venció o ya se usó."))
        connection.execute(
            text("UPDATE desafios_otp SET usado_en = now() WHERE id = :id"),
            {"id": body.desafioId},
        )
        connection.execute(
            text(
                """
                INSERT INTO sesiones (cuenta_id, ultima_actividad_en, expira_en)
                VALUES (:account, now(), now() + interval '720 hours')
                """
            ),
            {"account": challenge["cuenta_id"]},
        )
    return {
        "accessToken": create_access_token(challenge["id"], challenge["tipo"]),
        "tokenType": "Bearer",
        "usuario": user_response(challenge),
    }


@app.post(f"{API_PREFIX}/auth/recuperaciones", status_code=202, operation_id="solicitarRecuperacion", responses={400: {}, 429: {}, 500: {}, 503: {}})
def solicitar_recuperacion(body: AccountRecoveryRequest) -> dict[str, str]:
    with engine.begin() as connection:
        account_id = connection.execute(
            text("SELECT id FROM cuentas WHERE lower(correo) = :email"),
            {"email": str(body.correo).lower()},
        ).scalar_one_or_none()
        if account_id is not None:
            reset_token = str(account_id)
            connection.execute(
                text(
                    """
                    INSERT INTO tokens_cuenta (cuenta_id, tipo, token_hash, expira_en)
                    VALUES (:account, 'recuperacion_contrasena', :token, now() + interval '30 minutes')
                    ON CONFLICT (token_hash) DO UPDATE
                    SET expira_en = EXCLUDED.expira_en, usado_en = NULL
                    """
                ),
                {"account": account_id, "token": reset_token},
            )
            logger.info("Development password recovery token for account %s is its UUID", account_id)
    return {"mensaje": "Si el correo corresponde a una cuenta, recibirás instrucciones para recuperar el acceso."}


@app.post(f"{API_PREFIX}/auth/recuperaciones/restablecimiento", operation_id="restablecerContrasena", responses={400: {}, 401: {}, 429: {}, 500: {}})
def restablecer_contrasena(body: AccountResetRequest) -> dict[str, str]:
    with engine.begin() as connection:
        token = connection.execute(
            text(
                """
                SELECT id, cuenta_id FROM tokens_cuenta
                WHERE token_hash = :token AND tipo = 'recuperacion_contrasena'
                  AND usado_en IS NULL AND expira_en > now()
                """
            ),
            {"token": body.token},
        ).mappings().first()
        if token is None:
            raise HTTPException(status_code=401, detail=error_body("token_invalido", "El enlace ya se usó o venció."))
        connection.execute(
            text("UPDATE cuentas SET hash_contrasena = :password WHERE id = :account"),
            {"password": hash_secret(body.contrasenaNueva), "account": token["cuenta_id"]},
        )
        connection.execute(
            text("UPDATE tokens_cuenta SET usado_en = now() WHERE id = :id"),
            {"id": token["id"]},
        )
    return {"mensaje": "La contraseña se actualizó correctamente."}


@app.post(f"{API_PREFIX}/repositorios", status_code=201, operation_id="crearRepositorio", responses={400: {}, 401: {}, 403: {}, 500: {}})
def crear_repositorio(
    body: RepositoryCreateRequest,
    current: CurrentAccount,
) -> dict[str, Any]:
    with engine.begin() as connection:
        actor = current["id"]
        account = current["tipo"]
        if account == "medico":
            raise HTTPException(status_code=403, detail=error_body("sin_permiso", "Una cuenta médica no puede crear repositorios."))
        if body.titularEsOperador and account == "paciente":
            holder_account_id: uuid.UUID | None = actor
        elif not body.titularEsOperador:
            if account != "cuidador" or body.declaracionAutorizacion is not True:
                raise HTTPException(status_code=400, detail=error_body("autorizacion_requerida", "Se requiere la declaración de autorización del titular."))
            holder_account_id = None
        else:
            holder_account_id = None

        holder_id = connection.execute(
            text(
                """
                INSERT INTO titulares_paciente (nombre_completo, cuenta_id)
                VALUES (:name, :account) RETURNING id
                """
            ),
            {"name": body.titularNombreCompleto, "account": holder_account_id},
        ).scalar_one()
        repository_id = connection.execute(
            text(
                """
                INSERT INTO repositorios
                    (operador_cuenta_id, titular_paciente_id, titular_es_operador,
                     autorizacion_declarada_en, autorizacion_declarada_por_cuenta_id)
                VALUES (:operator, :holder, :self, :declared_at, :declared_by)
                RETURNING id
                """
            ),
            {
                "operator": actor,
                "holder": holder_id,
                "self": body.titularEsOperador,
                "declared_at": None if body.titularEsOperador else now_utc(),
                "declared_by": None if body.titularEsOperador else actor,
            },
        ).scalar_one()
        connection.execute(
            text(
                "INSERT INTO preferencias_accesibilidad (repositorio_id, tamano_texto) "
                "VALUES (:repo, :size)"
            ),
            {"repo": repository_id, "size": body.tamanoTexto},
        )
        return repository_row(connection, repository_id)


@app.get(f"{API_PREFIX}/repositorios/mio", operation_id="obtenerMiRepositorio", responses={401: {}, 403: {}, 404: {}, 500: {}})
def obtener_mi_repositorio(current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        return repository_row(connection, my_repository_id(connection, current["id"]))


@app.patch(f"{API_PREFIX}/repositorios/mio", operation_id="actualizarPreferenciasRepositorio", responses={400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def actualizar_preferencias_repositorio(
    body: PreferencesPatchRequest,
    current: CurrentAccount,
) -> dict[str, Any]:
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail=error_body("datos_invalidos", "Indica al menos una preferencia para actualizar."))
    with engine.begin() as connection:
        repository_id = my_repository_id(connection, current["id"])
        connection.execute(
            text("UPDATE preferencias_accesibilidad SET tamano_texto = :size WHERE repositorio_id = :repo"),
            {"size": changes["tamanoTexto"], "repo": repository_id},
        )
        return repository_row(connection, repository_id)


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}", operation_id="obtenerRepositorio", responses={401: {}, 403: {}, 404: {}, 500: {}})
def obtener_repositorio(repositorioId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        require_repository_access(connection, repositorioId, current)
        return repository_row(connection, repositorioId)


@app.delete(f"{API_PREFIX}/repositorios/{{repositorioId}}", status_code=204, operation_id="eliminarHistorial", responses={400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def eliminar_historial(
    repositorioId: uuid.UUID,
    confirmacion_nombre: Annotated[str, Header(alias="Confirmacion-Nombre")],
    current: CurrentAccount,
) -> Response:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        repository = connection.execute(
            text(
                """
                SELECT r.titular_paciente_id, t.nombre_completo
                FROM repositorios r JOIN titulares_paciente t ON t.id = r.titular_paciente_id
                WHERE r.id = :id AND r.eliminado_en IS NULL
                """
            ),
            {"id": repositorioId},
        ).mappings().first()
        if repository is None:
            raise HTTPException(status_code=404, detail=error_body("repositorio_no_encontrado", "No se encontró el repositorio."))
        if confirmacion_nombre != repository["nombre_completo"]:
            raise HTTPException(status_code=400, detail=error_body("confirmacion_invalida", "El nombre de confirmación no coincide con el titular."))
        connection.execute(
            text(
                """
                UPDATE vinculaciones SET estado = CASE
                    WHEN estado = 'pendiente_aceptacion' THEN 'cancelada'::estado_vinculacion
                    WHEN estado = 'vigente' THEN 'revocada'::estado_vinculacion
                    ELSE estado END
                WHERE repositorio_id = :repo AND estado IN ('pendiente_aceptacion', 'vigente')
                """
            ),
            {"repo": repositorioId},
        )
        connection.execute(
            text("UPDATE documentos SET eliminado_en = now() WHERE repositorio_id = :repo AND eliminado_en IS NULL"),
            {"repo": repositorioId},
        )
        connection.execute(
            text("UPDATE repositorios SET eliminado_en = now() WHERE id = :repo"),
            {"repo": repositorioId},
        )
    return Response(status_code=204)


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos", status_code=201, operation_id="subirDocumento", responses={400: {}, 401: {}, 403: {}, 404: {}, 413: {}, 500: {}})
async def subir_documento(
    repositorioId: uuid.UUID,
    current: CurrentAccount,
    archivo: UploadFile = File(...),
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    content_type = archivo.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=error_body("formato_invalido", "Solo se aceptan fotos JPG o PNG y archivos PDF."))
    payload = await archivo.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=error_body("archivo_demasiado_grande", "El archivo supera los 10 MB."))
    if not payload:
        raise HTTPException(status_code=400, detail=error_body("archivo_vacio", "El archivo está vacío."))

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    storage_key = f"{uuid.uuid4().hex}.{ALLOWED_CONTENT_TYPES[content_type]}"
    storage_path = settings.upload_dir / storage_key
    storage_path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    try:
        with engine.begin() as connection:
            require_repository_operator(connection, repositorioId, current)
            document_id = connection.execute(
                text(
                    """
                    INSERT INTO documentos
                        (repositorio_id, nombre_archivo, formato, deteccion_disponible,
                         tamano_bytes, hash_sha256, estado)
                    VALUES (:repo, :name, :format, false, :size, :hash, 'pendiente_confirmacion')
                    RETURNING id
                    """
                ),
                {
                    "repo": repositorioId,
                    "name": Path(archivo.filename or "documento").name,
                    "format": ALLOWED_CONTENT_TYPES[content_type],
                    "size": len(payload),
                    "hash": digest,
                },
            ).scalar_one()
            connection.execute(
                text(
                    """
                    INSERT INTO archivos_originales
                        (documento_id, clave_almacenamiento, tipo_contenido, metadatos_cifrado)
                    VALUES (:doc, :key, :type, '{}')
                    """
                ),
                {"doc": document_id, "key": storage_key, "type": content_type},
            )
            connection.execute(
                text(
                    "INSERT INTO documentos_indice_semantico (documento_id) VALUES (:doc)"
                ),
                {"doc": document_id},
            )
            result = document_row(connection, repositorioId, document_id)
    except Exception:
        storage_path.unlink(missing_ok=True)
        raise
    return result


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos", operation_id="listarDocumentos", responses={400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def listar_documentos(
    repositorioId: uuid.UUID,
    current: CurrentAccount,
    estado: Literal["pendiente_confirmacion", "confirmado"] | None = None,
    tipo: Literal["laboratorio", "informe_imagen", "receta", "otro"] | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamanoPagina: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    if desde and hasta and desde > hasta:
        raise HTTPException(status_code=400, detail=error_body("filtro_invalido", "La fecha inicial no puede ser posterior a la fecha final."))
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        if tier == "medico":
            # Un médico solo ve documentos confirmados, sin importar el filtro solicitado.
            estado = "confirmado"
        filters = [
            "repositorio_id = :repo",
            "eliminado_en IS NULL",
        ]
        params: dict[str, Any] = {
            "repo": repositorioId,
            "limit": tamanoPagina,
            "offset": (pagina - 1) * tamanoPagina,
        }
        if estado:
            filters.append("estado = :state")
            params["state"] = estado
        if tipo:
            filters.append("tipo = :type")
            params["type"] = tipo
        if desde:
            filters.append("fecha_documento >= :start")
            params["start"] = desde
        if hasta:
            filters.append("fecha_documento <= :end")
            params["end"] = hasta
        where = " AND ".join(filters)
        total = connection.execute(
            text(f"SELECT count(*) FROM documentos WHERE {where}"), params
        ).scalar_one()
        rows = connection.execute(
            text(
                "SELECT id FROM documentos WHERE "
                + where
                + " ORDER BY subido_en DESC LIMIT :limit OFFSET :offset"
            ),
            params,
        ).scalars().all()
        items = [document_row(connection, repositorioId, row_id) for row_id in rows]
    return {"items": items, "pagina": pagina, "tamanoPagina": tamanoPagina, "total": total}


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}", operation_id="obtenerDocumento", responses={401: {}, 403: {}, 404: {}, 500: {}})
def obtener_documento(repositorioId: uuid.UUID, documentoId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        document = document_row(connection, repositorioId, documentoId)
        if tier == "medico" and document["estado"] != "confirmado":
            raise HTTPException(status_code=403, detail=error_body("sin_permiso", "No tienes acceso a este documento."))
        return document


@app.patch(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}", operation_id="corregirMetadatos", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def corregir_metadatos(
    repositorioId: uuid.UUID,
    documentoId: uuid.UUID,
    body: DocumentMetadataPatchRequest,
    current: CurrentAccount,
) -> dict[str, Any]:
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail=error_body("datos_invalidos", "Indica al menos un metadato para corregir."))
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        actor = current["id"]
        current_doc = connection.execute(
            text(
                """
                SELECT fecha_documento, tipo, estado FROM documentos
                WHERE id = :id AND repositorio_id = :repo AND eliminado_en IS NULL
                """
            ),
            {"id": documentoId, "repo": repositorioId},
        ).mappings().first()
        if current_doc is None:
            raise HTTPException(status_code=404, detail=error_body("documento_no_encontrado", "No se encontró el documento."))
        if current_doc["estado"] != "confirmado":
            raise HTTPException(status_code=400, detail=error_body("documento_pendiente", "Confirma el documento antes de corregir sus metadatos."))
        for key, column, enum_value in (
            ("fecha", "fecha_documento", current_doc["fecha_documento"]),
            ("tipo", "tipo", current_doc["tipo"]),
        ):
            if key in changes:
                previous = enum_value.isoformat() if isinstance(enum_value, date) else enum_value
                connection.execute(
                    text(
                        """
                        INSERT INTO cambios_metadatos
                            (documento_id, realizado_por_cuenta_id, campo, valor_anterior)
                        VALUES (:doc, :actor, :field, :old)
                        """
                    ),
                    {"doc": documentoId, "actor": actor, "field": key, "old": str(previous)},
                )
        connection.execute(
            text(
                """
                UPDATE documentos SET
                    fecha_documento = COALESCE(:date, fecha_documento),
                    tipo = COALESCE(:type, tipo)
                WHERE id = :id AND repositorio_id = :repo
                """
            ),
            {"date": changes.get("fecha"), "type": changes.get("tipo"), "id": documentoId, "repo": repositorioId},
        )
        return document_row(connection, repositorioId, documentoId)


@app.delete(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}", status_code=204, operation_id="eliminarDocumento", responses={401: {}, 403: {}, 404: {}, 500: {}})
def eliminar_documento(repositorioId: uuid.UUID, documentoId: uuid.UUID, current: CurrentAccount) -> Response:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        result = connection.execute(
            text(
                """
                UPDATE documentos SET eliminado_en = now()
                WHERE id = :id AND repositorio_id = :repo AND eliminado_en IS NULL
                """
            ),
            {"id": documentoId, "repo": repositorioId},
        )
        if result.rowcount != 1:
            raise HTTPException(status_code=404, detail=error_body("documento_no_encontrado", "No se encontró el documento."))
    return Response(status_code=204)


@app.put(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}/confirmacion", operation_id="confirmarDocumento", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def confirmar_documento(
    repositorioId: uuid.UUID,
    documentoId: uuid.UUID,
    body: DocumentConfirmRequest,
    current: CurrentAccount,
) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        result = connection.execute(
            text(
                """
                UPDATE documentos SET estado = 'confirmado', fecha_documento = :date, tipo = :type
                WHERE id = :id AND repositorio_id = :repo AND estado = 'pendiente_confirmacion'
                  AND eliminado_en IS NULL
                """
            ),
            {"date": body.fecha, "type": body.tipo, "id": documentoId, "repo": repositorioId},
        )
        if result.rowcount != 1:
            exists = connection.execute(
                text("SELECT 1 FROM documentos WHERE id = :id AND repositorio_id = :repo AND eliminado_en IS NULL"),
                {"id": documentoId, "repo": repositorioId},
            ).first()
            if exists is None:
                raise HTTPException(status_code=404, detail=error_body("documento_no_encontrado", "No se encontró el documento."))
            raise HTTPException(status_code=400, detail=error_body("documento_ya_confirmado", "El documento ya fue confirmado."))
        return document_row(connection, repositorioId, documentoId)


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}/historial-cambios", operation_id="listarHistorialCambios", responses={401: {}, 403: {}, 404: {}, 500: {}})
def listar_historial_cambios(repositorioId: uuid.UUID, documentoId: uuid.UUID, current: CurrentAccount) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        document = document_row(connection, repositorioId, documentoId)
        if tier == "medico" and document["estado"] != "confirmado":
            raise HTTPException(status_code=403, detail=error_body("sin_permiso", "No tienes acceso a este documento."))
        rows = connection.execute(
            text(
                """
                SELECT fecha_hora, campo, valor_anterior, realizado_por_cuenta_id
                FROM cambios_metadatos WHERE documento_id = :id
                ORDER BY fecha_hora DESC
                """
            ),
            {"id": documentoId},
        ).mappings().all()
    return [
        {
            "fechaHora": row["fecha_hora"].isoformat(),
            "campo": row["campo"],
            "valorAnterior": row["valor_anterior"],
            "realizadoPorUsuarioId": str(row["realizado_por_cuenta_id"]),
        }
        for row in rows
    ]


def original_file(connection: Any, repository_id: uuid.UUID, document_id: uuid.UUID) -> tuple[Path, str, str, str]:
    row = connection.execute(
        text(
            """
            SELECT d.nombre_archivo, d.estado, a.clave_almacenamiento, a.tipo_contenido
            FROM documentos d JOIN archivos_originales a ON a.documento_id = d.id
            WHERE d.id = :doc AND d.repositorio_id = :repo AND d.eliminado_en IS NULL
            """
        ),
        {"doc": document_id, "repo": repository_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=error_body("documento_no_encontrado", "No se encontró el documento."))
    path = (settings.upload_dir / row["clave_almacenamiento"]).resolve()
    if settings.upload_dir.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail=error_body("archivo_no_encontrado", "No se encontró el archivo original."))
    return path, row["tipo_contenido"], row["nombre_archivo"], row["estado"]


def _ensure_medico_sees_confirmed(tier: str, estado: str) -> None:
    if tier == "medico" and estado != "confirmado":
        raise HTTPException(status_code=403, detail=error_body("sin_permiso", "No tienes acceso a este documento."))


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}/contenido", operation_id="visualizarDocumento", responses={401: {}, 403: {}, 404: {}, 500: {}})
def visualizar_documento(repositorioId: uuid.UUID, documentoId: uuid.UUID, current: CurrentAccount) -> FileResponse:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        path, content_type, filename, estado = original_file(connection, repositorioId, documentoId)
        _ensure_medico_sees_confirmed(tier, estado)
    return FileResponse(path, media_type=content_type, filename=filename, content_disposition_type="inline")


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/documentos/{{documentoId}}/archivo", operation_id="descargarArchivoOriginal", responses={401: {}, 403: {}, 404: {}, 500: {}})
def descargar_archivo_original(repositorioId: uuid.UUID, documentoId: uuid.UUID, current: CurrentAccount) -> FileResponse:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        path, content_type, filename, estado = original_file(connection, repositorioId, documentoId)
        _ensure_medico_sees_confirmed(tier, estado)
    return FileResponse(path, media_type=content_type, filename=filename)


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones", status_code=201, operation_id="solicitarVinculacion", responses={400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def solicitar_vinculacion(
    repositorioId: uuid.UUID,
    body: LinkCreateRequest,
    current: CurrentAccount,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        doctor = connection.execute(
            text("SELECT id FROM cuentas WHERE lower(correo) = :email AND tipo = 'medico'"),
            {"email": str(body.correoMedico).lower()},
        ).scalar_one_or_none()
        if doctor is None:
            raise HTTPException(status_code=400, detail=error_body("medico_no_encontrado", "No existe una cuenta de médico con ese correo."))
        duplicate = connection.execute(
            text(
                """
                SELECT 1 FROM vinculaciones
                WHERE repositorio_id = :repo AND medico_cuenta_id = :doctor
                  AND estado IN ('pendiente_aceptacion', 'vigente')
                """
            ),
            {"repo": repositorioId, "doctor": doctor},
        ).first()
        if duplicate:
            raise HTTPException(status_code=400, detail=error_body("vinculacion_duplicada", "Ya existe una vinculación vigente o pendiente con ese médico."))
        if not body.sinVencimiento and body.vigenciaDias is None:
            raise HTTPException(status_code=400, detail=error_body("vigencia_requerida", "Indica una vigencia o selecciona sin vencimiento."))
        link_id = connection.execute(
            text(
                """
                INSERT INTO vinculaciones
                    (repositorio_id, medico_cuenta_id, vigencia_dias, sin_vencimiento)
                VALUES (:repo, :doctor, :days, :forever)
                RETURNING id
                """
            ),
            {
                "repo": repositorioId,
                "doctor": doctor,
                "days": None if body.sinVencimiento else body.vigenciaDias,
                "forever": body.sinVencimiento,
            },
        ).scalar_one()
        insert_scope(connection, link_id, repositorioId, body.alcance)
        return link_row(connection, repositorioId, link_id)


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones", operation_id="listarVinculaciones", responses={401: {}, 403: {}, 404: {}, 500: {}})
def listar_vinculaciones(repositorioId: uuid.UUID, current: CurrentAccount) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        query = "SELECT id FROM vinculaciones WHERE repositorio_id = :repo"
        params: dict[str, Any] = {"repo": repositorioId}
        if tier == "medico":
            # Un médico solo ve su propia vinculación, no las de otros médicos con este repo.
            query += " AND medico_cuenta_id = :doctor"
            params["doctor"] = current["id"]
        ids = connection.execute(
            text(query + " ORDER BY solicitada_en DESC"), params
        ).scalars().all()
        return [link_row(connection, repositorioId, link_id) for link_id in ids]


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones/{{vinculacionId}}", operation_id="obtenerVinculacion", responses={401: {}, 403: {}, 404: {}, 500: {}})
def obtener_vinculacion(repositorioId: uuid.UUID, vinculacionId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        tier = require_repository_access(connection, repositorioId, current)
        link = link_row(connection, repositorioId, vinculacionId)
        if tier == "medico" and link["medico"]["id"] != str(current["id"]):
            raise HTTPException(status_code=403, detail=error_body("sin_permiso", "Esta vinculación no está dirigida a tu cuenta."))
        return link


def mutate_link_status(
    connection: Any,
    repository_id: uuid.UUID,
    link_id: uuid.UUID,
    allowed_states: tuple[str, ...],
    target_state: str,
) -> dict[str, Any]:
    updated = connection.execute(
        text(
            """
            UPDATE vinculaciones SET estado = CAST(:target AS estado_vinculacion)
            WHERE id = :id AND repositorio_id = :repo
              AND estado = ANY(CAST(:allowed AS estado_vinculacion[]))
            """
        ),
        {"id": link_id, "repo": repository_id, "target": target_state, "allowed": list(allowed_states)},
    )
    if updated.rowcount != 1:
        exists = connection.execute(
            text("SELECT 1 FROM vinculaciones WHERE id = :id AND repositorio_id = :repo"),
            {"id": link_id, "repo": repository_id},
        ).first()
        if exists is None:
            raise HTTPException(status_code=404, detail=error_body("vinculacion_no_encontrada", "No se encontró la vinculación."))
        raise HTTPException(status_code=400, detail=error_body("estado_invalido", "La operación no está permitida para el estado actual."))
    return link_row(connection, repository_id, link_id)


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones/{{vinculacionId}}/reenvio-aviso", operation_id="reenviarAvisoVinculacion", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}, 503: {}})
def reenviar_aviso_vinculacion(repositorioId: uuid.UUID, vinculacionId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        row = connection.execute(
            text(
                """
                UPDATE vinculaciones SET aviso_enviado_en = now()
                WHERE id = :id AND repositorio_id = :repo AND estado = 'pendiente_aceptacion'
                RETURNING id
                """
            ),
            {"id": vinculacionId, "repo": repositorioId},
        ).first()
        if row is None:
            raise HTTPException(status_code=400, detail=error_body("estado_invalido", "Solo se puede reenviar el aviso de una solicitud pendiente."))
        return link_row(connection, repositorioId, vinculacionId)


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones/{{vinculacionId}}/cancelacion", operation_id="cancelarVinculacion", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def cancelar_vinculacion(repositorioId: uuid.UUID, vinculacionId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        return mutate_link_status(connection, repositorioId, vinculacionId, ("pendiente_aceptacion",), "cancelada")


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/vinculaciones/{{vinculacionId}}/revocacion", operation_id="revocarVinculacion", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def revocar_vinculacion(repositorioId: uuid.UUID, vinculacionId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_operator(connection, repositorioId, current)
        return mutate_link_status(connection, repositorioId, vinculacionId, ("vigente",), "revocada")


@app.get(f"{API_PREFIX}/vinculaciones/recibidas", operation_id="listarVinculacionesRecibidas", responses={401: {}, 403: {}, 500: {}})
def listar_vinculaciones_recibidas(
    current: Annotated[dict[str, Any], Depends(require_roles("medico"))],
    estado: Literal[
        "pendiente_aceptacion", "vigente", "vencida", "revocada", "rechazada", "cancelada"
    ] | None = None,
) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        params: dict[str, Any] = {"doctor": current["id"]}
        state_filter = ""
        if estado:
            state_filter = " AND estado = :state"
            params["state"] = estado
        ids = connection.execute(
            text(
                "SELECT id FROM vinculaciones WHERE medico_cuenta_id = :doctor"
                + state_filter
                + " ORDER BY solicitada_en DESC"
            ),
            params,
        ).scalars().all()
        return [received_link_row(connection, link_id) for link_id in ids]


def decide_received_link(link_id: uuid.UUID, actor_id: uuid.UUID, target_state: str) -> dict[str, Any]:
    with engine.begin() as connection:
        link = connection.execute(
            text("SELECT medico_cuenta_id FROM vinculaciones WHERE id = :id"), {"id": link_id}
        ).mappings().first()
        if link is None:
            raise HTTPException(status_code=404, detail=error_body("vinculacion_no_encontrada", "No se encontró la vinculación."))
        if link["medico_cuenta_id"] != actor_id:
            raise HTTPException(status_code=403, detail=error_body("sin_permiso", "Esta vinculación no está dirigida a tu cuenta."))
        if target_state == "vigente":
            updated = connection.execute(
                text(
                    """
                    UPDATE vinculaciones SET
                        estado = 'vigente',
                        aceptada_en = now(),
                        vence_en = CASE
                            WHEN sin_vencimiento THEN NULL
                            ELSE now() + (vigencia_dias * interval '24 hours')
                        END
                    WHERE id = :id AND estado = 'pendiente_aceptacion'
                      AND solicitud_expira_en > now()
                    RETURNING id
                    """
                ),
                {"id": link_id},
            ).first()
        else:
            updated = connection.execute(
                text(
                    """
                    UPDATE vinculaciones SET estado = 'rechazada'
                    WHERE id = :id AND estado = 'pendiente_aceptacion'
                      AND solicitud_expira_en > now()
                    RETURNING id
                    """
                ),
                {"id": link_id},
            ).first()
        if updated is None:
            raise HTTPException(status_code=400, detail=error_body("estado_invalido", "La solicitud ya no está pendiente o venció."))
        return received_link_row(connection, link_id)


@app.post(f"{API_PREFIX}/vinculaciones/{{vinculacionId}}/aceptacion", operation_id="aceptarVinculacion", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def aceptar_vinculacion(
    vinculacionId: uuid.UUID, current: Annotated[dict[str, Any], Depends(require_roles("medico"))]
) -> dict[str, Any]:
    return decide_received_link(vinculacionId, current["id"], "vigente")


@app.post(f"{API_PREFIX}/vinculaciones/{{vinculacionId}}/rechazo", operation_id="rechazarVinculacion", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}})
def rechazar_vinculacion(
    vinculacionId: uuid.UUID, current: Annotated[dict[str, Any], Depends(require_roles("medico"))]
) -> dict[str, Any]:
    return decide_received_link(vinculacionId, current["id"], "rechazada")


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/exportacion", operation_id="exportarHistorial", responses={401: {}, 403: {}, 404: {}, 500: {}})
def exportar_historial(repositorioId: uuid.UUID, current: CurrentAccount) -> StreamingResponse:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=error_body("exportacion_no_disponible", "Instala reportlab para habilitar exportaciones.")) from exc

    with engine.connect() as connection:
        require_repository_access(connection, repositorioId, current)
        repo = repository_row(connection, repositorioId)
        rows = connection.execute(
            text(
                """
                SELECT d.id, d.nombre_archivo, d.fecha_documento, d.tipo,
                       a.clave_almacenamiento
                FROM documentos d JOIN archivos_originales a ON a.documento_id = d.id
                WHERE d.repositorio_id = :repo AND d.estado = 'confirmado'
                  AND d.eliminado_en IS NULL
                ORDER BY d.fecha_documento DESC
                """
            ),
            {"repo": repositorioId},
        ).mappings().all()
        files = []
        for row in rows:
            path = (settings.upload_dir / row["clave_almacenamiento"]).resolve()
            if not path.is_file():
                raise HTTPException(status_code=404, detail=error_body("archivo_no_encontrado", "Falta un archivo original del historial."))
            files.append((row, path.read_bytes()))

    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.drawString(50, 750, f"Historial de {repo['titular']['nombreCompleto']}")
    pdf.drawString(50, 730, f"Fecha de exportación: {now_utc().date().isoformat()}")
    y = 700
    for row, _ in files:
        pdf.drawString(
            50,
            y,
            f"{row['fecha_documento'].isoformat()} | {row['tipo']} | {row['nombre_archivo'][:90]}",
        )
        y -= 18
        if y < 50:
            pdf.showPage()
            y = 750
    pdf.save()

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("resumen.pdf", pdf_buffer.getvalue())
        for row, payload in files:
            safe_name = Path(row["nombre_archivo"]).name
            output.writestr(f"documentos/{row['id']}-{safe_name}", payload)
    archive.seek(0)
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=historial.zip"},
    )


@app.post(f"{API_PREFIX}/repositorios/{{repositorioId}}/busquedas", status_code=201, operation_id="crearBusqueda", responses={400: {}, 401: {}, 403: {}, 404: {}, 500: {}, 503: {}})
def crear_busqueda(
    repositorioId: uuid.UUID,
    body: SearchCreateRequest,
    current: CurrentAccount,
) -> dict[str, Any]:
    with engine.begin() as connection:
        require_repository_access(connection, repositorioId, current)
        actor = current["id"]
        search_id = connection.execute(
            text(
                """
                INSERT INTO busquedas (repositorio_id, realizada_por_cuenta_id, consulta)
                VALUES (:repo, :actor, :query) RETURNING id
                """
            ),
            {"repo": repositorioId, "actor": actor, "query": body.consulta},
        ).scalar_one()
        rows = connection.execute(
            text(
                """
                SELECT id, nombre_archivo, fecha_documento, tipo
                FROM documentos
                WHERE repositorio_id = :repo AND estado = 'confirmado'
                  AND eliminado_en IS NULL
                  AND (nombre_archivo ILIKE :query OR tipo::text ILIKE :query)
                ORDER BY fecha_documento DESC LIMIT 20
                """
            ),
            {"repo": repositorioId, "query": f"%{body.consulta}%"},
        ).mappings().all()
        for position, row in enumerate(rows, start=1):
            connection.execute(
                text(
                    """
                    INSERT INTO resultados_busqueda
                        (busqueda_id, documento_id, repositorio_id, posicion, puntaje)
                    VALUES (:search, :document, :repo, :position, :score)
                    """
                ),
                {
                    "search": search_id,
                    "document": row["id"],
                    "repo": repositorioId,
                    "position": position,
                    "score": 1 - position / (len(rows) + 1),
                },
            )
        summaries = [document_summary(row) for row in rows]
    result: dict[str, Any] = {
        "id": str(search_id),
        "consulta": body.consulta,
        "resultados": summaries,
    }
    result["principal"] = summaries[0] if summaries else None
    if not summaries:
        result["mensaje"] = "No encontré documentos que coincidan con su búsqueda."
    return result


def search_response(connection: Any, repository_id: uuid.UUID, search_id: uuid.UUID) -> dict[str, Any]:
    search = connection.execute(
        text(
            "SELECT id, consulta FROM busquedas WHERE id = :id AND repositorio_id = :repo"
        ),
        {"id": search_id, "repo": repository_id},
    ).mappings().first()
    if search is None:
        raise HTTPException(status_code=404, detail=error_body("busqueda_no_encontrada", "No se encontró la búsqueda."))
    rows = connection.execute(
        text(
            """
            SELECT d.id, d.nombre_archivo, d.fecha_documento, d.tipo
            FROM resultados_busqueda r JOIN documentos d ON d.id = r.documento_id
            WHERE r.busqueda_id = :search AND d.eliminado_en IS NULL
            ORDER BY r.posicion
            """
        ),
        {"search": search_id},
    ).mappings().all()
    summaries = [document_summary(row) for row in rows]
    result: dict[str, Any] = {
        "id": str(search["id"]),
        "consulta": search["consulta"],
        "resultados": summaries,
        "principal": summaries[0] if summaries else None,
    }
    if not summaries:
        result["mensaje"] = "No encontré documentos que coincidan con su búsqueda."
    return result


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/busquedas/{{busquedaId}}", operation_id="obtenerBusqueda", responses={200: {}, 401: {}, 403: {}, 404: {}, 500: {}, 503: {}})
def obtener_busqueda(repositorioId: uuid.UUID, busquedaId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        require_repository_access(connection, repositorioId, current)
        return search_response(connection, repositorioId, busquedaId)


@app.get(f"{API_PREFIX}/repositorios/{{repositorioId}}/busquedas/{{busquedaId}}/alternativas", operation_id="verOtrasCoincidencias", responses={200: {}, 400: {}, 401: {}, 403: {}, 404: {}, 500: {}, 503: {}})
def ver_alternativas(repositorioId: uuid.UUID, busquedaId: uuid.UUID, current: CurrentAccount) -> dict[str, Any]:
    with engine.connect() as connection:
        require_repository_access(connection, repositorioId, current)
        search_response(connection, repositorioId, busquedaId)
        rows = connection.execute(
            text(
                """
                SELECT d.id, d.nombre_archivo, d.fecha_documento, d.tipo
                FROM resultados_busqueda r JOIN documentos d ON d.id = r.documento_id
                WHERE r.busqueda_id = :search AND r.posicion > 1
                  AND d.eliminado_en IS NULL
                ORDER BY r.posicion
                """
            ),
            {"search": busquedaId},
        ).mappings().all()
    return {"opciones": [document_summary(row) for row in rows]}
