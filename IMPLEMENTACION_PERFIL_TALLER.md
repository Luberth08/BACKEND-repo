# Implementación: Perfil de Taller

## Resumen
Se implementó la funcionalidad completa para que los administradores de taller puedan ver y editar el perfil de sus talleres, con permisos diferenciados según el rol.

## Funcionalidad Implementada

### Permisos por Rol
- **admin_taller**: Solo puede VER la información del taller
- **super_admin_taller**: Puede VER y EDITAR la información del taller

### Campos del Perfil
- Nombre del taller
- Ubicación (coordenadas lat,lon para mostrar en mapa)
- Teléfono
- Email
- Hora de inicio
- Hora de fin
- URL web
- Puntos (calificación)
- Estado (activo/suspendido)

## Archivos Modificados

### 1. Schemas (`app/schemas/taller.py`)

**Schemas nuevos:**

#### `TallerDetailResponse`
Schema completo con todos los campos del taller para mostrar en el perfil:
```python
{
  "id": 1,
  "nombre": "Taller Mecánico ABC",
  "telefono": "70123456",
  "email": "taller@example.com",
  "ubicacion": "-17.783333,-63.182222",  # lat,lon
  "hora_inicio": "08:00:00",
  "hora_fin": "18:00:00",
  "url_web": "https://tallerabc.com",
  "puntos": 4.5,
  "estado": "activo"
}
```

#### `TallerUpdate`
Schema para actualizar información del taller con validaciones:
```python
{
  "nombre": "Nuevo Nombre",           # Opcional
  "telefono": "70987654",             # Opcional, validado
  "email": "nuevo@example.com",       # Opcional, validado
  "ubicacion": "-17.78,-63.18",       # Opcional, formato "lat,lon"
  "hora_inicio": "09:00",             # Opcional, formato "HH:MM"
  "hora_fin": "19:00",                # Opcional, formato "HH:MM"
  "url_web": "https://nuevo.com"      # Opcional
}
```

**Validaciones implementadas:**
- Ubicación: Formato "lat,lon", latitud [-90, 90], longitud [-180, 180]
- Teléfono: Solo números, entre 7 y 15 dígitos
- Email: Formato válido de email
- Horas: Formato "HH:MM" o "HH:MM:SS"
- hora_fin debe ser mayor que hora_inicio

### 2. Servicio (`app/services/taller_service.py`)

**Funciones nuevas:**

#### `get_taller_detail(db, id_taller, id_usuario)`
- Obtiene el detalle completo de un taller
- Verifica que el usuario sea admin_taller o super_admin_taller del taller
- Retorna `TallerDetailResponse`

#### `update_taller(db, id_taller, id_usuario, data)`
- Actualiza la información del taller
- Solo super_admin_taller puede editar
- Valida que el nombre no esté duplicado
- Valida que hora_fin > hora_inicio
- Convierte ubicación de "lat,lon" a Geography
- Retorna `TallerDetailResponse` actualizado

#### `_check_user_taller_role(db, id_usuario, id_taller, required_roles)`
- Función auxiliar para verificar permisos
- Verifica que el usuario tenga uno de los roles requeridos en el taller específico
- Lanza HTTPException 403 si no tiene permisos

**Funciones auxiliares:**
- `_format_time()`: Convierte time a string "HH:MM:SS"
- `_parse_time()`: Convierte string a objeto time
- `_format_ubicacion()`: Convierte Geography a "lat,lon"

### 3. Endpoints (`app/api/api_v1/endpoints/talleres.py`)

**Endpoints nuevos:**

#### `GET /talleres/{taller_id}`
- Obtiene el detalle completo de un taller
- Requiere: admin_taller o super_admin_taller del taller
- Response: `TallerDetailResponse`

#### `PUT /talleres/{taller_id}`
- Actualiza la información del taller
- Requiere: super_admin_taller del taller
- Body: `TallerUpdate`
- Response: `TallerDetailResponse`

**Endpoints existentes (sin cambios):**
- `GET /talleres/mis-talleres`: Lista talleres del usuario
- `GET /talleres/`: Lista todos los talleres (admin_sistema)
- `PUT /talleres/{taller_id}/suspender`: Suspende taller (admin_sistema)
- `PUT /talleres/{taller_id}/activar`: Activa taller (admin_sistema)

## Ejemplos de Uso

### 1. Obtener Detalle del Taller
```http
GET /api/v1/talleres/1
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "nombre": "Taller Mecánico ABC",
  "telefono": "70123456",
  "email": "taller@example.com",
  "ubicacion": "-17.783333,-63.182222",
  "hora_inicio": "08:00:00",
  "hora_fin": "18:00:00",
  "url_web": "https://tallerabc.com",
  "puntos": 4.5,
  "estado": "activo"
}
```

### 2. Actualizar Información del Taller (super_admin_taller)
```http
PUT /api/v1/talleres/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Taller Mecánico ABC - Sucursal Centro",
  "telefono": "70987654",
  "ubicacion": "-17.780000,-63.180000",
  "hora_inicio": "09:00",
  "hora_fin": "19:00"
}

Response 200:
{
  "id": 1,
  "nombre": "Taller Mecánico ABC - Sucursal Centro",
  "telefono": "70987654",
  "email": "taller@example.com",
  "ubicacion": "-17.780000,-63.180000",
  "hora_inicio": "09:00:00",
  "hora_fin": "19:00:00",
  "url_web": "https://tallerabc.com",
  "puntos": 4.5,
  "estado": "activo"
}
```

### 3. Actualizar Solo Algunos Campos
```http
PUT /api/v1/talleres/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "telefono": "71234567",
  "url_web": "https://nuevo-sitio.com"
}
```

## Validaciones y Errores

### Error 403: Sin Permisos
```json
{
  "detail": "No tiene permisos para acceder a este taller"
}
```

### Error 404: Taller No Encontrado
```json
{
  "detail": "Taller no encontrado"
}
```

### Error 400: Nombre Duplicado
```json
{
  "detail": "Ya existe otro taller con ese nombre"
}
```

### Error 400: Horario Inválido
```json
{
  "detail": "La hora de fin debe ser posterior a la hora de inicio"
}
```

### Error 422: Validación de Campos
```json
{
  "detail": [
    {
      "loc": ["body", "ubicacion"],
      "msg": "Ubicación debe estar en formato \"lat,lon\"",
      "type": "value_error"
    }
  ]
}
```

## Flujo de Trabajo en el Frontend

### Para admin_taller (solo lectura):
1. Seleccionar taller de la lista
2. Llamar `GET /talleres/{taller_id}`
3. Mostrar información en modo lectura
4. Mostrar mapa con la ubicación (usando lat,lon)

### Para super_admin_taller (edición):
1. Seleccionar taller de la lista
2. Llamar `GET /talleres/{taller_id}`
3. Mostrar información con botón "Editar"
4. Al hacer clic en "Editar":
   - Abrir modal con campos prellenados
   - Permitir editar campos
   - Para ubicación: mostrar mapa interactivo donde se pueda mover el marcador
5. Al confirmar:
   - Llamar `PUT /talleres/{taller_id}` con los datos modificados
   - Actualizar la vista con la respuesta

## Notas Técnicas

### Formato de Ubicación
- **Base de datos**: Geography (PostGIS)
- **API**: String "lat,lon" (ej: "-17.783333,-63.182222")
- **Frontend**: Puede usar librerías como Leaflet, Google Maps, etc.

### Formato de Horas
- **Base de datos**: Time
- **API Request**: String "HH:MM" o "HH:MM:SS"
- **API Response**: String "HH:MM:SS"

### Conversión de Coordenadas
El servicio maneja automáticamente la conversión entre:
- String "lat,lon" → Geography (WKT POINT)
- Geography → String "lat,lon"

## Seguridad

- Todos los endpoints requieren autenticación (Bearer token)
- Los permisos se verifican a nivel de taller específico
- Solo super_admin_taller puede editar
- admin_taller solo puede ver
- No se puede editar el estado del taller (solo admin_sistema puede suspender/activar)
- No se pueden editar los puntos (calificación) desde este endpoint
