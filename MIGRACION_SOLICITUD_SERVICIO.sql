-- Migración para crear la tabla solicitud_servicio
-- Ejecutar en la base de datos de producción

-- Crear tipos ENUM si no existen
DO $$ BEGIN
    CREATE TYPE sugerido_por_tipo AS ENUM ('ia','conductor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_solicitud_servicio AS ENUM ('pendiente','aceptada','rechazada','cancelada','expirada');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tabla solicitud_servicio
CREATE TABLE IF NOT EXISTS solicitud_servicio (
    id SERIAL PRIMARY KEY,
    ubicacion GEOGRAPHY(Point, 4326), -- del cliente
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    comentario TEXT,
    estado estado_solicitud_servicio NOT NULL DEFAULT 'pendiente',
    fecha_aceptada TIMESTAMP,
    costo_estimado DECIMAL(10,2),
    sugerido_por sugerido_por_tipo NOT NULL,
    id_taller INT NOT NULL
        REFERENCES taller(id) ON DELETE RESTRICT,
    id_diagnostico INT NOT NULL
        REFERENCES diagnostico(id) ON DELETE RESTRICT,
    
    -- Constraints
    CONSTRAINT uq_solicitud_taller_diagnostico UNIQUE (id_taller, id_diagnostico),
    CONSTRAINT check_costo_estimado_positivo CHECK (costo_estimado >= 0)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_solicitud_servicio_taller ON solicitud_servicio(id_taller);
CREATE INDEX IF NOT EXISTS idx_solicitud_servicio_diagnostico ON solicitud_servicio(id_diagnostico);
CREATE INDEX IF NOT EXISTS idx_solicitud_servicio_estado ON solicitud_servicio(estado);
CREATE INDEX IF NOT EXISTS idx_solicitud_servicio_fecha ON solicitud_servicio(fecha DESC);

-- Insertar configuración de distancia máxima si no existe
INSERT INTO configuracion_sistema (clave, valor, descripcion)
VALUES (
    'distancia_maxima_taller_km',
    '50',
    'Distancia máxima en kilómetros para buscar talleres cercanos al cliente'
)
ON CONFLICT (clave) DO NOTHING;

COMMENT ON TABLE solicitud_servicio IS 'Solicitudes de servicio enviadas a talleres para atender diagnósticos';
COMMENT ON COLUMN solicitud_servicio.ubicacion IS 'Ubicación del cliente (copiada de solicitud_diagnostico)';
COMMENT ON COLUMN solicitud_servicio.sugerido_por IS 'Indica si la solicitud fue sugerida por IA o elegida por el conductor';
COMMENT ON COLUMN solicitud_servicio.estado IS 'Estado actual de la solicitud de servicio';
