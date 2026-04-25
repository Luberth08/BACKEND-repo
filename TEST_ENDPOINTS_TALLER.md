# Testing: Endpoints de Gestión de Servicios para Taller

## Prerequisitos

1. Ejecutar migraciones:
```bash
cd BACKEND-repo
alembic upgrade head
```

2. Tener un usuario con rol "administrador" en un taller
3. Tener solicitudes de servicio en la base de datos

---

## Endpoints a Probar

### 1. Solicitudes Recientes
```http
GET /api/v1/taller/solicitudes/recientes
Authorization: Bearer {token}
```

**Respuesta Esperada**: Lista de solicitudes de los últimos 60 minutos
```json
[
  {
    "id": 1,
    "fecha": "2026-04-25T10:30:00",
    "estado": "pendiente",
    "sugerido_por": "ia",
    "distancia_km": 5.2,
    "comentario": null,
    "tiene_servicio": false
  }
]
```

---

### 2. Solicitudes Históricas
```http
GET /api/v1/taller/solicitudes/historico
Authorization: Bearer {token}
```

**Respuesta Esperada**: Todas las solicitudes del taller

---

### 3. Detalle de Solicitud
```http
GET /api/v1/taller/solicitudes/1/detalle
Authorization: Bearer {token}
```

**Respuesta Esperada**: Información completa
```json
{
  "id": 1,
  "ubicacion": "-17.7833,-63.1821",
  "fecha": "2026-04-25T10:30:00",
  "comentario": "Urgente",
  "estado": "pendiente",
  "sugerido_por": "ia",
  "distancia_km": 5.2,
  "diagnostico": {
    "id": 1,
    "descripcion": "Problema con frenos",
    "nivel_confianza": 0.85,
    "fecha": "2026-04-25T10:00:00"
  },
  "vehiculo_cliente": {
    "matricula": "ABC-123",
    "marca": "Toyota",
    "modelo": "Corolla",
    "anio": 2020,
    "color": "Rojo",
    "tipo": "sedan"
  },
  "evidencias": [
    {
      "id": 1,
      "url": "https://...",
      "tipo": "foto",
      "transcripcion": null
    },
    {
      "id": 2,
      "url": "https://...",
      "tipo": "audio",
      "transcripcion": "Los frenos hacen ruido..."
    }
  ],
  "descripcion_conductor": "Los frenos hacen un ruido extraño"
}
```

---

### 4. Técnicos Disponibles
```http
GET /api/v1/taller/recursos/tecnicos-disponibles
Authorization: Bearer {token}
```

**Respuesta Esperada**:
```json
[
  {
    "id": 1,
    "nombre_completo": "Juan Pérez",
    "especialidades": ["Mecánica General", "Frenos"],
    "estado": "disponible"
  }
]
```

---

### 5. Vehículos Disponibles
```http
GET /api/v1/taller/recursos/vehiculos-disponibles
Authorization: Bearer {token}
```

**Respuesta Esperada**:
```json
[
  {
    "id": 1,
    "matricula": "XYZ-789",
    "marca": "Ford",
    "modelo": "F-150",
    "tipo": "camioneta",
    "estado": "disponible"
  }
]
```

---

### 6. Aceptar Solicitud
```http
POST /api/v1/taller/solicitudes/1/aceptar
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [1, 2],
  "vehiculos_ids": [1]
}
```

**Respuesta Esperada**:
```json
{
  "id": 1,
  "fecha": "2026-04-25T11:00:00",
  "estado": "creado",
  "id_taller": 1,
  "id_solicitud_servicio": 1,
  "tecnicos_asignados": [
    {
      "id_empleado": 1,
      "nombre_completo": "Juan Pérez"
    }
  ],
  "vehiculos_asignados": [
    {
      "id_vehiculo_taller": 1,
      "matricula": "XYZ-789",
      "marca": "Ford",
      "modelo": "F-150"
    }
  ]
}
```

**Verificar**:
- Estado de solicitud cambió a "aceptada"
- Estado de técnicos cambió a "en_servicio"
- Estado de vehículos cambió a "en_servicio"

---

### 7. Rechazar Solicitud
```http
POST /api/v1/taller/solicitudes/2/rechazar
Authorization: Bearer {token}
```

**Respuesta Esperada**:
```json
{
  "message": "Solicitud rechazada exitosamente",
  "solicitud_id": 2,
  "estado": "rechazada"
}
```

---

### 8. Servicios en Proceso
```http
GET /api/v1/taller/servicios/en-proceso
Authorization: Bearer {token}
```

**Respuesta Esperada**: Lista de servicios con estado "creado" o "en_proceso"

---

### 9. Servicios Históricos
```http
GET /api/v1/taller/servicios/historico
Authorization: Bearer {token}
```

**Respuesta Esperada**: Lista de servicios con estado "completado" o "cancelado"

---

### 10. Completar Servicio
```http
POST /api/v1/taller/servicios/1/completar
Authorization: Bearer {token}
```

**Respuesta Esperada**:
```json
{
  "message": "Servicio completado exitosamente",
  "servicio_id": 1,
  "estado": "completado"
}
```

**Verificar**:
- Estado de servicio cambió a "completado"
- Estado de técnicos cambió a "disponible"
- Estado de vehículos cambió a "disponible"

---

### 11. Detalle de Servicio
```http
GET /api/v1/taller/servicios/1/detalle
Authorization: Bearer {token}
```

**Respuesta Esperada**: Información completa del servicio

---

## Casos de Error a Probar

### 1. Usuario sin permisos
```http
GET /api/v1/taller/solicitudes/recientes
Authorization: Bearer {token_sin_permisos}
```
**Esperado**: 403 Forbidden - "No tiene permisos de administrador de taller"

---

### 2. Aceptar solicitud sin técnicos
```http
POST /api/v1/taller/solicitudes/1/aceptar
{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [],
  "vehiculos_ids": [1]
}
```
**Esperado**: 400 Bad Request - "Debe asignar al menos un técnico"

---

### 3. Aceptar solicitud sin vehículos
```http
POST /api/v1/taller/solicitudes/1/aceptar
{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [1],
  "vehiculos_ids": []
}
```
**Esperado**: 400 Bad Request - "Debe asignar al menos un vehículo"

---

### 4. Aceptar solicitud ya aceptada
```http
POST /api/v1/taller/solicitudes/1/aceptar
{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [1],
  "vehiculos_ids": [1]
}
```
**Esperado**: 400 Bad Request - "Ya existe un servicio para esta solicitud"

---

### 5. Asignar técnico no disponible
```http
POST /api/v1/taller/solicitudes/1/aceptar
{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [999],
  "vehiculos_ids": [1]
}
```
**Esperado**: 400 Bad Request - "Técnico 999 no encontrado" o "no está disponible"

---

### 6. Rechazar solicitud ya aceptada
```http
POST /api/v1/taller/solicitudes/1/rechazar
```
**Esperado**: 400 Bad Request - "Solo se pueden rechazar solicitudes en estado pendiente"

---

### 7. Acceder a solicitud de otro taller
```http
GET /api/v1/taller/solicitudes/999/detalle
Authorization: Bearer {token_taller_A}
```
**Esperado**: 403 Forbidden - "La solicitud no pertenece a su taller"

---

## Flujo Completo de Prueba

### Escenario: Aceptar y Completar un Servicio

1. **Listar solicitudes recientes**
   ```
   GET /api/v1/taller/solicitudes/recientes
   → Obtener id de solicitud pendiente
   ```

2. **Ver detalle de solicitud**
   ```
   GET /api/v1/taller/solicitudes/{id}/detalle
   → Revisar información completa
   ```

3. **Obtener recursos disponibles**
   ```
   GET /api/v1/taller/recursos/tecnicos-disponibles
   GET /api/v1/taller/recursos/vehiculos-disponibles
   → Seleccionar técnicos y vehículos
   ```

4. **Aceptar solicitud**
   ```
   POST /api/v1/taller/solicitudes/{id}/aceptar
   → Crear servicio y asignar recursos
   ```

5. **Verificar servicio en proceso**
   ```
   GET /api/v1/taller/servicios/en-proceso
   → Confirmar que aparece el servicio
   ```

6. **Completar servicio**
   ```
   POST /api/v1/taller/servicios/{id}/completar
   → Finalizar servicio
   ```

7. **Verificar servicio en histórico**
   ```
   GET /api/v1/taller/servicios/historico
   → Confirmar que aparece el servicio completado
   ```

8. **Verificar recursos liberados**
   ```
   GET /api/v1/taller/recursos/tecnicos-disponibles
   GET /api/v1/taller/recursos/vehiculos-disponibles
   → Confirmar que los recursos están disponibles nuevamente
   ```

---

## Notas

- Todos los endpoints requieren autenticación con Bearer token
- El token debe pertenecer a un usuario con rol "administrador" en un taller
- Las fechas están en formato ISO 8601 con timezone UTC
- Las ubicaciones están en formato "lat,lon"
- Los estados son strings en minúsculas

---

## Herramientas Recomendadas

- **Postman**: Para pruebas manuales
- **Thunder Client** (VS Code): Para pruebas rápidas
- **pytest**: Para pruebas automatizadas (próximo paso)
