# Guía de Pruebas: Flujo Completo E2E (Desde Cero)

Esta guía documenta todos los endpoints y los JSON exactos necesarios para simular el ciclo de vida completo en la plataforma.

---

## FASE 0: Creación del Taller (Afiliación)

*Nota: Autentícate en Swagger con el token de un **Usuario Normal** que desea registrar su taller.*

### 0.1 Crear Solicitud de Afiliación de Taller
**Endpoint:** `POST /api/v1/solicitudes/afiliacion/`
**JSON Body:**
```json
{
  "nombre": "Taller Mecánico Central",
  "ubicacion": "-17.7833,-63.1821",
  "telefono": "77712345",
  "email": "contacto@tallercentral.com",
  "comentario": "Taller con especialidad en grúas y mecánica general."
}
```
*Guarda el `solicitud_id` (ej. `1`).*

### 0.2 Aprobar Solicitud (Crea el Taller Oficialmente)
*Nota: Autentícate en Swagger con un **Super Administrador del Sistema**.*
**Endpoint:** `PUT /api/v1/solicitudes/afiliacion/{solicitud_id}/estado`
**JSON Body:**
```json
{
  "estado": "aprobada",
  "comentario_revision": "Taller verificado y aprobado."
}
```
*Esto creará el Taller en la BD y le asignará el rol de `administrador_taller` al usuario que lo solicitó. Guarda el `taller_id` de la respuesta.*

---

## FASE 1: Preparación del Taller (Técnicos y Vehículos)

*Nota: Autentícate en Swagger con la cuenta del **Administrador de Taller** (el mismo de la fase 0.1).*

### 1.1 Crear un Técnico en el Taller
**Endpoint:** `POST /api/v1/talleres/{taller_id}/tecnicos/`
**(Reemplaza `{taller_id}` por el ID de tu taller)**
**JSON Body:**
```json
{
  "email": "tecnico.experto@taller.com",
  "especialidades_ids": [1, 2]
}
```
*Guarda el ID del técnico que te devuelva la respuesta (ej. `tecnico_id: 1`).*

### 1.2 Registrar un Vehículo (Ej. Grúa o Camioneta)
**Endpoint:** `POST /api/v1/talleres/{taller_id}/vehiculos/`
**JSON Body:**
```json
{
  "matricula": "1234-XYZ",
  "marca": "Toyota",
  "modelo": "Hilux",
  "anio": 2023,
  "color": "Blanco",
  "tipo": "remolque"
}
```
*Guarda el ID del vehículo que te devuelva (ej. `vehiculo_id: 1`).*

---

## FASE 2: El Cliente Pide Ayuda

*Nota: Autentícate en Swagger con el token de un **Conductor/Cliente**.*

### 2.1 Generar Solicitud de Servicio a un Taller
Supongamos que el cliente ya usó la IA y tiene un `diagnostico_id: 1`.
**Endpoint:** `POST /api/v1/servicios/{diagnostico_id}/solicitar-taller`
**(Reemplaza `{diagnostico_id}` por `1`)**

Como este endpoint usa `FormData` (por subir archivos), los campos a enviar en la interfaz de Swagger son:
- **id_taller**: `1`
- **comentario**: `"Mi auto se apagó en plena avenida, necesito grúa."`

*Guarda el ID de la solicitud devuelta (ej. `solicitud_id: 1`).*

---

## FASE 3: El Taller Acepta y Asigna

*Nota: Vuelve a la sesión del **Administrador de Taller**.*

### 3.1 Aceptar la Solicitud (Crear el Servicio)
El taller recibe la solicitud y le asigna el técnico y el vehículo creados en la Fase 1.
**Endpoint:** `POST /api/v1/taller/solicitudes/{solicitud_id}/aceptar`

**JSON Body:**
```json
{
  "id_solicitud_servicio": 1,
  "tecnicos_ids": [1],
  "vehiculos_ids": [1]
}
```
*Al ejecutar esto, se crea un **Servicio**. Guarda el `servicio_id` de la respuesta.*

---

## FASE 4: Trabajo del Técnico (Tracking)

*Nota: Obtén el token del **Técnico** (haciendo Login con el email que usaste en la fase 1.1) y usa ese token.*

### 4.1 Técnico Reporta "En Camino"
**Endpoint:** `PUT /api/v1/tecnico/servicios/{servicio_id}/actualizar-estado`
**JSON Body:**
```json
{
  "estado": "en_camino"
}
```

### 4.2 Técnico Empieza a Transmitir GPS
**Endpoint:** `POST /api/v1/tecnico/servicios/{servicio_id}/actualizar-ubicacion`
**JSON Body:**
```json
{
  "latitud": -17.7833,
  "longitud": -63.1821
}
```

### 4.3 Técnico Llega y Empieza a Atender
Manda esta misma petición dos veces, primero con `"en_lugar"`, y luego con `"en_atencion"`.
**Endpoint:** `PUT /api/v1/tecnico/servicios/{servicio_id}/actualizar-estado`
**JSON Body:**
```json
{
  "estado": "en_atencion"
}
```

---

## FASE 5: Monitoreo y Chat (Cliente)

*Nota: Vuelve a la sesión del **Cliente**.*

### 5.1 Consultar ETA y Ubicación Actual
**Endpoint:** `GET /api/v1/monitoreo/servicio/{servicio_id}/ubicacion-tecnico`

### 5.2 Ver Timeline de Estados
**Endpoint:** `GET /api/v1/monitoreo/servicio/{servicio_id}/timeline`

### 5.3 Cliente Envía Mensaje
**Endpoint:** `POST /api/v1/mensajes/servicio/{servicio_id}`
**JSON Body:**
```json
{
  "texto": "Ya veo su grúa acercándose, gracias."
}
```

---

## FASE 6: Cobro y Finalización

*Nota: Vuelve a la sesión del **Técnico**.*

### Opcion A: Cobro Digital (Stripe)
**Endpoint:** `POST /api/v1/pagos/servicio/{servicio_id}/generar`
**JSON Body:**
```json
{
  "monto_total": 250.50
}
```
*Devuelve el link de Stripe.*

### Opcion B: Cobro en Efectivo
**Endpoint:** `POST /api/v1/pagos/servicio/{servicio_id}/pago-efectivo`
**JSON Body:**
```json
{
  "monto_total": 250.50
}
```
*Esto finaliza el servicio de forma automática al registrarse el pago.*

---

## FASE 7: Verificación Final

**Endpoint:** `GET /api/v1/monitoreo/servicio/{servicio_id}`
El `estado` será `"finalizado"`.
