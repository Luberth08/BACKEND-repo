# Guía de Pruebas: CU-13 (Monitoreo), CU-14 (Mensajería) y CU-15 (Pagos)

Esta guía detalla el flujo paso a paso para probar los nuevos módulos implementados desde un cliente REST (Postman, Thunder Client o Swagger `/docs`).

## Prerequisitos

1. Tener el servidor corriendo (`uvicorn app.main:app --reload`).
2. Tener tokens JWT válidos para:
   - **Técnico**: Para actualizar estados, ubicación y solicitar pagos.
   - **Cliente**: Para monitorear, enviar mensajes y consultar su factura.
3. Tener un **Servicio** activo (estado `creado` o `tecnico_asignado`) asignado al técnico.

---

## 1. Flujo del Técnico: Actualización de Estado (CU-13)

El técnico debe actualizar su estado y ubicación para que el cliente pueda monitorearlo.

### 1.1 Actualizar Ubicación
El técnico envía su posición GPS en tiempo real.

```http
POST /api/v1/tecnico/servicios/{servicio_id}/actualizar-ubicacion
Authorization: Bearer {token_tecnico}
Content-Type: application/json

{
  "latitud": -17.7833,
  "longitud": -63.1821
}
```

### 1.2 Actualizar Estado (Genera Historial y Métricas)
El técnico avisa que está en camino y luego que llegó al lugar.

```http
PUT /api/v1/tecnico/servicios/{servicio_id}/actualizar-estado
Authorization: Bearer {token_tecnico}
Content-Type: application/json

{
  "estado": "en_camino"
}
```
*Repetir con estado `en_lugar` y luego `en_atencion`. El backend generará automáticamente el historial en cada paso.*

---

## 2. Flujo del Cliente: Monitoreo (CU-13)

El cliente usa la app para ver el progreso de su auxilio.

### 2.1 Ver Estado Completo y ETA
Devuelve los datos del taller, vehículo, técnico y el tiempo estimado de llegada (calculado con Haversine).

```http
GET /api/v1/monitoreo/servicio/{servicio_id}
Authorization: Bearer {token_cliente}
```

### 2.2 Consultar Timeline (Historial)
Devuelve la lista de eventos generados por el técnico.

```http
GET /api/v1/monitoreo/servicio/{servicio_id}/timeline
Authorization: Bearer {token_cliente}
```

---

## 3. Comunicación Bidireccional (CU-14)

El cliente y el taller pueden intercambiar mensajes.

### 3.1 Enviar Mensaje (Cliente o Taller)
```http
POST /api/v1/mensajes/servicio/{servicio_id}
Authorization: Bearer {token_cliente_o_taller}
Content-Type: application/json

{
  "texto": "Hola, estoy en un auto rojo en la rotonda."
}
```

### 3.2 Leer Chat
Trae todo el historial y marca como leídos los mensajes no propios.
```http
GET /api/v1/mensajes/servicio/{servicio_id}
Authorization: Bearer {token_cliente_o_taller}
```

---

## 4. Gestión de Pagos (CU-15)

Cuando el servicio está `en_atencion`, se debe proceder al cobro.

### 4.1 Generar Cobro (Técnico)
El técnico ingresa el monto total (ej. 150 Bs) para generar el link de Stripe.

```http
POST /api/v1/pagos/servicio/{servicio_id}/generar
Authorization: Bearer {token_tecnico}
Content-Type: application/json

{
  "monto_total": 150.00
}
```
**Resultado:** Devuelve un JSON con la `url_qr` (Link de Stripe) y el estado `pendiente`.

### 4.2 Consultar Factura (Cliente)
El cliente obtiene la factura para acceder al link de pago.

```http
GET /api/v1/pagos/servicio/{servicio_id}
Authorization: Bearer {token_cliente}
```

### 4.3 Alternativa: Pago en Efectivo (Técnico)
Si el cliente no quiere pagar por Stripe, el técnico cobra en efectivo. Este endpoint registra el pago y **finaliza el servicio automáticamente**.

```http
POST /api/v1/pagos/servicio/{servicio_id}/pago-efectivo
Authorization: Bearer {token_tecnico}
Content-Type: application/json

{
  "monto_total": 150.00
}
```
**Validación:**
1. Al ejecutar esto, la factura cambiará a `pagado`.
2. Si llamas a `GET /api/v1/monitoreo/servicio/{servicio_id}`, verás que el servicio ahora está en estado `finalizado`.
3. El técnico **ya no puede** seguir mandando actualizaciones de estado.
