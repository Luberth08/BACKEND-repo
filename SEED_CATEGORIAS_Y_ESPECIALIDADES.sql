-- Script para poblar categorías de incidentes, especialidades y sus relaciones
-- Ejecutar después de tener tipos de incidentes en la base de datos

-- ============================================================
-- 1. INSERTAR CATEGORÍAS DE INCIDENTES
-- ============================================================
INSERT INTO categoria_incidente (nombre, descripcion) VALUES
('Motor', 'Problemas relacionados con el motor del vehículo'),
('Sistema de Frenos', 'Problemas con el sistema de frenado'),
('Sistema Eléctrico', 'Problemas eléctricos y electrónicos'),
('Transmisión', 'Problemas con la transmisión y caja de cambios'),
('Suspensión y Dirección', 'Problemas con suspensión, amortiguadores y dirección'),
('Sistema de Combustible', 'Problemas con el sistema de combustible'),
('Sistema de Refrigeración', 'Problemas con el sistema de enfriamiento'),
('Neumáticos y Ruedas', 'Problemas con neumáticos y ruedas'),
('Escape', 'Problemas con el sistema de escape'),
('Aire Acondicionado', 'Problemas con el sistema de climatización')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================
-- 2. INSERTAR ESPECIALIDADES
-- ============================================================
INSERT INTO especialidad (nombre, descripcion) VALUES
('Mecánica General', 'Reparación y mantenimiento general de vehículos'),
('Mecánica de Motor', 'Especialista en motores y sus componentes'),
('Electricidad Automotriz', 'Sistemas eléctricos y electrónicos del vehículo'),
('Frenos y Suspensión', 'Sistemas de frenado y suspensión'),
('Transmisión', 'Cajas de cambio y sistemas de transmisión'),
('Aire Acondicionado', 'Sistemas de climatización vehicular'),
('Diagnóstico Computarizado', 'Diagnóstico con escáner y computadora'),
('Neumáticos', 'Cambio y reparación de neumáticos')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================
-- 3. RELACIONAR CATEGORÍAS CON ESPECIALIDADES
-- ============================================================
-- Motor → Mecánica General, Mecánica de Motor, Diagnóstico Computarizado
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Motor' 
  AND e.nombre IN ('Mecánica General', 'Mecánica de Motor', 'Diagnóstico Computarizado')
ON CONFLICT DO NOTHING;

-- Sistema de Frenos → Mecánica General, Frenos y Suspensión
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Sistema de Frenos' 
  AND e.nombre IN ('Mecánica General', 'Frenos y Suspensión')
ON CONFLICT DO NOTHING;

-- Sistema Eléctrico → Electricidad Automotriz, Diagnóstico Computarizado
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Sistema Eléctrico' 
  AND e.nombre IN ('Electricidad Automotriz', 'Diagnóstico Computarizado')
ON CONFLICT DO NOTHING;

-- Transmisión → Mecánica General, Transmisión
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Transmisión' 
  AND e.nombre IN ('Mecánica General', 'Transmisión')
ON CONFLICT DO NOTHING;

-- Suspensión y Dirección → Mecánica General, Frenos y Suspensión
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Suspensión y Dirección' 
  AND e.nombre IN ('Mecánica General', 'Frenos y Suspensión')
ON CONFLICT DO NOTHING;

-- Sistema de Combustible → Mecánica General, Mecánica de Motor
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Sistema de Combustible' 
  AND e.nombre IN ('Mecánica General', 'Mecánica de Motor')
ON CONFLICT DO NOTHING;

-- Sistema de Refrigeración → Mecánica General, Mecánica de Motor
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Sistema de Refrigeración' 
  AND e.nombre IN ('Mecánica General', 'Mecánica de Motor')
ON CONFLICT DO NOTHING;

-- Neumáticos y Ruedas → Neumáticos
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Neumáticos y Ruedas' 
  AND e.nombre = 'Neumáticos'
ON CONFLICT DO NOTHING;

-- Escape → Mecánica General
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Escape' 
  AND e.nombre = 'Mecánica General'
ON CONFLICT DO NOTHING;

-- Aire Acondicionado → Aire Acondicionado
INSERT INTO requiere_especialidad (id_categoria_incidente, id_especialidad)
SELECT c.id, e.id
FROM categoria_incidente c, especialidad e
WHERE c.nombre = 'Aire Acondicionado' 
  AND e.nombre = 'Aire Acondicionado'
ON CONFLICT DO NOTHING;

-- ============================================================
-- 4. ACTUALIZAR TIPOS DE INCIDENTES CON CATEGORÍAS
-- ============================================================
-- Motor
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Motor')
WHERE concepto IN ('falla_motor', 'sobrecalentamiento', 'problema_arranque');

-- Frenos
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Sistema de Frenos')
WHERE concepto = 'problema_frenos';

-- Eléctrico
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Sistema Eléctrico')
WHERE concepto IN ('falla_electrica', 'bateria_descargada', 'luz_check_engine');

-- Transmisión
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Transmisión')
WHERE concepto IN ('problema_transmision', 'falla_embrague');

-- Suspensión
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Suspensión y Dirección')
WHERE concepto IN ('problema_suspension', 'problema_direccion', 'vibracion_excesiva');

-- Combustible
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Sistema de Combustible')
WHERE concepto IN ('fuga_combustible', 'fuga_aceite');

-- Neumáticos
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Neumáticos y Ruedas')
WHERE concepto = 'neumatico_pinchado';

-- Escape
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Escape')
WHERE concepto = 'problema_escape';

-- Aire Acondicionado
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Aire Acondicionado')
WHERE concepto = 'falla_aire_acondicionado';

-- Ruido (Motor)
UPDATE tipo_incidente SET id_categoria_incidente = (SELECT id FROM categoria_incidente WHERE nombre = 'Motor')
WHERE concepto = 'ruido_anormal';

-- ============================================================
-- 5. VERIFICAR RESULTADOS
-- ============================================================
-- Ver categorías creadas
SELECT * FROM categoria_incidente ORDER BY nombre;

-- Ver especialidades creadas
SELECT * FROM especialidad ORDER BY nombre;

-- Ver relaciones categoría-especialidad
SELECT 
    ci.nombre as categoria,
    e.nombre as especialidad
FROM requiere_especialidad re
JOIN categoria_incidente ci ON re.id_categoria_incidente = ci.id
JOIN especialidad e ON re.id_especialidad = e.id
ORDER BY ci.nombre, e.nombre;

-- Ver tipos de incidentes con sus categorías
SELECT 
    ti.concepto,
    ci.nombre as categoria
FROM tipo_incidente ti
LEFT JOIN categoria_incidente ci ON ti.id_categoria_incidente = ci.id
ORDER BY ci.nombre, ti.concepto;

-- Contar especialidades por categoría
SELECT 
    ci.nombre as categoria,
    COUNT(re.id_especialidad) as num_especialidades
FROM categoria_incidente ci
LEFT JOIN requiere_especialidad re ON ci.id = re.id_categoria_incidente
GROUP BY ci.id, ci.nombre
ORDER BY ci.nombre;
