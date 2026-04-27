-- Script para insertar la configuración de distancia máxima
-- Ejecutar en PostgreSQL después de crear la tabla solicitud_servicio

-- Opción 1: Si conoces el email del administrador
-- Reemplaza 'luberthgutierrez@gmail.com' con el email correcto si es diferente
WITH admin_user AS (
    SELECT u.id 
    FROM usuario u
    JOIN persona p ON u.id_persona = p.id
    WHERE p.email = 'luberthgutierrez@gmail.com'
    LIMIT 1
)
INSERT INTO configuracion_sistema (clave, valor, id_usuario)
SELECT 
    'distancia_maxima_taller_km',
    '50',
    admin_user.id
FROM admin_user
ON CONFLICT (clave) DO NOTHING;

-- Verificar que se insertó correctamente
SELECT cs.*, p.email as email_admin
FROM configuracion_sistema cs
JOIN usuario u ON cs.id_usuario = u.id
JOIN persona p ON u.id_persona = p.id
WHERE cs.clave = 'distancia_maxima_taller_km';

-- Opción 2: Si conoces el ID del usuario directamente
-- Descomenta y reemplaza 123 con el ID correcto
/*
INSERT INTO configuracion_sistema (clave, valor, id_usuario)
VALUES ('distancia_maxima_taller_km', '50', 123)
ON CONFLICT (clave) DO NOTHING;
*/

-- Opción 3: Obtener el primer usuario administrador disponible
-- Descomenta si no tienes un email específico
/*
WITH admin_user AS (
    SELECT u.id 
    FROM usuario u
    JOIN rol_usuario ru ON ru.id_usuario = u.id
    JOIN rol r ON r.id = ru.id_rol
    WHERE r.nombre = 'administrador'
    LIMIT 1
)
INSERT INTO configuracion_sistema (clave, valor, id_usuario)
SELECT 
    'distancia_maxima_taller_km',
    '50',
    admin_user.id
FROM admin_user
ON CONFLICT (clave) DO NOTHING;
*/

-- Para actualizar el valor más adelante:
-- UPDATE configuracion_sistema 
-- SET valor = '30', id_usuario = (SELECT id FROM usuario WHERE ...)
-- WHERE clave = 'distancia_maxima_taller_km';
