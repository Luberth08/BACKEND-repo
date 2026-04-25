# Instrucciones para Poblar Tipos de Incidentes

## Problema
El sistema necesita que la tabla `tipo_incidente` tenga datos para que la IA pueda asociar incidentes a los diagnósticos.

## Solución

### Opción 1: Ejecutar el script de seed (Recomendado)

1. Asegúrate de tener las dependencias instaladas:
```bash
pip install -r requirements.txt
```

2. Ejecuta el script de seed:
```bash
python seed_tipos_incidente.py
```

Este script insertará 20 tipos de incidentes comunes si la tabla está vacía.

### Opción 2: Insertar manualmente con SQL

Conéctate a tu base de datos PostgreSQL y ejecuta:

```sql
INSERT INTO tipo_incidente (concepto, prioridad, requiere_remolque) VALUES
('falla_motor', 1, true),
('problema_frenos', 1, true),
('fuga_aceite', 2, false),
('bateria_descargada', 2, false),
('neumatico_pinchado', 2, false),
('sobrecalentamiento', 1, true),
('problema_transmision', 1, true),
('falla_electrica', 2, false),
('problema_suspension', 2, false),
('fuga_combustible', 1, true),
('problema_direccion', 1, true),
('ruido_anormal', 3, false),
('vibracion_excesiva', 3, false),
('luz_check_engine', 2, false),
('problema_arranque', 2, false),
('falla_aire_acondicionado', 3, false),
('problema_escape', 3, false),
('falla_embrague', 2, false),
('informacion_insuficiente', 3, false),
('desconocido', 3, false);
```

### Opción 3: Usar Render Shell (Para producción)

1. Ve a tu dashboard de Render
2. Selecciona tu servicio de backend
3. Ve a la pestaña "Shell"
4. Ejecuta:
```bash
python seed_tipos_incidente.py
```

## Verificar que funcionó

Puedes verificar que los datos se insertaron correctamente:

```sql
SELECT COUNT(*) FROM tipo_incidente;
```

Deberías ver 20 registros.

## Tipos de Incidentes Incluidos

| Concepto | Prioridad | Requiere Remolque |
|----------|-----------|-------------------|
| falla_motor | 1 (Alta) | Sí |
| problema_frenos | 1 (Alta) | Sí |
| fuga_aceite | 2 (Media) | No |
| bateria_descargada | 2 (Media) | No |
| neumatico_pinchado | 2 (Media) | No |
| sobrecalentamiento | 1 (Alta) | Sí |
| problema_transmision | 1 (Alta) | Sí |
| falla_electrica | 2 (Media) | No |
| problema_suspension | 2 (Media) | No |
| fuga_combustible | 1 (Alta) | Sí |
| problema_direccion | 1 (Alta) | Sí |
| ruido_anormal | 3 (Baja) | No |
| vibracion_excesiva | 3 (Baja) | No |
| luz_check_engine | 2 (Media) | No |
| problema_arranque | 2 (Media) | No |
| falla_aire_acondicionado | 3 (Baja) | No |
| problema_escape | 3 (Baja) | No |
| falla_embrague | 2 (Media) | No |
| informacion_insuficiente | 3 (Baja) | No |
| desconocido | 3 (Baja) | No |

## Notas Importantes

- **informacion_insuficiente**: La IA devuelve este concepto cuando no tiene suficiente información para hacer un diagnóstico
- **desconocido**: Se usa cuando la IA no puede clasificar el problema en ninguna categoría conocida
- Los conceptos deben coincidir exactamente con los que la IA puede devolver
