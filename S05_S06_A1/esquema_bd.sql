-- RepoSalud - esquema inicial PostgreSQL
-- Fuente: diagrama_clases_equipo.puml, openapi_equipo.yaml y arquitectura_equipo.md.
-- Los DTOs HTTP no se almacenan como tablas; sus datos persistentes se mapean
-- a las entidades de dominio. Este script crea la extensión vector y tipos en un esquema
-- nuevo; ejecutar una sola vez durante la inicialización de la base.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE tipo_cuenta AS ENUM (
    'paciente',
    'cuidador',
    'medico'
);

CREATE TYPE estado_documento AS ENUM (
    'pendiente_confirmacion',
    'confirmado'
);

CREATE TYPE tipo_documento AS ENUM (
    'laboratorio',
    'informe_imagen',
    'receta',
    'otro'
);

CREATE TYPE formato_archivo AS ENUM (
    'jpg',
    'png',
    'pdf'
);

CREATE TYPE tamano_texto AS ENUM (
    'normal',
    'grande'
);

CREATE TYPE estado_vinculacion AS ENUM (
    'pendiente_aceptacion',
    'vigente',
    'vencida',
    'revocada',
    'rechazada',
    'cancelada'
);

CREATE TYPE tipo_alcance AS ENUM (
    'total',
    'rango_fechas',
    'tipos',
    'documentos'
);

CREATE TYPE tipo_token_cuenta AS ENUM (
    'verificacion_correo',
    'recuperacion_contrasena'
);

CREATE TYPE campo_metadato AS ENUM (
    'fecha',
    'tipo'
);

CREATE TABLE cuentas (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre text NOT NULL CHECK (length(btrim(nombre)) > 0),
    correo text NOT NULL CHECK (length(btrim(correo)) > 0),
    hash_contrasena text NOT NULL,
    tipo tipo_cuenta NOT NULL,
    correo_verificado_en timestamptz,
    bloqueada_desde timestamptz,
    bloqueada_hasta timestamptz,
    intentos_contrasena_fallidos integer NOT NULL DEFAULT 0
        CHECK (intentos_contrasena_fallidos BETWEEN 0 AND 5),
    creada_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_cuenta_bloqueo_15_minutos CHECK (
        (intentos_contrasena_fallidos < 5
            AND bloqueada_desde IS NULL
            AND bloqueada_hasta IS NULL)
        OR
        (intentos_contrasena_fallidos = 5
            AND bloqueada_desde IS NOT NULL
            AND bloqueada_hasta = bloqueada_desde + interval '15 minutes'
            AND bloqueada_hasta IS NOT NULL)
    )
);

-- El correo no distingue mayúsculas/minúsculas en el dominio del registro.
CREATE UNIQUE INDEX uq_cuentas_correo_ci ON cuentas (lower(correo));
CREATE INDEX ix_cuentas_nombre_ci ON cuentas (lower(nombre));

CREATE TABLE consentimientos_cuenta (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id uuid NOT NULL REFERENCES cuentas (id) ON DELETE RESTRICT,
    version_aviso_privacidad text NOT NULL,
    aviso_privacidad_aceptado boolean NOT NULL CHECK (aviso_privacidad_aceptado),
    consentimiento_datos_salud boolean NOT NULL CHECK (consentimiento_datos_salud),
    otorgado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_consentimientos_version_no_vacia
        CHECK (length(btrim(version_aviso_privacidad)) > 0)
);

CREATE INDEX ix_consentimientos_cuenta_fecha
    ON consentimientos_cuenta (cuenta_id, otorgado_en DESC);

CREATE TABLE titulares_paciente (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_completo text NOT NULL CHECK (length(btrim(nombre_completo)) > 0),
    cuenta_id uuid UNIQUE REFERENCES cuentas (id) ON DELETE RESTRICT
);

CREATE INDEX ix_titulares_nombre_ci
    ON titulares_paciente (lower(nombre_completo));

CREATE TABLE repositorios (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operador_cuenta_id uuid NOT NULL UNIQUE
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    titular_paciente_id uuid NOT NULL
        REFERENCES titulares_paciente (id) ON DELETE RESTRICT,
    titular_es_operador boolean NOT NULL,
    autorizacion_declarada_en timestamptz,
    autorizacion_declarada_por_cuenta_id uuid
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    creado_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_repositorio_declaracion_autorizacion CHECK (
        (titular_es_operador
            AND autorizacion_declarada_en IS NULL
            AND autorizacion_declarada_por_cuenta_id IS NULL)
        OR
        (NOT titular_es_operador
            AND autorizacion_declarada_en IS NOT NULL
                AND autorizacion_declarada_por_cuenta_id IS NOT NULL
                AND autorizacion_declarada_por_cuenta_id = operador_cuenta_id)
    )
);

CREATE INDEX ix_repositorios_titular
    ON repositorios (titular_paciente_id);

CREATE TABLE preferencias_accesibilidad (
    repositorio_id uuid PRIMARY KEY
        REFERENCES repositorios (id) ON DELETE CASCADE,
    tamano_texto tamano_texto NOT NULL DEFAULT 'normal'
);

CREATE TABLE documentos (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    repositorio_id uuid NOT NULL
        REFERENCES repositorios (id) ON DELETE RESTRICT,
    nombre_archivo text NOT NULL
        CHECK (length(btrim(nombre_archivo)) > 0),
    formato formato_archivo NOT NULL,
    deteccion_disponible boolean NOT NULL DEFAULT true,
    tamano_bytes integer NOT NULL
        CHECK (tamano_bytes > 0 AND tamano_bytes <= 10485760),
    hash_sha256 char(64) NOT NULL
        CHECK (hash_sha256 ~ '^[0-9A-Fa-f]{64}$'),
    estado estado_documento NOT NULL DEFAULT 'pendiente_confirmacion',
    fecha_documento date,
    tipo tipo_documento,
    sugerencia_fecha date,
    sugerencia_tipo tipo_documento,
    subido_en timestamptz NOT NULL DEFAULT now(),
    eliminado_en timestamptz,
    CONSTRAINT ck_documento_estado_metadatos CHECK (
        (estado = 'pendiente_confirmacion'
            AND fecha_documento IS NULL
            AND tipo IS NULL)
        OR
        (estado = 'confirmado'
            AND fecha_documento IS NOT NULL
            AND tipo IS NOT NULL)
    ),
    CONSTRAINT uq_documento_id_repositorio UNIQUE (id, repositorio_id)
);

CREATE INDEX ix_documentos_repositorio_fecha
    ON documentos (repositorio_id, fecha_documento DESC)
    WHERE eliminado_en IS NULL;
CREATE INDEX ix_documentos_repositorio_tipo_fecha
    ON documentos (repositorio_id, tipo, fecha_documento DESC)
    WHERE estado = 'confirmado' AND eliminado_en IS NULL;
CREATE INDEX ix_documentos_repositorio_estado
    ON documentos (repositorio_id, estado)
    WHERE eliminado_en IS NULL;
CREATE INDEX ix_documentos_nombre_archivo_ci
    ON documentos (lower(nombre_archivo));

CREATE TABLE archivos_originales (
    documento_id uuid PRIMARY KEY
        REFERENCES documentos (id) ON DELETE CASCADE,
    clave_almacenamiento text NOT NULL UNIQUE
        CHECK (length(btrim(clave_almacenamiento)) > 0),
    tipo_contenido text NOT NULL,
    metadatos_cifrado text NOT NULL,
    creado_en timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE cambios_metadatos (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id uuid NOT NULL
        REFERENCES documentos (id) ON DELETE CASCADE,
    realizado_por_cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    fecha_hora timestamptz NOT NULL DEFAULT now(),
    campo campo_metadato NOT NULL,
    valor_anterior varchar(255) NOT NULL,
    CONSTRAINT ck_cambio_valor_anterior_no_vacio
        CHECK (length(btrim(valor_anterior)) > 0)
);

CREATE INDEX ix_cambios_metadatos_documento_fecha
    ON cambios_metadatos (documento_id, fecha_hora DESC);
CREATE INDEX ix_cambios_metadatos_actor_fecha
    ON cambios_metadatos (realizado_por_cuenta_id, fecha_hora DESC);

CREATE TABLE desafios_otp (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    codigo_hash text NOT NULL,
    creado_en timestamptz NOT NULL DEFAULT now(),
    expira_en timestamptz NOT NULL,
    usado_en timestamptz,
    intentos_fallidos integer NOT NULL DEFAULT 0
        CHECK (intentos_fallidos >= 0),
    CONSTRAINT ck_desafio_otp_expiracion CHECK (expira_en > creado_en)
);

CREATE INDEX ix_desafios_otp_cuenta_expiracion
    ON desafios_otp (cuenta_id, expira_en DESC);

CREATE TABLE tokens_cuenta (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    tipo tipo_token_cuenta NOT NULL,
    token_hash text NOT NULL UNIQUE,
    creado_en timestamptz NOT NULL DEFAULT now(),
    expira_en timestamptz NOT NULL,
    usado_en timestamptz,
    CONSTRAINT ck_token_cuenta_expiracion CHECK (expira_en > creado_en),
    CONSTRAINT ck_token_recuperacion_30_minutos CHECK (
        tipo <> 'recuperacion_contrasena'
        OR expira_en = creado_en + interval '30 minutes'
    )
);

CREATE INDEX ix_tokens_cuenta_tipo_expiracion
    ON tokens_cuenta (cuenta_id, tipo, expira_en DESC);

CREATE TABLE sesiones (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    creada_en timestamptz NOT NULL DEFAULT now(),
    ultima_actividad_en timestamptz NOT NULL DEFAULT now(),
    expira_en timestamptz NOT NULL,
    revocada_en timestamptz,
    CONSTRAINT ck_sesion_expiracion CHECK (expira_en > creada_en),
    CONSTRAINT ck_sesion_ultima_actividad CHECK (ultima_actividad_en >= creada_en),
    CONSTRAINT ck_sesion_vigencia_30_dias CHECK (
        expira_en = ultima_actividad_en + interval '720 hours'
    )
);

CREATE INDEX ix_sesiones_cuenta_expiracion
    ON sesiones (cuenta_id, expira_en DESC);

CREATE TABLE vinculaciones (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    repositorio_id uuid NOT NULL
        REFERENCES repositorios (id) ON DELETE RESTRICT,
    medico_cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    estado estado_vinculacion NOT NULL DEFAULT 'pendiente_aceptacion',
    solicitada_en timestamptz NOT NULL DEFAULT now(),
    solicitud_expira_en timestamptz NOT NULL DEFAULT (now() + interval '168 hours'),
    aceptada_en timestamptz,
    vigencia_dias smallint,
    sin_vencimiento boolean NOT NULL DEFAULT false,
    vence_en timestamptz,
    aviso_enviado_en timestamptz,
    CONSTRAINT ck_vinculacion_dias CHECK (
        vigencia_dias IS NULL OR vigencia_dias BETWEEN 1 AND 365
    ),
    CONSTRAINT ck_vinculacion_vigencia CHECK (
        (sin_vencimiento AND vigencia_dias IS NULL AND vence_en IS NULL)
        OR
        (NOT sin_vencimiento
            AND vigencia_dias IS NOT NULL
            AND (
                (aceptada_en IS NULL AND vence_en IS NULL)
                OR
                (aceptada_en IS NOT NULL
                    AND vence_en = aceptada_en + (vigencia_dias * interval '24 hours'))
            ))
    ),
    CONSTRAINT ck_vinculacion_aceptacion CHECK (
        estado NOT IN ('vigente', 'revocada')
        OR aceptada_en IS NOT NULL
    ),
    CONSTRAINT ck_vinculacion_estados_sin_aceptacion CHECK (
        estado NOT IN ('pendiente_aceptacion', 'rechazada', 'cancelada')
        OR aceptada_en IS NULL
    ),
    CONSTRAINT ck_vinculacion_solicitud_expiracion CHECK (
        solicitud_expira_en = solicitada_en + interval '168 hours'
    ),
    CONSTRAINT ck_vinculacion_sin_vencimiento_estado CHECK (
        NOT sin_vencimiento OR estado <> 'vencida'
    ),
    CONSTRAINT uq_vinculacion_id_repositorio UNIQUE (id, repositorio_id)
);

CREATE INDEX ix_vinculaciones_repositorio_estado
    ON vinculaciones (repositorio_id, estado);
CREATE INDEX ix_vinculaciones_medico_estado
    ON vinculaciones (medico_cuenta_id, estado);
CREATE UNIQUE INDEX uq_vinculacion_activa_repositorio_medico
    ON vinculaciones (repositorio_id, medico_cuenta_id)
    WHERE estado IN ('pendiente_aceptacion', 'vigente');

CREATE TABLE alcances_vinculacion (
    vinculacion_id uuid PRIMARY KEY,
    repositorio_id uuid NOT NULL,
    tipo tipo_alcance NOT NULL,
    fecha_desde date,
    fecha_hasta date,
    CONSTRAINT fk_alcance_vinculacion
        FOREIGN KEY (vinculacion_id, repositorio_id)
        REFERENCES vinculaciones (id, repositorio_id) ON DELETE CASCADE,
    CONSTRAINT ck_alcance_vinculacion_configuracion CHECK (
        (tipo = 'total'
            AND fecha_desde IS NULL
            AND fecha_hasta IS NULL)
        OR
        (tipo = 'rango_fechas'
            AND fecha_desde IS NOT NULL
            AND fecha_hasta IS NOT NULL
            AND fecha_desde <= fecha_hasta)
        OR
        (tipo IN ('tipos', 'documentos')
            AND fecha_desde IS NULL
            AND fecha_hasta IS NULL)
    ),
    CONSTRAINT uq_alcance_vinculacion_repositorio
        UNIQUE (vinculacion_id, repositorio_id)
);

CREATE TABLE alcances_vinculacion_tipos (
    vinculacion_id uuid NOT NULL
        REFERENCES alcances_vinculacion (vinculacion_id) ON DELETE CASCADE,
    tipo_documento tipo_documento NOT NULL,
    PRIMARY KEY (vinculacion_id, tipo_documento)
);

CREATE TABLE vinculaciones_documentos (
    vinculacion_id uuid NOT NULL,
    documento_id uuid NOT NULL,
    repositorio_id uuid NOT NULL,
    PRIMARY KEY (vinculacion_id, documento_id),
    CONSTRAINT fk_vinculacion_documento_alcance
        FOREIGN KEY (vinculacion_id, repositorio_id)
        REFERENCES alcances_vinculacion (vinculacion_id, repositorio_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_vinculacion_documento_documento
        FOREIGN KEY (documento_id, repositorio_id)
        REFERENCES documentos (id, repositorio_id) ON DELETE RESTRICT
);

CREATE INDEX ix_vinculaciones_documentos_documento
    ON vinculaciones_documentos (documento_id);

CREATE TABLE busquedas (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    repositorio_id uuid NOT NULL
        REFERENCES repositorios (id) ON DELETE RESTRICT,
    realizada_por_cuenta_id uuid NOT NULL
        REFERENCES cuentas (id) ON DELETE RESTRICT,
    consulta varchar(500) NOT NULL
        CHECK (length(btrim(consulta)) BETWEEN 1 AND 500),
    creada_en timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_busqueda_id_repositorio UNIQUE (id, repositorio_id)
);

CREATE INDEX ix_busquedas_repositorio_fecha
    ON busquedas (repositorio_id, creada_en DESC);
CREATE INDEX ix_busquedas_actor_fecha
    ON busquedas (realizada_por_cuenta_id, creada_en DESC);

CREATE TABLE resultados_busqueda (
    busqueda_id uuid NOT NULL,
    documento_id uuid NOT NULL,
    repositorio_id uuid NOT NULL,
    posicion integer NOT NULL CHECK (posicion > 0),
    puntaje numeric(8, 7),
    PRIMARY KEY (busqueda_id, documento_id),
    CONSTRAINT uq_resultado_busqueda_posicion UNIQUE (busqueda_id, posicion),
    CONSTRAINT ck_resultado_busqueda_puntaje
        CHECK (puntaje IS NULL OR puntaje BETWEEN 0 AND 1),
    CONSTRAINT fk_resultado_busqueda_busqueda
        FOREIGN KEY (busqueda_id, repositorio_id)
        REFERENCES busquedas (id, repositorio_id) ON DELETE CASCADE,
    CONSTRAINT fk_resultado_busqueda_documento
        FOREIGN KEY (documento_id, repositorio_id)
        REFERENCES documentos (id, repositorio_id) ON DELETE RESTRICT
);

CREATE INDEX ix_resultados_busqueda_documento
    ON resultados_busqueda (documento_id);

-- Tabla auxiliar de infraestructura: texto extraído y embedding no se exponen
-- en el schema público Documento, pero la arquitectura requiere indexación
-- semántica. Se usa vector sin dimensión fija hasta seleccionar el modelo.
-- Al decidir el modelo de embeddings, fijar la dimensión y crear el índice
-- HNSW/IVFFlat correspondiente (por ejemplo vector_cosine_ops).
CREATE TABLE documentos_indice_semantico (
    documento_id uuid PRIMARY KEY
        REFERENCES documentos (id) ON DELETE CASCADE,
    texto_extraido text,
    embedding vector,
    modelo_embedding varchar(200),
    procesado_en timestamptz,
    CONSTRAINT ck_indice_modelo_embedding CHECK (
        embedding IS NULL OR modelo_embedding IS NOT NULL
    )
);

CREATE INDEX ix_documentos_indice_procesado
    ON documentos_indice_semantico (procesado_en);

COMMENT ON TABLE documentos_indice_semantico IS
    'Datos internos de búsqueda; no incluir texto extraído ni embedding en respuestas de la API.';
COMMENT ON COLUMN documentos_indice_semantico.embedding IS
    'Dimensión pendiente de seleccionar el modelo; crear índice vectorial después de fijar la dimensión.';
COMMENT ON TABLE archivos_originales IS
    'Referencia al original cifrado e inmutable; las llaves de cifrado no se guardan aquí.';

CREATE FUNCTION validar_hijo_obligatorio() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    ids uuid[] := ARRAY[]::uuid[];
    parent_id uuid;
    parent_exists boolean;
    child_exists boolean;
BEGIN
    IF TG_TABLE_NAME = TG_ARGV[0] THEN
        IF TG_OP <> 'DELETE' THEN
            ids := array_append(ids, (to_jsonb(NEW) ->> TG_ARGV[1])::uuid);
        END IF;
    ELSE
        IF TG_OP <> 'INSERT' THEN
            ids := array_append(ids, (to_jsonb(OLD) ->> TG_ARGV[3])::uuid);
        END IF;
        IF TG_OP <> 'DELETE' THEN
            ids := array_append(ids, (to_jsonb(NEW) ->> TG_ARGV[3])::uuid);
        END IF;
    END IF;

    FOREACH parent_id IN ARRAY ids LOOP
        EXECUTE format(
            'SELECT EXISTS (SELECT 1 FROM %I WHERE %I = $1)',
            TG_ARGV[0], TG_ARGV[1]
        ) INTO parent_exists USING parent_id;

        IF parent_exists THEN
            EXECUTE format(
                'SELECT EXISTS (SELECT 1 FROM %I WHERE %I = $1)',
                TG_ARGV[2], TG_ARGV[3]
            ) INTO child_exists USING parent_id;

            IF NOT child_exists THEN
                RAISE EXCEPTION 'Falta la fila obligatoria en % para % = %',
                    TG_ARGV[2], TG_ARGV[3], parent_id
                    USING ERRCODE = '23514';
            END IF;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER ct_cuenta_consentimiento_requerido
AFTER INSERT OR UPDATE ON cuentas
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'cuentas', 'id', 'consentimientos_cuenta', 'cuenta_id'
);
CREATE CONSTRAINT TRIGGER ct_consentimiento_cuenta_requerido
AFTER INSERT OR UPDATE OR DELETE ON consentimientos_cuenta
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'cuentas', 'id', 'consentimientos_cuenta', 'cuenta_id'
);

CREATE CONSTRAINT TRIGGER ct_repositorio_preferencias_requeridas
AFTER INSERT OR UPDATE ON repositorios
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'repositorios', 'id', 'preferencias_accesibilidad', 'repositorio_id'
);
CREATE CONSTRAINT TRIGGER ct_preferencias_repositorio_requeridas
AFTER INSERT OR UPDATE OR DELETE ON preferencias_accesibilidad
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'repositorios', 'id', 'preferencias_accesibilidad', 'repositorio_id'
);

CREATE CONSTRAINT TRIGGER ct_documento_original_requerido
AFTER INSERT OR UPDATE ON documentos
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'documentos', 'id', 'archivos_originales', 'documento_id'
);
CREATE CONSTRAINT TRIGGER ct_original_documento_requerido
AFTER INSERT OR UPDATE OR DELETE ON archivos_originales
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'documentos', 'id', 'archivos_originales', 'documento_id'
);

CREATE CONSTRAINT TRIGGER ct_vinculacion_alcance_requerido
AFTER INSERT OR UPDATE ON vinculaciones
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'vinculaciones', 'id', 'alcances_vinculacion', 'vinculacion_id'
);
CREATE CONSTRAINT TRIGGER ct_alcance_vinculacion_requerido
AFTER INSERT OR UPDATE OR DELETE ON alcances_vinculacion
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_hijo_obligatorio(
    'vinculaciones', 'id', 'alcances_vinculacion', 'vinculacion_id'
);

CREATE FUNCTION validar_tipo_alcance_y_elementos() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    ids uuid[] := ARRAY[]::uuid[];
    v_id uuid;
    tipo_actual tipo_alcance;
    estado_vinculacion_actual estado_vinculacion;
    cantidad_tipos integer;
    cantidad_documentos integer;
BEGIN
    IF TG_TABLE_NAME = 'alcances_vinculacion' THEN
        IF TG_OP <> 'DELETE' THEN
            ids := array_append(ids, NEW.vinculacion_id);
        END IF;
        IF TG_OP <> 'INSERT' THEN
            ids := array_append(ids, OLD.vinculacion_id);
        END IF;
    ELSE
        IF TG_OP <> 'INSERT' THEN
            ids := array_append(ids, OLD.vinculacion_id);
        END IF;
        IF TG_OP <> 'DELETE' THEN
            ids := array_append(ids, NEW.vinculacion_id);
        END IF;
    END IF;

    FOREACH v_id IN ARRAY ids LOOP
        SELECT a.tipo, v.estado
        INTO tipo_actual, estado_vinculacion_actual
        FROM alcances_vinculacion AS a
        JOIN vinculaciones AS v ON v.id = a.vinculacion_id
        WHERE a.vinculacion_id = v_id;

        IF FOUND THEN
            SELECT count(*) INTO cantidad_tipos
            FROM alcances_vinculacion_tipos
            WHERE alcances_vinculacion_tipos.vinculacion_id = v_id;
            SELECT count(*) INTO cantidad_documentos
            FROM vinculaciones_documentos
            WHERE vinculaciones_documentos.vinculacion_id = v_id;

            IF (tipo_actual = 'tipos' AND (cantidad_tipos = 0 OR cantidad_documentos <> 0))
                OR (tipo_actual = 'documentos'
                    AND (cantidad_tipos <> 0
                        OR (estado_vinculacion_actual IN ('pendiente_aceptacion', 'vigente')
                            AND cantidad_documentos = 0)))
                OR (tipo_actual NOT IN ('tipos', 'documentos')
                    AND (cantidad_tipos <> 0 OR cantidad_documentos <> 0)) THEN
                RAISE EXCEPTION 'Los elementos no corresponden al tipo del alcance %',
                    v_id USING ERRCODE = '23514';
            END IF;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER ct_alcance_elementos_validos
AFTER INSERT OR UPDATE OR DELETE ON alcances_vinculacion
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_tipo_alcance_y_elementos();
CREATE CONSTRAINT TRIGGER ct_tipos_alcance_validos
AFTER INSERT OR UPDATE OR DELETE ON alcances_vinculacion_tipos
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_tipo_alcance_y_elementos();
CREATE CONSTRAINT TRIGGER ct_documentos_alcance_validos
AFTER INSERT OR UPDATE OR DELETE ON vinculaciones_documentos
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION validar_tipo_alcance_y_elementos();

CREATE FUNCTION validar_cuenta_titular() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    tipo_actual tipo_cuenta;
BEGIN
    IF NEW.cuenta_id IS NOT NULL THEN
        SELECT tipo INTO tipo_actual FROM cuentas WHERE id = NEW.cuenta_id;
        IF tipo_actual IS DISTINCT FROM 'paciente' THEN
            RAISE EXCEPTION 'La cuenta del titular debe ser de tipo paciente'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_titular_cuenta_paciente
BEFORE INSERT OR UPDATE OF cuenta_id ON titulares_paciente
FOR EACH ROW EXECUTE FUNCTION validar_cuenta_titular();

CREATE FUNCTION validar_actualizacion_cuenta_titular() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM repositorios AS r
        WHERE r.titular_paciente_id = OLD.id
          AND (
              (r.titular_es_operador
                  AND NEW.cuenta_id IS DISTINCT FROM r.operador_cuenta_id)
              OR
              (NOT r.titular_es_operador
                  AND NEW.cuenta_id = r.operador_cuenta_id)
          )
    ) THEN
        RAISE EXCEPTION 'El cambio de cuenta contradice la titularidad del repositorio'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_titular_cuenta_coherente_con_repositorio
BEFORE UPDATE OF cuenta_id ON titulares_paciente
FOR EACH ROW EXECUTE FUNCTION validar_actualizacion_cuenta_titular();

CREATE FUNCTION validar_operador_y_titular_repositorio() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    tipo_operador tipo_cuenta;
    cuenta_titular uuid;
BEGIN
    SELECT tipo INTO tipo_operador FROM cuentas WHERE id = NEW.operador_cuenta_id;
    SELECT cuenta_id INTO cuenta_titular
    FROM titulares_paciente WHERE id = NEW.titular_paciente_id;

    IF tipo_operador NOT IN ('paciente', 'cuidador') THEN
        RAISE EXCEPTION 'Solo una cuenta paciente o cuidador puede operar un repositorio'
            USING ERRCODE = '23514';
    END IF;
    IF NEW.titular_es_operador
        AND (tipo_operador <> 'paciente' OR cuenta_titular IS DISTINCT FROM NEW.operador_cuenta_id) THEN
        RAISE EXCEPTION 'El titular-operador debe ser la cuenta paciente titular'
            USING ERRCODE = '23514';
    END IF;
    IF NOT NEW.titular_es_operador
        AND (tipo_operador = 'paciente' OR cuenta_titular = NEW.operador_cuenta_id) THEN
        RAISE EXCEPTION 'La cuenta paciente debe figurar como titular y operador'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_repositorio_roles
BEFORE INSERT OR UPDATE ON repositorios
FOR EACH ROW EXECUTE FUNCTION validar_operador_y_titular_repositorio();

CREATE FUNCTION validar_cuenta_medico_vinculacion() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    tipo_actual tipo_cuenta;
BEGIN
    SELECT tipo INTO tipo_actual FROM cuentas WHERE id = NEW.medico_cuenta_id;
    IF tipo_actual IS DISTINCT FROM 'medico' THEN
        RAISE EXCEPTION 'El destinatario de una vinculacion debe ser una cuenta medico'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_vinculacion_destinatario_medico
BEFORE INSERT OR UPDATE OF medico_cuenta_id ON vinculaciones
FOR EACH ROW EXECUTE FUNCTION validar_cuenta_medico_vinculacion();

CREATE FUNCTION validar_actor_cambio_metadatos() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    operador uuid;
BEGIN
    SELECT r.operador_cuenta_id INTO operador
    FROM documentos AS d
    JOIN repositorios AS r ON r.id = d.repositorio_id
    WHERE d.id = NEW.documento_id;

    IF operador IS DISTINCT FROM NEW.realizado_por_cuenta_id THEN
        RAISE EXCEPTION 'Solo el operador del repositorio puede corregir sus metadatos'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_cambio_metadatos_actor_autorizado
BEFORE INSERT OR UPDATE ON cambios_metadatos
FOR EACH ROW EXECUTE FUNCTION validar_actor_cambio_metadatos();

CREATE FUNCTION validar_actor_busqueda() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    operador uuid;
    tipo_actor tipo_cuenta;
BEGIN
    SELECT operador_cuenta_id INTO operador
    FROM repositorios WHERE id = NEW.repositorio_id;

    IF operador = NEW.realizada_por_cuenta_id THEN
        RETURN NEW;
    END IF;

    SELECT tipo INTO tipo_actor FROM cuentas WHERE id = NEW.realizada_por_cuenta_id;
    IF tipo_actor IS DISTINCT FROM 'medico' OR NOT EXISTS (
        SELECT 1
        FROM vinculaciones AS v
        WHERE v.repositorio_id = NEW.repositorio_id
          AND v.medico_cuenta_id = NEW.realizada_por_cuenta_id
          AND v.estado = 'vigente'
          AND (v.sin_vencimiento OR v.vence_en > now())
    ) THEN
        RAISE EXCEPTION 'El actor no tiene acceso vigente al repositorio de la búsqueda'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_busqueda_actor_autorizado
BEFORE INSERT OR UPDATE ON busquedas
FOR EACH ROW EXECUTE FUNCTION validar_actor_busqueda();

CREATE FUNCTION validar_cambio_tipo_cuenta() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.tipo IS DISTINCT FROM OLD.tipo THEN
        IF EXISTS (
            SELECT 1 FROM repositorios
            WHERE operador_cuenta_id = OLD.id
              AND ((NEW.tipo = 'medico')
                  OR (NEW.tipo = 'paciente' AND NOT titular_es_operador)
                  OR (NEW.tipo = 'cuidador' AND titular_es_operador))
        ) THEN
            RAISE EXCEPTION 'El cambio de tipo contradice el rol del operador en su repositorio'
                USING ERRCODE = '23514';
        END IF;
        IF NEW.tipo <> 'medico' AND EXISTS (
            SELECT 1 FROM vinculaciones WHERE medico_cuenta_id = OLD.id
        ) THEN
            RAISE EXCEPTION 'No se puede cambiar el tipo de una cuenta destinataria de vinculaciones'
                USING ERRCODE = '23514';
        END IF;
        IF NEW.tipo <> 'paciente' AND EXISTS (
            SELECT 1 FROM titulares_paciente WHERE cuenta_id = OLD.id
        ) THEN
            RAISE EXCEPTION 'No se puede cambiar el tipo de una cuenta titular de paciente'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_cuenta_tipo_inmutable_por_relaciones
BEFORE UPDATE OF tipo ON cuentas
FOR EACH ROW EXECUTE FUNCTION validar_cambio_tipo_cuenta();

CREATE FUNCTION impedir_edicion_archivo_original() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'El registro del archivo original es inmutable'
        USING ERRCODE = '23514';
END;
$$;

CREATE TRIGGER tr_archivo_original_inmutable
BEFORE UPDATE ON archivos_originales
FOR EACH ROW EXECUTE FUNCTION impedir_edicion_archivo_original();

CREATE FUNCTION validar_documento_activo_confirmado() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    estado_actual estado_documento;
    eliminado_actual timestamptz;
    actor_id uuid;
    tipo_actor tipo_cuenta;
BEGIN
    SELECT estado, eliminado_en INTO estado_actual, eliminado_actual
    FROM documentos WHERE id = NEW.documento_id;

    IF estado_actual IS DISTINCT FROM 'confirmado' OR eliminado_actual IS NOT NULL THEN
        RAISE EXCEPTION 'Solo se permiten documentos confirmados y no eliminados'
            USING ERRCODE = '23514';
    END IF;

    IF TG_TABLE_NAME = 'resultados_busqueda' THEN
        SELECT b.realizada_por_cuenta_id INTO actor_id
        FROM busquedas AS b
        WHERE b.id = NEW.busqueda_id;

        SELECT tipo INTO tipo_actor FROM cuentas WHERE id = actor_id;
        IF tipo_actor = 'medico' AND NOT EXISTS (
            SELECT 1
            FROM busquedas AS b
            JOIN vinculaciones AS v
              ON v.repositorio_id = b.repositorio_id
             AND v.medico_cuenta_id = b.realizada_por_cuenta_id
            JOIN alcances_vinculacion AS a ON a.vinculacion_id = v.id
            JOIN documentos AS d ON d.id = NEW.documento_id
            WHERE b.id = NEW.busqueda_id
              AND v.estado = 'vigente'
              AND (v.sin_vencimiento OR v.vence_en > now())
              AND (
                  a.tipo = 'total'
                  OR (a.tipo = 'rango_fechas'
                      AND d.fecha_documento BETWEEN a.fecha_desde AND a.fecha_hasta)
                  OR (a.tipo = 'tipos' AND EXISTS (
                      SELECT 1
                      FROM alcances_vinculacion_tipos AS t
                      WHERE t.vinculacion_id = a.vinculacion_id
                        AND t.tipo_documento = d.tipo
                  ))
                  OR (a.tipo = 'documentos' AND EXISTS (
                      SELECT 1
                      FROM vinculaciones_documentos AS vd
                      WHERE vd.vinculacion_id = a.vinculacion_id
                        AND vd.documento_id = d.id
                  ))
              )
        ) THEN
            RAISE EXCEPTION 'El resultado excede el alcance de la vinculación médica'
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_documento_seleccionado_confirmado
BEFORE INSERT OR UPDATE ON vinculaciones_documentos
FOR EACH ROW EXECUTE FUNCTION validar_documento_activo_confirmado();
CREATE TRIGGER tr_resultado_busqueda_confirmado
BEFORE INSERT OR UPDATE ON resultados_busqueda
FOR EACH ROW EXECUTE FUNCTION validar_documento_activo_confirmado();

CREATE FUNCTION validar_inmutabilidad_y_estado_documento() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.repositorio_id IS DISTINCT FROM OLD.repositorio_id
        OR NEW.nombre_archivo IS DISTINCT FROM OLD.nombre_archivo
        OR NEW.formato IS DISTINCT FROM OLD.formato
        OR NEW.tamano_bytes IS DISTINCT FROM OLD.tamano_bytes
        OR NEW.hash_sha256 IS DISTINCT FROM OLD.hash_sha256
        OR NEW.subido_en IS DISTINCT FROM OLD.subido_en THEN
        RAISE EXCEPTION 'Los datos del archivo original no pueden modificarse'
            USING ERRCODE = '23514';
    END IF;
    IF OLD.estado = 'confirmado' AND NEW.estado <> OLD.estado THEN
        RAISE EXCEPTION 'Un documento confirmado no puede volver a estar pendiente'
            USING ERRCODE = '23514';
    END IF;
    IF OLD.eliminado_en IS NOT NULL AND NEW.eliminado_en IS DISTINCT FROM OLD.eliminado_en THEN
        RAISE EXCEPTION 'La fecha de eliminación lógica no puede modificarse'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_documento_inmutabilidad_estado
BEFORE UPDATE ON documentos
FOR EACH ROW EXECUTE FUNCTION validar_inmutabilidad_y_estado_documento();

CREATE FUNCTION validar_estado_inicial_documento() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.estado <> 'pendiente_confirmacion' THEN
        RAISE EXCEPTION 'Un documento nuevo debe iniciar pendiente de confirmación'
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_documento_inicia_pendiente
BEFORE INSERT ON documentos
FOR EACH ROW EXECUTE FUNCTION validar_estado_inicial_documento();

CREATE FUNCTION limpiar_referencias_documento_eliminado() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.eliminado_en IS NULL AND NEW.eliminado_en IS NOT NULL THEN
        UPDATE vinculaciones AS v
        SET estado = CASE
            WHEN v.estado = 'pendiente_aceptacion' THEN 'cancelada'::estado_vinculacion
            ELSE 'revocada'::estado_vinculacion
        END
        FROM vinculaciones_documentos AS vd
        WHERE vd.documento_id = NEW.id
          AND vd.vinculacion_id = v.id
          AND v.estado IN ('pendiente_aceptacion', 'vigente')
          AND NOT EXISTS (
              SELECT 1
              FROM vinculaciones_documentos AS restantes
              WHERE restantes.vinculacion_id = vd.vinculacion_id
                AND restantes.documento_id <> NEW.id
          );
        DELETE FROM vinculaciones_documentos WHERE documento_id = NEW.id;
        DELETE FROM resultados_busqueda WHERE documento_id = NEW.id;
        DELETE FROM documentos_indice_semantico WHERE documento_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_documento_eliminado_limpia_referencias
AFTER UPDATE OF eliminado_en ON documentos
FOR EACH ROW EXECUTE FUNCTION limpiar_referencias_documento_eliminado();
