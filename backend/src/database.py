from collections.abc import Iterator

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.settings import settings


engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)


def get_connection() -> Iterator[Connection]:
    with engine.connect() as connection:
        yield connection


def assert_database_ready() -> None:
    required_tables = {
        "cuentas",
        "consentimientos_cuenta",
        "repositorios",
        "titulares_paciente",
        "preferencias_accesibilidad",
        "documentos",
        "archivos_originales",
        "cambios_metadatos",
        "desafios_otp",
        "tokens_cuenta",
        "sesiones",
        "vinculaciones",
        "alcances_vinculacion",
        "alcances_vinculacion_tipos",
        "vinculaciones_documentos",
        "busquedas",
        "resultados_busqueda",
        "documentos_indice_semantico",
    }
    try:
        with engine.connect() as connection:
            existing_tables = set(
                connection.execute(
                    text(
                        "SELECT tablename FROM pg_tables "
                        "WHERE schemaname = current_schema()"
                    )
                ).scalars()
            )
            version = connection.execute(text("SELECT version()")).scalar_one()
    except OperationalError as exc:
        raise RuntimeError(
            "No fue posible conectar con PostgreSQL. Revisa DATABASE_URL."
        ) from exc

    missing_tables = required_tables - existing_tables
    if missing_tables:
        raise RuntimeError(
            "Faltan tablas del esquema RepoSalud: "
            + ", ".join(sorted(missing_tables))
            + ". Importa S05_S06_A1/esquema_bd.sql antes de iniciar la API."
        )
    if "PostgreSQL" not in version:
        raise RuntimeError("La base configurada no es PostgreSQL.")


def db_error_to_http(exc: SQLAlchemyError) -> HTTPException:
    if isinstance(exc, IntegrityError):
        return HTTPException(
            status_code=400,
            detail={
                "codigo": "datos_invalidos",
                "mensaje": "Los datos contradicen una restricción de la base de datos.",
            },
        )
    if isinstance(exc, OperationalError):
        return HTTPException(
            status_code=503,
            detail={
                "codigo": "base_no_disponible",
                "mensaje": "La base de datos no está disponible.",
            },
        )
    return HTTPException(
        status_code=500,
        detail={"codigo": "error_interno", "mensaje": "Ocurrió un error interno."},
    )


def require_database_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise db_error_to_http(exc) from exc
