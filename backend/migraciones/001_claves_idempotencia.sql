-- Claves de idempotencia de subirDocumento y solicitarVinculacion (openapi_equipo.yaml, parámetro Idempotency-Key).
-- Para bases creadas antes de este cambio; las bases nuevas ya la traen en esquema_bd.sql.

CREATE TABLE IF NOT EXISTS claves_idempotencia (
    cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    operacion text NOT NULL
        CHECK (operacion IN ('subirDocumento', 'solicitarVinculacion')),
    clave uuid NOT NULL,
    huella_peticion text NOT NULL,
    respuesta_estado smallint,
    respuesta_cuerpo jsonb,
    creada_en timestamptz NOT NULL DEFAULT now(),
    expira_en timestamptz NOT NULL DEFAULT now() + interval '24 hours',
    PRIMARY KEY (cuenta_id, operacion, clave),
    CONSTRAINT ck_clave_idempotencia_expiracion CHECK (expira_en > creada_en),
    CONSTRAINT ck_clave_idempotencia_respuesta CHECK (
        (respuesta_estado IS NULL) = (respuesta_cuerpo IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS ix_claves_idempotencia_expiracion
    ON claves_idempotencia (expira_en);

COMMENT ON TABLE claves_idempotencia IS
    'Respuesta original de una creación identificada por Idempotency-Key. Se conserva 24 horas.';
COMMENT ON COLUMN claves_idempotencia.huella_peticion IS
    'sha256 de lo que define la misma petición; con la misma clave y otra huella la API responde 400.';
