# Endpoints de Servicios para Cliente Móvil

## Resumen
Nuevos endpoints agregados para que el cliente móvil pueda ver sus servicios activos e historial.

## Endpoints Creados

### 1. Obtener Servicio Actual
```
GET /api/v1/servicios/mis-servicios/actual
```

**Descripción**: Obtiene el servicio activo del cliente (estado: creado o en_proceso)

**Autenticación**: Requiere token de cliente (Persona)

**Respuesta**:
```json
{
  "id": 1,
  "fecha": "2026-04-25T10:00:00",
  "estado": "en_proceso",
  "taller": {
    "id": 28,
    "nombre": "Taller Mecánico Central",
    "telefono": "+591 12345678",
    "email": "contacto@taller.com",
    "direccion": "Av. Principal #123",
    "ubicacion": "-17.783333,-63.182222",
    "puntos": 4.5
  },
  "tecnicos_asignados": [
    {
      "id_empleado": 45,
      "nombre_completo": "Juan Pérez"
    }
  ],
  "vehiculos_asignados": [
    {
      "id_vehiculo_taller": 12,
      "matricula": "ABC-123",
      "marca": "Toyota",
      "modelo": "Hilux"
    }
  ],
  "ubicacion_cliente": "-17.783333,-63.182222",
  "diagnostico": {
    "id": 15,
    "descripcion": "Problema con el motor",
    "nivel_confianza": 0.85,
    "fecha": "2026-04-25T09:00:00"
  }
}
```

**Retorna**: `null` si no hay servicio activo

---

### 2. Obtener Historial de Servicios
```
GET /api/v1/servicios/mis-servicios/historial
```

**Descripción**: Lista todos los servicios completados o cancelados del cliente

**Autenticación**: Requiere token de cliente (Persona)

**Respuesta**:
```json
[
  {
    "id": 5,
    "fecha": "2026-04-20T14:30:00",
    "estado": "completado",
    "taller_nombre": "Taller Mecánico Central",
    "diagnostico_descripcion": "Problema con el motor"
  },
  {
    "id": 3,
    "fecha": "2026-04-15T10:00:00",
    "estado": "completado",
    "taller_nombre": "AutoService Express",
    "diagnostico_descripcion": "Falla en frenos"
  }
]
```

---

### 3. Obtener Detalle de Servicio
```
GET /api/v1/servicios/mis-servicios/{servicio_id}/detalle
```

**Descripción**: Obtiene el detalle completo de un servicio específico (activo o histórico)

**Autenticación**: Requiere token de cliente (Persona)

**Parámetros**:
- `servicio_id` (path): ID del servicio

**Respuesta**: Igual que el endpoint de servicio actual (estructura completa)

**Errores**:
- `404`: Servicio no encontrado
- `403`: El servicio no pertenece al cliente

---

## Estados de Servicio

- `creado`: Servicio recién creado, taller aceptó la solicitud
- `en_proceso`: Servicio en progreso
- `completado`: Servicio finalizado exitosamente
- `cancelado`: Servicio cancelado

## Flujo de Usuario

1. **Cliente crea diagnóstico** → Sistema sugiere talleres
2. **Cliente envía solicitudes** → Talleres reciben notificación
3. **Taller acepta solicitud** → Se crea servicio en estado "creado"
4. **Cliente consulta servicio actual** → `GET /mis-servicios/actual`
5. **Taller completa servicio** → Estado cambia a "completado"
6. **Cliente ve historial** → `GET /mis-servicios/historial`

## Seguridad

- Todos los endpoints requieren autenticación con token JWT
- Solo se pueden ver servicios propios (verificación por `id_persona`)
- No se puede modificar servicios desde el cliente (solo lectura)

## Notas de Implementación

- Las ubicaciones se devuelven en formato "lat,lon" (string)
- Los técnicos se devuelven con su nombre completo (desde `usuario.nombre`)
- El servicio actual siempre es el más reciente en estado activo
- El historial se ordena por fecha descendente (más reciente primero)
