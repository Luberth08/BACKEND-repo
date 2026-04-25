# Implementación: Gestión de Servicios para Administradores de Taller

## Estado: ✅ COMPLETADO (Backend)

## Resumen

Sistema completo para que los administradores de talleres gestionen las solicitudes de servicio entrantes, las acepten asignando recursos (técnicos y vehículos), y den seguimiento a los servicios en proceso e históricos.

---

## Archivos Creados/Modificados

### 1. Modelos (✅ Completado)

#### Nuevos Modelos:
- **`app/models/servicio.py`** - Modelo principal de servicio con estados
- **`app/models/servicio_tecnico.py`** - Tabla asociativa servicio-técnico
- **`app/models/servicio_vehiculo.py`** - Tabla asociativa servicio-vehículo

#### Modificados:
- **`app/models/solicitud_servicio.py`** - Agregado campo `distancia_km`

### 2. Schemas (✅ Completado)

**`app/schemas/servicio.py`** - 8 schemas creados:
- `TecnicoDisponibleResponse` - Técnicos disponibles con especialidades
- `VehiculoTallerDisponibleResponse` - Vehículos disponibles
- `TecnicoAsignadoResponse` - Técnicos asignados a un servicio
- `VehiculoAsignadoResponse` - Vehículos asignados a un servicio
- `ServicioResponse` - Respuesta completa de servicio
- `ServicioCreate` - Crear servicio con asignaciones
- `SolicitudServicioDetalleResponse` - Detalle completo para modal
- `SolicitudServicioListResponse` - Lista resumida de solicitudes

### 3. CRUDs (✅ Completado)

- **`app/crud/crud_servicio.py`** - CRUD para servicios
  - `get_by_taller()` - Servicios de un taller
  - `get_en_proceso()` - Servicios activos
  - `get_historicos()` - Servicios completados/cancelados
  - `get_by_solicitud()` - Servicio por solicitud
  - `update_estado()` - Actualizar estado

- **`app/crud/crud_servicio_tecnico.py`** - CRUD para asignaciones de técnicos
  - `get_by_servicio()` - Técnicos de un servicio
  - `delete_by_servicio()` - Eliminar asignaciones

- **`app/crud/crud_servicio_vehiculo.py`** - CRUD para asignaciones de vehículos
  - `get_by_servicio()` - Vehículos de un servicio
  - `delete_by_servicio()` - Eliminar asignaciones

- **`app/crud/__init__.py`** - Actualizado con exports

### 4. Services (✅ Completado)

**`app/services/servicio_service.py`** - 7 funciones de lógica de negocio:

1. **`obtener_solicitudes_recientes()`**
   - Últimos 60 minutos
   - Solo pendientes
   - Ordenadas por fecha descendente

2. **`obtener_solicitudes_historicas()`**
   - Todas las solicitudes
   - Todos los estados
   - Ordenadas por fecha descendente

3. **`obtener_tecnicos_disponibles()`**
   - Técnicos con estado "disponible"
   - Incluye especialidades
   - Filtrado por taller

4. **`obtener_vehiculos_disponibles()`**
   - Vehículos con estado "disponible"
   - Filtrado por taller

5. **`aceptar_solicitud_servicio()`**
   - Validaciones completas
   - Crea servicio
   - Asigna técnicos y vehículos
   - Cambia estados a "en_servicio"
   - Actualiza solicitud a "aceptada"

6. **`rechazar_solicitud_servicio()`**
   - Valida permisos
   - Actualiza estado a "rechazada"

7. **`completar_servicio()`**
   - Libera técnicos (disponible)
   - Libera vehículos (disponible)
   - Actualiza servicio a "completado"

**`app/services/solicitud_servicio_service.py`** - Modificado:
- Agregado cálculo y guardado de `distancia_km` en solicitudes automáticas
- Agregado cálculo y guardado de `distancia_km` en solicitudes manuales

### 5. Endpoints (✅ Completado)

**`app/api/api_v1/endpoints/taller_servicios.py`** - 11 endpoints creados:

#### Solicitudes:
1. **`GET /api/v1/taller/solicitudes/recientes`**
   - Lista solicitudes pendientes (últimos 60 min)
   - Requiere: rol "administrador" en taller

2. **`GET /api/v1/taller/solicitudes/historico`**
   - Lista todas las solicitudes
   - Requiere: rol "administrador" en taller

3. **`GET /api/v1/taller/solicitudes/{solicitud_id}/detalle`**
   - Detalle completo de una solicitud
   - Incluye: fotos, audio, transcripción, diagnóstico, vehículo
   - Requiere: rol "administrador" en taller

#### Recursos:
4. **`GET /api/v1/taller/recursos/tecnicos-disponibles`**
   - Lista técnicos disponibles del taller
   - Incluye especialidades

5. **`GET /api/v1/taller/recursos/vehiculos-disponibles`**
   - Lista vehículos disponibles del taller

#### Acciones sobre Solicitudes:
6. **`POST /api/v1/taller/solicitudes/{solicitud_id}/aceptar`**
   - Body: `{ "id_solicitud_servicio": int, "tecnicos_ids": [1,2], "vehiculos_ids": [3] }`
   - Crea servicio y asigna recursos
   - Cambia estados

7. **`POST /api/v1/taller/solicitudes/{solicitud_id}/rechazar`**
   - Rechaza la solicitud

#### Servicios:
8. **`GET /api/v1/taller/servicios/en-proceso`**
   - Lista servicios activos (creado, en_proceso)

9. **`GET /api/v1/taller/servicios/historico`**
   - Lista servicios completados/cancelados

10. **`POST /api/v1/taller/servicios/{servicio_id}/completar`**
    - Marca servicio como completado
    - Libera técnicos y vehículos

11. **`GET /api/v1/taller/servicios/{servicio_id}/detalle`**
    - Detalle completo del servicio

**`app/api/api_v1/routers.py`** - Actualizado:
- Importado `taller_servicios`
- Registrado router con tag "Taller - Gestión de Servicios"

### 6. Migraciones (✅ Completado)

#### **`alembic/versions/f8b3c45d7e21_add_servicio_tables.py`**
- Crea tipo ENUM `estadoservicio`
- Crea tabla `servicio`
- Crea tabla `servicio_tecnico`
- Crea tabla `servicio_vehiculo`
- Crea índices para optimización

#### **`alembic/versions/a9d4e56f8c32_add_distancia_km_to_solicitud_servicio.py`**
- Agrega columna `distancia_km` a `solicitud_servicio`

---

## Estructura de Base de Datos

### Tabla: `servicio`
```sql
CREATE TABLE servicio (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estado estadoservicio NOT NULL DEFAULT 'creado',
    id_taller INT NOT NULL REFERENCES taller(id) ON DELETE RESTRICT,
    id_solicitud_servicio INT UNIQUE REFERENCES solicitud_servicio(id) ON DELETE SET NULL
);
```

**Estados**: `creado`, `en_proceso`, `completado`, `cancelado`

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

---

## Flujo de Trabajo

### 1. Ver Solicitudes Recientes
```
Admin → GET /api/v1/taller/solicitudes/recientes
      → Lista de solicitudes (últimos 60 min)
      → Click en solicitud
      → GET /api/v1/taller/solicitudes/{id}/detalle
      → Modal con información completa
```

### 2. Aceptar Solicitud
```
Admin → GET /api/v1/taller/recursos/tecnicos-disponibles
      → GET /api/v1/taller/recursos/vehiculos-disponibles
      → Selecciona técnicos y vehículos
      → POST /api/v1/taller/solicitudes/{id}/aceptar
      → Servicio creado
      → Recursos asignados (estado: en_servicio)
      → Solicitud aceptada
```

### 3. Rechazar Solicitud
```
Admin → POST /api/v1/taller/solicitudes/{id}/rechazar
      → Solicitud rechazada
```

### 4. Ver Servicios en Proceso
```
Admin → GET /api/v1/taller/servicios/en-proceso
      → Lista de servicios activos
```

### 5. Completar Servicio
```
Admin → POST /api/v1/taller/servicios/{id}/completar
      → Servicio completado
      → Técnicos liberados (estado: disponible)
      → Vehículos liberados (estado: disponible)
```

---

## Validaciones Implementadas

✅ Solo administradores del taller pueden gestionar solicitudes  
✅ Solo se pueden aceptar solicitudes pendientes  
✅ No se puede crear servicio duplicado para misma solicitud  
✅ Técnicos deben estar disponibles  
✅ Vehículos deben estar disponibles  
✅ Mínimo 1 técnico y 1 vehículo requeridos  
✅ Al completar servicio, se liberan recursos automáticamente  
✅ Solicitudes recientes: solo últimos 60 minutos  
✅ Verificación de pertenencia al taller  

---

## Seguridad

- **Autenticación**: Todos los endpoints requieren autenticación
- **Autorización**: Función `verificar_admin_taller()` valida rol de administrador
- **Validación de pertenencia**: Verifica que solicitudes/servicios pertenezcan al taller
- **Validación de estados**: Solo permite transiciones válidas de estados

---

## Próximos Pasos

### Backend:
1. ✅ Ejecutar migraciones en base de datos:
   ```bash
   alembic upgrade head
   ```

2. ✅ Verificar que las relaciones funcionan correctamente

3. ✅ Probar endpoints con Postman/Thunder Client

### Frontend (Flutter):
1. ⏳ Crear pantalla de solicitudes recientes
2. ⏳ Crear modal de detalle de solicitud
3. ⏳ Crear modal de asignación de recursos
4. ⏳ Crear pantalla de servicios en proceso
5. ⏳ Crear pantalla de histórico de servicios
6. ⏳ Implementar API calls en Flutter

---

## Notas Técnicas

### Estados de Recursos

**Empleado (Técnico)**:
- `disponible` → Puede ser asignado
- `en_servicio` → Asignado a un servicio
- `inactivo` → No disponible

**VehiculoTaller**:
- `disponible` → Puede ser asignado
- `en_servicio` → Asignado a un servicio
- `en_mantenimiento` → No disponible
- `fuera_de_servicio` → No disponible

### Relaciones

```
solicitud_servicio (1) ←→ (0..1) servicio
servicio (1) ←→ (N) servicio_tecnico ←→ (1) empleado
servicio (1) ←→ (N) servicio_vehiculo ←→ (1) vehiculo_taller
taller (1) ←→ (N) servicio
```

### Información en Modal de Detalle

- Fecha y hora de la solicitud
- Estado actual
- Sugerido por (IA o conductor)
- Distancia del taller al cliente
- Comentario del cliente
- Ubicación en mapa
- Vehículo del cliente (matrícula, marca, modelo, año, color, tipo)
- Diagnóstico de la IA (descripción, nivel de confianza, fecha)
- Descripción del conductor
- Evidencias (fotos en galería, audio con reproductor y transcripción)

---

## Testing

### Endpoints a Probar:

1. **Solicitudes Recientes**: Verificar que solo muestra últimos 60 min
2. **Detalle de Solicitud**: Verificar que incluye todas las evidencias
3. **Técnicos Disponibles**: Verificar que solo muestra disponibles con especialidades
4. **Vehículos Disponibles**: Verificar que solo muestra disponibles
5. **Aceptar Solicitud**: Verificar cambios de estado y asignaciones
6. **Rechazar Solicitud**: Verificar cambio de estado
7. **Servicios en Proceso**: Verificar filtrado por estado
8. **Completar Servicio**: Verificar liberación de recursos

### Casos de Prueba:

- ✅ Admin de taller A no puede ver solicitudes de taller B
- ✅ No se puede aceptar solicitud ya aceptada
- ✅ No se puede asignar técnico no disponible
- ✅ No se puede asignar vehículo no disponible
- ✅ Requiere al menos 1 técnico y 1 vehículo
- ✅ Al completar servicio, recursos quedan disponibles

---

## Documentación de Referencia

- **Análisis Original**: `ANALISIS_GESTION_SERVICIOS_TALLER.md`
- **Modelos**: `app/models/servicio*.py`
- **Schemas**: `app/schemas/servicio.py`
- **Service Layer**: `app/services/servicio_service.py`
- **Endpoints**: `app/api/api_v1/endpoints/taller_servicios.py`

---

**Fecha de Implementación**: 2026-04-25  
**Estado**: ✅ Backend Completado - Listo para Frontend
