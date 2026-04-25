# Análisis: Gestión de Servicios para Administradores de Taller

## Descripción General

Sistema para que los administradores de talleres gestionen las solicitudes de servicio entrantes, las acepten asignando recursos (técnicos y vehículos), y den seguimiento a los servicios en proceso e históricos.

## Flujo Completo

### 1. Solicitudes Recientes (Últimos 60 minutos)
```
Admin Taller → Ve solicitudes pendientes recientes
             → Click en "Ver Detalle"
             → Modal con información completa:
                 - Ubicación del cliente
                 - Fecha y hora
                 - Comentario del cliente
                 - Estado actual
                 - Quién sugirió (IA o conductor)
                 - Fotos del incidente
                 - Descripción de la IA
                 - Descripción del conductor
                 - Audio + transcripción
                 - Información del vehículo
```

### 2. Acciones Disponibles
```
ACEPTAR:
  → Seleccionar técnicos disponibles (1 o más)
  → Seleccionar vehículos disponibles (1 o más)
  → Crear servicio
  → Cambiar estado de solicitud a "aceptada"
  → Cambiar estado de técnicos a "en_servicio"
  → Cambiar estado de vehículos a "en_servicio"

RECHAZAR:
  → Cambiar estado de solicitud a "rechazada"
  → No se crea servicio

CANCELAR/DEJAR PENDIENTE:
  → Mantener estado "pendiente"
  → No se crea servicio
```

### 3. Servicios en Proceso
```
Admin Taller → Ve servicios activos (creado, en_proceso)
             → Puede ver detalles
             → Puede marcar como completado
             → Al completar:
                 - Libera técnicos (disponible)
                 - Libera vehículos (disponible)
                 - Cambia estado a "completado"
```

### 4. Histórico de Servicios
```
Admin Taller → Ve servicios completados/cancelados
             → Solo lectura
             → Información completa del servicio
```

## Estructura de Base de Datos

### Tabla: `servicio`
```sql
CREATE TABLE servicio (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estado estado_servicio NOT NULL DEFAULT 'creado',
    id_taller INT NOT NULL REFERENCES taller(id),
    id_solicitud_servicio INT UNIQUE REFERENCES solicitud_servicio(id)
);
```

**Estados**:
- `creado` - Servicio recién creado
- `en_proceso` - Servicio en ejecución
- `completado` - Servicio finalizado
- `cancelado` - Servicio cancelado

### Tabla: `servicio_tecnico`
```sql
CREATE TABLE servicio_tecnico (
    id_servicio INT NOT NULL REFERENCES servicio(id) ON DELETE CASCADE,
    id_empleado INT NOT NULL REFERENCES empleado(id) ON DELETE RESTRICT,
    PRIMARY KEY (id_servicio, id_empleado)
);
```

### Tabla: `servicio_vehiculo`
```sql
CREATE TABLE servicio_vehiculo (
    id_servicio INT NOT NULL REFERENCES servicio(id) ON DELETE CASCADE,
    id_vehiculo_taller INT NOT NULL REFERENCES vehiculo_taller(id) ON DELETE RESTRICT,
    PRIMARY KEY (id_servicio, id_vehiculo_taller)
);
```

## Relaciones

```
solicitud_servicio (1) ←→ (0..1) servicio
servicio (1) ←→ (N) servicio_tecnico ←→ (1) empleado
servicio (1) ←→ (N) servicio_vehiculo ←→ (1) vehiculo_taller
taller (1) ←→ (N) servicio
```

## Archivos Creados

### Modelos
1. `app/models/servicio.py` - Modelo Servicio con estados
2. `app/models/servicio_tecnico.py` - Tabla asociativa servicio-técnico
3. `app/models/servicio_vehiculo.py` - Tabla asociativa servicio-vehículo

### Schemas
4. `app/schemas/servicio.py` - Schemas para:
   - TecnicoDisponibleResponse
   - VehiculoTallerDisponibleResponse
   - ServicioResponse
   - ServicioCreate
   - SolicitudServicioDetalleResponse (completo para modal)
   - SolicitudServicioListResponse (resumido para lista)

### CRUDs
5. `app/crud/crud_servicio.py` - Operaciones CRUD para servicios
6. `app/crud/crud_servicio_tecnico.py` - Operaciones para asignaciones de técnicos
7. `app/crud/crud_servicio_vehiculo.py` - Operaciones para asignaciones de vehículos

### Services
8. `app/services/servicio_service.py` - Lógica de negocio:
   - `obtener_solicitudes_recientes()` - Últimos 60 min
   - `obtener_solicitudes_historicas()` - Todas las solicitudes
   - `obtener_tecnicos_disponibles()` - Técnicos no en servicio
   - `obtener_vehiculos_disponibles()` - Vehículos no en servicio
   - `aceptar_solicitud_servicio()` - Crear servicio y asignar recursos
   - `rechazar_solicitud_servicio()` - Rechazar solicitud
   - `completar_servicio()` - Finalizar y liberar recursos

## Endpoints a Crear

### Para Administradores de Taller

```
GET    /api/v1/taller/solicitudes/recientes
       → Lista solicitudes pendientes (últimos 60 min)
       → Requiere: rol "administrador" en taller

GET    /api/v1/taller/solicitudes/historico
       → Lista todas las solicitudes
       → Requiere: rol "administrador" en taller

GET    /api/v1/taller/solicitudes/{solicitud_id}/detalle
       → Detalle completo de una solicitud
       → Incluye: fotos, audio, transcripción, diagnóstico
       → Requiere: rol "administrador" en taller

GET    /api/v1/taller/recursos/tecnicos-disponibles
       → Lista técnicos disponibles del taller
       → Incluye especialidades

GET    /api/v1/taller/recursos/vehiculos-disponibles
       → Lista vehículos disponibles del taller

POST   /api/v1/taller/solicitudes/{solicitud_id}/aceptar
       → Body: { tecnicos_ids: [1,2], vehiculos_ids: [3] }
       → Crea servicio y asigna recursos
       → Cambia estados

POST   /api/v1/taller/solicitudes/{solicitud_id}/rechazar
       → Rechaza la solicitud

GET    /api/v1/taller/servicios/en-proceso
       → Lista servicios activos (creado, en_proceso)

GET    /api/v1/taller/servicios/historico
       → Lista servicios completados/cancelados

POST   /api/v1/taller/servicios/{servicio_id}/completar
       → Marca servicio como completado
       → Libera técnicos y vehículos

GET    /api/v1/taller/servicios/{servicio_id}/detalle
       → Detalle completo del servicio
```

## Lógica de Negocio

### Aceptar Solicitud
1. Validar que solicitud existe y pertenece al taller
2. Validar que está en estado "pendiente"
3. Validar que no existe servicio previo
4. Validar que se proporcionaron técnicos y vehículos
5. Validar que técnicos están disponibles
6. Validar que vehículos están disponibles
7. Crear servicio
8. Asignar técnicos (cambiar estado a "en_servicio")
9. Asignar vehículos (cambiar estado a "en_servicio")
10. Actualizar solicitud a "aceptada"

### Completar Servicio
1. Validar que servicio existe y pertenece al taller
2. Obtener técnicos asignados
3. Cambiar estado de técnicos a "disponible"
4. Obtener vehículos asignados
5. Cambiar estado de vehículos a "disponible"
6. Actualizar servicio a "completado"

### Rechazar Solicitud
1. Validar que solicitud existe y pertenece al taller
2. Validar que está en estado "pendiente"
3. Actualizar solicitud a "rechazada"

## Información Completa en Modal

Cuando el admin hace click en "Ver Detalle":

### Sección 1: Información Básica
- Fecha y hora de la solicitud
- Estado actual
- Sugerido por (IA o conductor)
- Distancia del taller al cliente
- Comentario del cliente (si existe)

### Sección 2: Ubicación
- Mapa con ubicación del cliente
- Coordenadas

### Sección 3: Vehículo del Cliente
- Matrícula
- Marca, modelo, año
- Color, tipo

### Sección 4: Diagnóstico de la IA
- Descripción del diagnóstico
- Nivel de confianza
- Fecha del diagnóstico

### Sección 5: Descripción del Conductor
- Texto ingresado por el conductor

### Sección 6: Evidencias
- **Fotos**: Galería de imágenes
- **Audio**: Reproductor con transcripción

### Sección 7: Acciones
- Botón "Aceptar" → Abre modal de asignación
- Botón "Rechazar" → Confirma rechazo
- Botón "Cerrar" → Cierra modal

## Modal de Asignación (al Aceptar)

```
┌─────────────────────────────────────────┐
│ Asignar Recursos al Servicio            │
├─────────────────────────────────────────┤
│                                         │
│ Técnicos Disponibles:                   │
│ ☐ Juan Pérez (Mecánica General)        │
│ ☐ María López (Electricidad)           │
│ ☑ Carlos Ruiz (Frenos)                 │
│                                         │
│ Vehículos Disponibles:                  │
│ ☐ ABC-123 (Grúa)                       │
│ ☑ XYZ-789 (Camioneta)                  │
│                                         │
│         [Cancelar]  [Aceptar Servicio]  │
└─────────────────────────────────────────┘
```

## Estados de Recursos

### Empleado (Técnico)
- `disponible` → Puede ser asignado
- `en_servicio` → Asignado a un servicio
- `inactivo` → No disponible

### VehiculoTaller
- `disponible` → Puede ser asignado
- `en_servicio` → Asignado a un servicio
- `en_mantenimiento` → No disponible
- `fuera_de_servicio` → No disponible

## Validaciones Importantes

1. ✅ Solo administradores del taller pueden gestionar solicitudes
2. ✅ Solo se pueden aceptar solicitudes pendientes
3. ✅ No se puede crear servicio duplicado para misma solicitud
4. ✅ Técnicos deben estar disponibles
5. ✅ Vehículos deben estar disponibles
6. ✅ Mínimo 1 técnico y 1 vehículo requeridos
7. ✅ Al completar servicio, se liberan recursos automáticamente
8. ✅ Solicitudes recientes: solo últimos 60 minutos

## Próximos Pasos

1. ✅ Crear modelos (HECHO)
2. ✅ Crear schemas (HECHO)
3. ✅ Crear CRUDs (HECHO)
4. ✅ Crear service con lógica (HECHO)
5. ⏳ Crear endpoints
6. ⏳ Crear migración de Alembic
7. ⏳ Implementar frontend (Flutter)
