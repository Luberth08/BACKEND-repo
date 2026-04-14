-- ============================================================
--  PLATAFORMA INTELIGENTE DE ASISTENCIA VEHICULAR
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================
-- SECCIÓN 1 — TIPOS ENUMERADOS
-- ============================================================

-- Tipo de vehículo (aplica a VEHICULO)
CREATE TYPE tipo_vehiculo AS ENUM (
    'auto',
    'camioneta',
    'moto',
    'camion',
    'microbus',
    'otro'
);

-- Estado de una solicitud de afiliación de taller
CREATE TYPE estado_solicitud_afiliacion AS ENUM (
    'pendiente',
    'aprobada',
    'rechazada'
);

CREATE TYPE estado_taller AS ENUM (
    'activo',
    'suspendido'
);

-- ============================================================
-- SECCIÓN 2 — TABLAS BASE
-- ============================================================

CREATE TABLE persona (
	id SERIAL PRIMARY KEY,
	email VARCHAR(255) NOT NULL UNIQUE,
	nombre VARCHAR(100),
	apellido_p VARCHAR(100),
	apellido_m VARCHAR(100),
	ci VARCHAR(10),
	complemento VARCHAR(2),
	telefono VARCHAR(15),
	direccion VARCHAR(255)
);

CREATE UNIQUE INDEX uq_persona_ci_complemento
    ON persona (ci, COALESCE(complemento, ''))
    WHERE ci IS NOT NULL;

-- ============================================================
-- SECCIÓN 3 — IDENTIDAD Y ACCESO
-- ============================================================

CREATE TABLE usuario (
	id SERIAL PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL UNIQUE,
	contrasena VARCHAR(255) NOT NULL,
	url_img_perfil TEXT,
	id_persona INT NOT NULL UNIQUE
		REFERENCES persona(id) ON DELETE RESTRICT
);

CREATE TABLE dispositivo_usuario (
	id SERIAL PRIMARY KEY,
	token_fcm TEXT NOT NULL,
	id_persona INT NOT NULL
		REFERENCES persona(id) ON DELETE CASCADE
);

CREATE TABLE sesion (
    id SERIAL PRIMARY KEY,
    token TEXT NOT NULL UNIQUE,
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_expira TIMESTAMPTZ NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    id_persona INT NOT NULL
		REFERENCES persona(id) ON DELETE CASCADE
);

-- ============================================================
-- SECCIÓN 5 — AFILIACIÓN Y TALLER
-- ============================================================

CREATE TABLE solicitud_afiliacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion GEOGRAPHY(Point, 4326) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(255) NOT NULL,
    comentario TEXT,
	fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	fecha_revision TIMESTAMPTZ
    estado estado_solicitud_afiliacion NOT NULL DEFAULT 'pendiente',
    id_usuario_solicita INT NOT NULL
		REFERENCES usuario(id) ON DELETE RESTRICT,
    id_usuario_revisa INT
		REFERENCES usuario(id) ON DELETE SET NULL
);

CREATE TABLE taller (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion GEOGRAPHY(Point, 4326) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hora_inicio TIME,
    hora_fin TIME,
    url_web TEXT,
    puntos DECIMAL(3,2) NOT NULL DEFAULT 0.00
		CHECK (puntos >= 0.00 AND puntos <= 5.00),
    estado estado_taller NOT NULL DEFAULT 'activo',
    id_solicitud_afiliacion INT NOT NULL UNIQUE
		REFERENCES solicitud_afiliacion(id) ON DELETE RESTRICT,
    CONSTRAINT check_horario CHECK (hora_fin > hora_inicio)
);

-- ============================================================
-- SECCIÓN 6 — ROLES Y PERMISOS
-- ============================================================

CREATE TABLE rol (
	id SERIAL PRIMARY KEY,
	nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE permiso (
    id SERIAL PRIMARY KEY,
    concepto VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE rol_usuario (
	id_usuario INT NOT NULL
		REFERENCES usuario(id) ON DELETE CASCADE,
	id_rol INT NOT NULL
		REFERENCES rol(id) ON DELETE RESTRICT,
	id_taller INT
		REFERENCES taller(id) ON DELETE CASCADE,
	PRIMARY KEY(id_usuario, id_rol)
);

-- Un usuario no puede tener el mismo rol en el mismo taller dos veces
CREATE UNIQUE INDEX uq_rol_usuario_con_taller
    ON rol_usuario (id_usuario, id_rol, id_taller)
    WHERE id_taller IS NOT NULL;

CREATE TABLE rol_permiso (
    id_rol INT NOT NULL 
		REFERENCES rol(id) ON DELETE CASCADE,
    id_permiso INT NOT NULL 
		REFERENCES permiso(id) ON DELETE CASCADE,
    PRIMARY KEY (id_rol, id_permiso)
);

-- ============================================================
-- SECCIÓN 7 — VEHÍCULOS DEL CLIENTE
-- ============================================================

CREATE TABLE vehiculo (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    anio SMALLINT NOT NULL,
    color VARCHAR(50),
    tipo tipo_vehiculo NOT NULL,
    id_persona INT NOT NULL
		REFERENCES persona(id) ON DELETE RESTRICT,
	CONSTRAINT check_anio CHECK (anio >= 1900 AND anio <= 2100)
);