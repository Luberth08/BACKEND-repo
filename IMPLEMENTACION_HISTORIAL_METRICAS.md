# Implementación de Historial de Estados y Métricas de Servicios

## Resumen

Se implementó un sistema completo para:
1. **Registrar cada cambio de estado** de un servicio en una tabla de historial
2. **Calcular y guardar métricas** cuando un servicio se finaliza

## Tablas Creadas

### 1. `historial_estados_servicio`
Registra TODOS los cambios de estado de un servicio.

```sql
CREATE TABLE historial_estados_servicio (
    id SERIAL PRIMARY KEY,
    estado estadoservicio NOT NULL,
    tiempo TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_servicio INT NOT NULL REFERENCES servicio(id) ON DELETE CASCADE
);
```

**Propósito:** Auditoría completa - saber cuándo y cómo cambió cada estado.

### 2. `metrica`
Almacena métricas calculadas de servicios finalizados.

```sql
CREATE TABLE metrica (
    id SERIAL PRIMARY KEY,
    tiempo_respuesta INTERVAL,  -- desde creación de solicitud hasta aceptación
    tiempo_llegada INTERVAL,    -- desde aceptación hasta "en_lugar"
    tiempo_resolucion INTERVAL, -- desde "en_lugar" hasta "finalizado"
    id_servicio INT NOT NULL UNIQUE REFERENCES servicio(id) ON DELETE CASCADE
);
```

**Propósito:** Análisis de rendimiento del taller y técnicos.

## Funciones Implementadas

### `registrar_cambio_estado(db, id_servicio, nuevo_estado)`
- Se llama **cada vez** que cambia el estado de un servicio
- Crea un registro en `historial_estados_servicio`
- Registra el timestamp automáticamente

### `calcular_y_guardar_metricas(db, id_servicio)`
- Se llama **solo cuando** el servicio se marca como `finalizado`
- Lee el historial de estados
- Calcula los 3 intervalos de tiempo
- Guarda en la tabla `metrica`

### `actualizar_estado_servicio(db, id_servicio, nuevo_estado)`
- **Función principal** para cambiar estados
- Actualiza el estado del servicio
- Llama a `registrar_cambio_estado()`
- Si el estado es `finalizado`, llama a `calcular_y_guardar_metricas()`

## Integración en el Código

### 1. Al aceptar una solicitud (`aceptar_solicitud_servicio`)
```python
servicio = await servicio_crud.create(db, servicio_data)
await registrar_cambio_estado(db, servicio.id, EstadoServicio.tecnico_asignado)
```

### 2. Al completar un servicio (`completar_servicio`)
```python
await actualizar_estado_servicio(db, id_servicio, EstadoServicio.finalizado)
# Esto automáticamente:
# - Registra el cambio en historial
# - Calcula y guarda las métricas
```

### 3. Desde la app móvil (endpoint técnico)
```python
# En tecnico_servicios.py - actualizar_estado_servicio
await servicio_service.actualizar_estado_servicio(db, servicio_id, nuevo_estado_enum)
# Automáticamente registra historial y métricas si es finalizado
```

## Flujo Completo de Ejemplo

1. **Taller acepta solicitud** → Estado: `tecnico_asignado`
   - ✅ Se guarda en `historial_estados_servicio`

2. **Técnico inicia viaje** → Estado: `en_camino`
   - ✅ Se guarda en `historial_estados_servicio`

3. **Técnico llega** → Estado: `en_lugar`
   - ✅ Se guarda en `historial_estados_servicio`

4. **Técnico inicia reparación** → Estado: `en_atencion`
   - ✅ Se guarda en `historial_estados_servicio`

5. **Técnico finaliza** → Estado: `finalizado`
   - ✅ Se guarda en `historial_estados_servicio`
   - ✅ Se calculan métricas:
     - `tiempo_respuesta` = tiempo entre solicitud y aceptación
     - `tiempo_llegada` = tiempo entre aceptación y llegada
     - `tiempo_resolucion` = tiempo entre llegada y finalización
   - ✅ Se guardan en tabla `metrica`

## Métricas Calculadas

### `tiempo_respuesta`
**Desde:** Creación de la solicitud  
**Hasta:** Estado `tecnico_asignado`  
**Mide:** Qué tan rápido responde el taller

### `tiempo_llegada`
**Desde:** Estado `tecnico_asignado`  
**Hasta:** Estado `en_lugar`  
**Mide:** Qué tan rápido llega el técnico al cliente

### `tiempo_resolucion`
**Desde:** Estado `en_lugar`  
**Hasta:** Estado `finalizado`  
**Mide:** Cuánto tiempo toma resolver el problema

## Consultas Útiles

### Ver historial de un servicio
```sql
SELECT estado, tiempo 
FROM historial_estados_servicio 
WHERE id_servicio = 123 
ORDER BY tiempo ASC;
```

### Ver métricas de un servicio
```sql
SELECT 
    tiempo_respuesta,
    tiempo_llegada,
    tiempo_resolucion
FROM metrica 
WHERE id_servicio = 123;
```

### Métricas promedio de un taller
```sql
SELECT 
    AVG(tiempo_respuesta) as promedio_respuesta,
    AVG(tiempo_llegada) as promedio_llegada,
    AVG(tiempo_resolucion) as promedio_resolucion
FROM metrica m
JOIN servicio s ON s.id = m.id_servicio
WHERE s.id_taller = 1;
```

## Archivos Modificados

1. **Modelos:**
   - `app/models/metrica.py` (nuevo)
   - `app/models/historial_estado_servicio.py` (nuevo)
   - `app/models/servicio.py` (agregadas relaciones)
   - `app/models/__init__.py` (importaciones)

2. **Servicios:**
   - `app/services/servicio_service.py` (funciones helper)

3. **Endpoints:**
   - `app/api/api_v1/endpoints/tecnico_servicios.py` (integración)

4. **Migraciones:**
   - `alembic/versions/8d27e4211689_mensaje_descriptivo.py`

## Próximos Pasos (Opcional)

1. Crear endpoints para consultar métricas:
   - GET `/api/v1/metricas/servicio/{id}`
   - GET `/api/v1/metricas/taller/{id}`
   - GET `/api/v1/historial/servicio/{id}`

2. Dashboard de métricas en el frontend del taller

3. Reportes de rendimiento de técnicos

4. Alertas si las métricas superan umbrales
