# Documentación: Sistema de Solicitud de Servicio

## Descripción General

El sistema de solicitud de servicio permite generar automáticamente solicitudes a talleres cercanos basándose en:
- Las especialidades requeridas por los tipos de incidentes del diagnóstico
- La ubicación del cliente
- La disponibilidad de técnicos con las especialidades necesarias
- Un límite de distancia configurable

## Flujo de Funcionamiento

### 1. Generación Automática de Solicitudes

Cuando el usuario presiona "Solicitar Servicio":

1. **Identificar especialidades requeridas**:
   - Se obtienen los tipos de incidentes asociados al diagnóstico
   - Se buscan las especialidades requeridas en `requiere_especialidad`
   - Las especialidades están vinculadas a categorías de incidentes

2. **Buscar talleres cercanos**:
   - Se obtiene la distancia máxima desde `configuracion_sistema` (clave: `distancia_maxima_taller_km`)
   - Se buscan talleres activos dentro del rango usando PostGIS
   - Se ordenan por distancia (más cercanos primero)

3. **Verificar disponibilidad de técnicos**:
   - Para cada taller cercano, se verifica que tenga empleados con rol "tecnico"
   - Se verifica que estos técnicos tengan al menos una de las especialidades requeridas
   - Solo se consideran talleres que cumplan este requisito

4. **Crear solicitudes automáticas**:
   - Se crean solicitudes de servicio con `sugerido_por = 'ia'`
   - Se evitan duplicados (constraint único: `id_taller + id_diagnostico`)
   - Se copia la ubicación del cliente desde `solicitud_diagnostico`

### 2. Solicitud Manual

El usuario también puede:
- Ver todos los talleres cercanos (sugeridos y otros)
- Enviar solicitud manual a cualquier taller con `sugerido_por = 'conductor'`
- Agregar un comentario opcional

## Estructura de Base de Datos

### Tabla: `solicitud_servicio`

```sql
CREATE TABLE solicitud_servicio (
    id SERIAL PRIMARY KEY,
    ubicacion GEOGRAPHY(Point, 4326),
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    comentario TEXT,
    estado estado_solicitud_servicio NOT NULL DEFAULT 'pendiente',
    fecha_aceptada TIMESTAMP,
    costo_estimado DECIMAL(10,2),
    sugerido_por sugerido_por_tipo NOT NULL,
    id_taller INT NOT NULL REFERENCES taller(id),
    id_diagnostico INT NOT NULL REFERENCES diagnostico(id),
    CONSTRAINT uq_solicitud_taller_diagnostico UNIQUE (id_taller, id_diagnostico)
);
```

### ENUMs

```sql
CREATE TYPE sugerido_por_tipo AS ENUM ('ia','conductor');
CREATE TYPE estado_solicitud_servicio AS ENUM ('pendiente','aceptada','rechazada','cancelada','expirada');
```

## Endpoints API

### 1. Generar Solicitudes Automáticas

```http
POST /api/v1/servicios/{diagnostico_id}/generar-solicitudes
Authorization: Bearer {token}
```

**Respuesta**:
```json
{
  "solicitudes_creadas": 3,
  "talleres_sugeridos": [
    {
      "id": 1,
      "nombre": "Taller Mecánico ABC",
      "distancia_km": 2.5,
      "especialidades": ["Mecánica General", "Frenos"]
    }
  ],
  "especialidades_requeridas": ["Mecánica General", "Frenos", "Suspensión"]
}
```

### 2. Listar Talleres Sugeridos y Otros

```http
GET /api/v1/servicios/{diagnostico_id}/talleres-sugeridos
Authorization: Bearer {token}
```

**Respuesta**:
```json
[
  {
    "taller": {
      "id": 1,
      "nombre": "Taller ABC",
      "telefono": "12345678",
      "email": "abc@taller.com",
      "puntos": 4.5
    },
    "distancia_km": 2.5,
    "tiene_solicitud": true,
    "solicitud_id": 10,
    "especialidades_disponibles": ["Mecánica General", "Frenos"]
  }
]
```

### 3. Solicitar Servicio Manual

```http
POST /api/v1/servicios/{diagnostico_id}/solicitar-taller
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded

id_taller=5&comentario=Necesito atención urgente
```

### 4. Listar Solicitudes de Servicio

```http
GET /api/v1/servicios/{diagnostico_id}/solicitudes
Authorization: Bearer {token}
```

### 5. Cancelar Solicitud

```http
DELETE /api/v1/servicios/{solicitud_id}
Authorization: Bearer {token}
```

## Configuración del Sistema

### Distancia Máxima

La distancia máxima para buscar talleres se configura en la tabla `configuracion_sistema`:

```sql
INSERT INTO configuracion_sistema (clave, valor, descripcion)
VALUES (
    'distancia_maxima_taller_km',
    '50',
    'Distancia máxima en kilómetros para buscar talleres cercanos al cliente'
);
```

Para cambiar el valor:
```sql
UPDATE configuracion_sistema 
SET valor = '30' 
WHERE clave = 'distancia_maxima_taller_km';
```

## Relaciones entre Tablas

```
tipo_incidente
    ↓ (requiere_especialidad)
especialidad
    ↓ (tecnico_especialidad)
empleado (con rol "tecnico")
    ↓
taller
    ↓
solicitud_servicio
```

## Archivos Creados

### Modelos
- `app/models/solicitud_servicio.py`

### CRUD
- `app/crud/crud_solicitud_servicio.py`

### Schemas
- `app/schemas/solicitud_servicio.py`

### Services
- `app/services/solicitud_servicio_service.py`

### Endpoints
- `app/api/api_v1/endpoints/servicios.py`

### Migraciones
- `MIGRACION_SOLICITUD_SERVICIO.sql`

## Pasos para Implementar

### 1. Ejecutar Migración SQL

```bash
# En Render Shell o localmente
psql $DATABASE_URL -f MIGRACION_SOLICITUD_SERVICIO.sql
```

### 2. Verificar Datos Necesarios

Asegúrate de que existan:
- Tipos de incidentes en `tipo_incidente`
- Especialidades en `especialidad`
- Relaciones en `requiere_especialidad`
- Talleres activos con ubicación
- Técnicos con especialidades en `tecnico_especialidad`

### 3. Probar Endpoints

1. Crear un diagnóstico con incidentes
2. Llamar a `/servicios/{diagnostico_id}/generar-solicitudes`
3. Verificar que se crearon solicitudes
4. Listar talleres sugeridos
5. Enviar solicitud manual a otro taller

## Consideraciones Importantes

1. **PostGIS**: El sistema usa funciones geográficas de PostGIS para calcular distancias
2. **Unicidad**: Un taller no puede recibir dos solicitudes para el mismo diagnóstico
3. **Estados**: Las solicitudes solo se pueden cancelar si están en estado "pendiente"
4. **Permisos**: Solo el dueño del diagnóstico puede crear/ver/cancelar solicitudes
5. **Especialidades**: Si no hay especialidades requeridas, no se generan solicitudes automáticas

## Próximos Pasos (Frontend)

1. Pantalla de resultado con botón "Solicitar Servicio"
2. Mostrar talleres sugeridos vs otros talleres
3. Permitir agregar comentario
4. Mostrar estado de solicitudes enviadas
5. Permitir cancelar solicitudes pendientes
