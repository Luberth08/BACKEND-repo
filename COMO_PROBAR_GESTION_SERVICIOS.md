# Guía de Pruebas: Gestión de Servicios de Taller

## Requisitos Previos

1. **Base de datos actualizada** con las tablas:
   - `servicio`
   - `servicio_tecnico`
   - `servicio_vehiculo`
   - Migración ejecutada: `8573982aa8bc_servicio.py`

2. **Datos de prueba**:
   - Al menos 1 taller registrado
   - Al menos 2 técnicos disponibles en el taller
   - Al menos 2 vehículos disponibles en el taller
   - Al menos 1 diagnóstico completado con solicitudes de servicio generadas

3. **Usuario de prueba**:
   - Email: `luberthgutierrez@gmail.com` (o cualquier admin de taller)
   - Rol: `administrador` o `superadministrador` en un taller

## Paso 1: Verificar Backend

### 1.1 Iniciar servidor backend
```bash
cd BACKEND-repo
uvicorn app.main:app --reload
```

### 1.2 Probar endpoints con curl o Postman

**Obtener token de autenticación:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/web/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "luberthgutierrez@gmail.com", "password": "tu_password"}'
```

**Listar solicitudes recientes:**
```bash
curl -X GET "http://localhost:8000/api/v1/taller/solicitudes/recientes?id_taller=1&minutos=60" \
  -H "Authorization: Bearer TU_TOKEN"
```

**Listar técnicos disponibles:**
```bash
curl -X GET "http://localhost:8000/api/v1/taller/recursos/tecnicos-disponibles?id_taller=1" \
  -H "Authorization: Bearer TU_TOKEN"
```

**Listar vehículos disponibles:**
```bash
curl -X GET "http://localhost:8000/api/v1/taller/recursos/vehiculos-disponibles?id_taller=1" \
  -H "Authorization: Bearer TU_TOKEN"
```

## Paso 2: Verificar Frontend

### 2.1 Iniciar servidor frontend
```bash
cd FRONTEND-repo
npm start
```

### 2.2 Acceder a la aplicación
1. Abrir navegador en `http://localhost:4200`
2. Iniciar sesión con usuario administrador de taller
3. Navegar a tab "Gestión de Taller"
4. Seleccionar taller en el selector
5. Click en "Gestión de Servicios" en el sidebar

## Paso 3: Pruebas Funcionales

### 3.1 Ver Solicitudes Recientes
- [ ] Se muestra la tabla con solicitudes de los últimos 60 minutos
- [ ] Columnas: Fecha, Estado, Sugerido por, Distancia, Comentario, Acciones
- [ ] Estados tienen colores distintivos
- [ ] Botón "Ver Detalle" funciona

### 3.2 Ver Detalle de Solicitud
- [ ] Modal se abre correctamente
- [ ] Se muestra información básica (fecha, estado, sugerido por, distancia)
- [ ] Se muestra comentario del cliente (si existe)
- [ ] Botón "Ver en Mapa" funciona
- [ ] Se muestra información del vehículo del cliente
- [ ] Se muestra diagnóstico de la IA con nivel de confianza
- [ ] Se muestra descripción del conductor
- [ ] Se muestran fotos de evidencias en galería
- [ ] Se muestra reproductor de audio
- [ ] Se muestra transcripción del audio
- [ ] Botones de acción visibles (Aceptar, Rechazar, Cerrar)

### 3.3 Ver Mapa
- [ ] Modal de mapa se abre
- [ ] Mapa de OpenStreetMap se carga correctamente
- [ ] Marcador en la ubicación correcta
- [ ] Zoom apropiado (15)

### 3.4 Aceptar Solicitud
1. Click en "Aceptar" en modal de detalle
2. [ ] Modal de asignación se abre
3. [ ] Se muestra lista de técnicos disponibles con especialidades
4. [ ] Se muestra lista de vehículos disponibles
5. [ ] Checkboxes funcionan correctamente
6. Seleccionar al menos 1 técnico
7. Seleccionar al menos 1 vehículo
8. Click en "Aceptar Servicio"
9. [ ] Notificación de éxito
10. [ ] Modal se cierra
11. [ ] Solicitud desaparece de "Recientes" (ya no está pendiente)
12. [ ] Servicio aparece en "Servicios en Proceso"

### 3.5 Validaciones de Aceptar
- [ ] Error si no se selecciona ningún técnico
- [ ] Error si no se selecciona ningún vehículo
- [ ] Error si técnico no está disponible (backend)
- [ ] Error si vehículo no está disponible (backend)

### 3.6 Rechazar Solicitud
1. Click en "Rechazar" en modal de detalle
2. [ ] Modal de confirmación se abre
3. Click en "Rechazar"
4. [ ] Notificación de éxito
5. [ ] Modal se cierra
6. [ ] Solicitud cambia a estado "rechazada"

### 3.7 Ver Historial de Solicitudes
- [ ] Tab "Historial Solicitudes" funciona
- [ ] Se muestran todas las solicitudes (no solo últimos 60 min)
- [ ] Columna "Tiene Servicio" muestra Sí/No correctamente
- [ ] Se pueden ver detalles de solicitudes históricas

### 3.8 Ver Servicios en Proceso
- [ ] Tab "Servicios en Proceso" funciona
- [ ] Se muestran servicios con estado "creado" o "en_proceso"
- [ ] Se muestran técnicos asignados
- [ ] Se muestran vehículos asignados
- [ ] Botón "Completar" visible

### 3.9 Completar Servicio
1. Click en "Completar" en servicio en proceso
2. [ ] Modal de confirmación se abre
3. [ ] Mensaje indica que recursos quedarán disponibles
4. Click en "Completar"
5. [ ] Notificación de éxito
6. [ ] Modal se cierra
7. [ ] Servicio desaparece de "En Proceso"
8. [ ] Servicio aparece en "Historial Servicios"
9. Verificar en tab "Vehículos" del taller:
   - [ ] Vehículos asignados vuelven a estado "disponible"
10. Verificar en tab "Técnicos" del taller:
    - [ ] Técnicos asignados vuelven a estado "disponible"

### 3.10 Ver Historial de Servicios
- [ ] Tab "Historial Servicios" funciona
- [ ] Se muestran servicios completados/cancelados
- [ ] Se muestran técnicos que estuvieron asignados
- [ ] Se muestran vehículos que estuvieron asignados
- [ ] No hay botón "Completar" (solo lectura)

## Paso 4: Pruebas de Seguridad

### 4.1 Permisos
- [ ] Usuario sin rol de administrador NO puede acceder
- [ ] Usuario administrador de taller A NO puede ver solicitudes de taller B
- [ ] Usuario administrador de taller A NO puede aceptar solicitudes de taller B

### 4.2 Estados
- [ ] Solo se pueden aceptar solicitudes en estado "pendiente"
- [ ] Solo se pueden rechazar solicitudes en estado "pendiente"
- [ ] No se puede crear servicio duplicado para misma solicitud

## Paso 5: Pruebas de UI/UX

### 5.1 Responsividad
- [ ] Tablas se ven bien en pantallas grandes
- [ ] Modales se adaptan al tamaño de pantalla
- [ ] Scroll funciona correctamente en modales largos

### 5.2 Loading States
- [ ] Spinner se muestra mientras carga datos
- [ ] Spinner desaparece cuando datos están listos

### 5.3 Estados Visuales
- [ ] Estado "pendiente" - amarillo
- [ ] Estado "aceptada" - verde
- [ ] Estado "rechazada" - rojo
- [ ] Estado "cancelada" - gris
- [ ] Estado "creado" - azul claro
- [ ] Estado "en_proceso" - azul oscuro
- [ ] Estado "completado" - verde

### 5.4 Interacciones
- [ ] Hover en filas de tabla cambia color de fondo
- [ ] Botones tienen efecto hover
- [ ] Checkboxes se marcan/desmarcan correctamente
- [ ] Modales se cierran al hacer click en X
- [ ] Modales se cierran al hacer click en "Cancelar"
- [ ] Modales NO se cierran al hacer click en el contenido

## Paso 6: Pruebas de Integración

### 6.1 Flujo Completo: Cliente → Taller
1. **Como cliente (mobile)**:
   - Crear diagnóstico con fotos y audio
   - Generar solicitudes automáticas
   - Agregar comentario a solicitud

2. **Como administrador de taller (web)**:
   - Ver solicitud en "Recientes"
   - Ver detalle completo
   - Ver ubicación en mapa
   - Ver fotos y audio
   - Aceptar solicitud asignando recursos
   - Ver servicio en "En Proceso"
   - Completar servicio

3. **Verificar**:
   - [ ] Recursos quedan disponibles
   - [ ] Servicio en historial
   - [ ] Solicitud marcada como "aceptada"

### 6.2 Flujo: Múltiples Talleres
1. Iniciar sesión con superadministrador que tiene 2+ talleres
2. [ ] Selector de taller muestra todos los talleres
3. Seleccionar taller A
4. [ ] Se muestran solicitudes de taller A
5. Seleccionar taller B
6. [ ] Se muestran solicitudes de taller B
7. [ ] No se mezclan datos entre talleres

## Paso 7: Pruebas de Rendimiento

### 7.1 Carga de Datos
- [ ] Lista de 50+ solicitudes carga en < 2 segundos
- [ ] Detalle de solicitud carga en < 1 segundo
- [ ] Lista de técnicos disponibles carga en < 1 segundo
- [ ] Lista de vehículos disponibles carga en < 1 segundo

### 7.2 Operaciones
- [ ] Aceptar solicitud completa en < 2 segundos
- [ ] Rechazar solicitud completa en < 1 segundo
- [ ] Completar servicio completa en < 2 segundos

## Problemas Comunes y Soluciones

### Error: "No hay solicitudes recientes"
- **Causa**: No hay solicitudes en los últimos 60 minutos
- **Solución**: Crear nuevas solicitudes desde la app móvil o cambiar a tab "Historial"

### Error: "No hay técnicos disponibles"
- **Causa**: Todos los técnicos están en servicio o inactivos
- **Solución**: Completar servicios activos o crear nuevos técnicos

### Error: "No hay vehículos disponibles"
- **Causa**: Todos los vehículos están en servicio o inactivos
- **Solución**: Completar servicios activos o crear nuevos vehículos

### Error: "La solicitud no pertenece a este taller"
- **Causa**: Intentando acceder a solicitud de otro taller
- **Solución**: Verificar que el taller seleccionado es el correcto

### Error: "Solo se pueden aceptar solicitudes en estado pendiente"
- **Causa**: Solicitud ya fue aceptada o rechazada
- **Solución**: Verificar estado de la solicitud en historial

### Mapa no se muestra
- **Causa**: Problema con OpenStreetMap o ubicación inválida
- **Solución**: Verificar que ubicación tiene formato "lat,lon" válido

### Audio no se reproduce
- **Causa**: Formato de audio no soportado o URL inválida
- **Solución**: Verificar que audio está en formato .m4a y URL es accesible

## Checklist Final

- [ ] Backend funcionando sin errores
- [ ] Frontend funcionando sin errores
- [ ] Todas las pruebas funcionales pasadas
- [ ] Todas las pruebas de seguridad pasadas
- [ ] Todas las pruebas de UI/UX pasadas
- [ ] Flujo completo probado
- [ ] Documentación actualizada
- [ ] Código sin warnings de TypeScript
- [ ] Código sin warnings de Python

## Comandos Útiles

### Backend
```bash
# Ver logs del servidor
tail -f logs/app.log

# Ejecutar migraciones
alembic upgrade head

# Verificar estado de base de datos
psql -U postgres -d tu_database -c "SELECT * FROM servicio LIMIT 5;"
```

### Frontend
```bash
# Compilar sin errores
ng build --configuration production

# Ejecutar linter
ng lint

# Ver errores de TypeScript
ng build --watch
```

## Contacto

Si encuentras algún problema durante las pruebas, documenta:
1. Pasos para reproducir
2. Comportamiento esperado
3. Comportamiento actual
4. Capturas de pantalla
5. Logs del backend/frontend
