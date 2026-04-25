# Cambios: Cancelación Automática de Solicitudes

## Resumen
Cuando un taller acepta una solicitud de servicio, todas las demás solicitudes del mismo diagnóstico hacia otros talleres se cancelan automáticamente.

## Cambios Realizados

### Backend

#### 1. `app/services/servicio_service.py`
- **Función modificada**: `aceptar_solicitud_servicio()`
- **Cambio**: Agregada lógica para cancelar automáticamente todas las solicitudes pendientes del mismo diagnóstico
- **Comportamiento**:
  1. Cuando se acepta una solicitud, se obtiene el `id_diagnostico`
  2. Se buscan todas las solicitudes con el mismo `id_diagnostico` que estén en estado `pendiente`
  3. Se excluye la solicitud actual
  4. Se cambia el estado de todas las demás a `cancelada`
  5. Se registra en el log cuántas solicitudes fueron canceladas

```python
# CANCELAR TODAS LAS DEMÁS SOLICITUDES DEL MISMO DIAGNÓSTICO
id_diagnostico = solicitud.id_diagnostico

if id_diagnostico:
    result = await db.execute(
        select(SolicitudServicio).where(
            and_(
                SolicitudServicio.id_diagnostico == id_diagnostico,
                SolicitudServicio.id != id_solicitud,
                SolicitudServicio.estado == EstadoSolicitudServicio.pendiente
            )
        )
    )
    
    solicitudes_a_cancelar = result.scalars().all()
    
    for sol in solicitudes_a_cancelar:
        sol.estado = EstadoSolicitudServicio.cancelada
    
    logger.info(f"Se cancelaron {len(solicitudes_a_cancelar)} solicitudes del diagnóstico {id_diagnostico}")
```

### Frontend

#### 1. `src/app/features/taller/servicios/servicios-page.ts`
- **Cambio**: Corregido el error NG0100 (ExpressionChangedAfterItHasBeenCheckedError)
- **Solución**: Usar `setTimeout` para ejecutar las notificaciones y recarga de datos después del ciclo de detección de cambios

```typescript
this.serviciosService.aceptarSolicitud(this.solicitudIdAsignar, this.tallerId, data).subscribe({
  next: () => {
    this.closeAsignacionModal();
    setTimeout(() => {
      this.notificationService.showSuccess('Solicitud aceptada exitosamente');
      this.cargarDatosSegunTab();
    }, 0);
  },
  // ...
});
```

#### 2. `src/app/features/taller/servicios/servicios-page.html`
- **Comportamiento existente**: Los botones de "Aceptar" y "Rechazar" solo se muestran si `solicitudDetalle.estado === 'pendiente'`
- **Resultado**: Las solicitudes canceladas automáticamente no mostrarán botones de acción, solo el botón "Cerrar"

#### 3. `src/app/features/taller/servicios/servicios-page.scss`
- **Estilo existente**: Ya existe el estilo para `.estado-cancelada`
- **Apariencia**: Fondo gris claro (#f3f4f6) con texto gris oscuro (#4b5563)

## Flujo Completo

1. **Cliente solicita diagnóstico** → Se crea un diagnóstico con IA
2. **Sistema sugiere talleres** → Se crean múltiples solicitudes (una por taller) con el mismo `id_diagnostico`
3. **Taller A acepta la solicitud** → 
   - Se crea un servicio para el Taller A
   - Se asignan técnicos y vehículos
   - La solicitud del Taller A cambia a estado `aceptada`
   - **TODAS las demás solicitudes del mismo diagnóstico cambian a estado `cancelada`**
4. **Otros talleres ven sus solicitudes** → 
   - Las solicitudes aparecen en "Historial Solicitudes" con estado "cancelada"
   - No pueden aceptar ni rechazar estas solicitudes
   - Solo pueden ver el detalle

## Estados de Solicitud

- `pendiente`: Solicitud recién creada, esperando respuesta del taller
- `aceptada`: Taller aceptó la solicitud y creó un servicio
- `rechazada`: Taller rechazó explícitamente la solicitud
- `cancelada`: Solicitud cancelada automáticamente porque otro taller aceptó el mismo diagnóstico
- `expirada`: Solicitud expirada por tiempo (no implementado aún)

## Beneficios

1. **Evita duplicación de servicios**: Un diagnóstico solo puede ser atendido por un taller
2. **Claridad para talleres**: Los talleres saben inmediatamente si una solicitud ya fue atendida
3. **Mejor experiencia de usuario**: No se pueden aceptar solicitudes que ya fueron tomadas por otro taller
4. **Integridad de datos**: Garantiza que un diagnóstico no tenga múltiples servicios activos simultáneamente
