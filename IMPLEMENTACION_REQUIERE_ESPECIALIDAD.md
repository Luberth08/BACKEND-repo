# Implementación: Relación Categoría Incidente - Especialidad

## Resumen
Se implementó la funcionalidad para que cada categoría de incidente requiera al menos una especialidad. Esta es una relación muchos-a-muchos entre `categoria_incidente` y `especialidad`.

## Cambios Realizados

### 1. Modelo de Datos
**Archivo nuevo:** `app/models/requiere_especialidad.py`
- Tabla intermedia con clave primaria compuesta
- Relación muchos-a-muchos entre categorías y especialidades
- Eliminación en cascada (CASCADE) cuando se elimina una categoría o especialidad

**Archivos modificados:**
- `app/models/categoria_incidente.py`: Agregado relationship a especialidades
- `app/models/especialidad.py`: Agregado relationship a categorías
- `app/models/__init__.py`: Importado el nuevo modelo

### 2. CRUD
**Archivo nuevo:** `app/crud/crud_requiere_especialidad.py`

Métodos implementados:
- `get_especialidades_by_categoria()`: Obtiene IDs de especialidades de una categoría
- `get_categorias_by_especialidad()`: Obtiene IDs de categorías que requieren una especialidad
- `add_especialidad_to_categoria()`: Asocia una especialidad a una categoría
- `remove_especialidad_from_categoria()`: Elimina una asociación específica
- `remove_all_especialidades_from_categoria()`: Elimina todas las especialidades de una categoría
- `set_especialidades_for_categoria()`: Reemplaza todas las especialidades (usado en create/update)

### 3. Schemas
**Archivo modificado:** `app/schemas/categoria_incidente.py`

Cambios:
- `CategoriaIncidenteCreate`: Agregado campo `especialidad_ids: List[int]` (requerido, mínimo 1)
- `CategoriaIncidenteUpdate`: Agregado campo `especialidad_ids: List[int] | None` (opcional, pero si se envía debe tener mínimo 1)
- `CategoriaIncidenteResponse`: Agregado campo `especialidad_ids: List[int]`
- Validadores con `@field_validator` para asegurar al menos una especialidad

### 4. Servicios
**Archivo modificado:** `app/services/categoria_incidente_service.py`

Funciones actualizadas:
- `list_categorias()`: Ahora incluye las especialidades de cada categoría
- `create_categoria()`: 
  - Valida que todas las especialidades existan
  - Crea la categoría y asocia las especialidades
- `update_categoria()`:
  - Valida especialidades si se están actualizando
  - Permite actualizar nombre y/o especialidades independientemente
- `delete_categoria()`: Las especialidades se eliminan automáticamente por CASCADE

**Función nueva:**
- `get_categoria_by_id()`: Obtiene una categoría específica con sus especialidades

**Archivo modificado:** `app/services/especialidad_service.py`
- `delete_especialidad()`: Ahora valida que no existan categorías que requieran la especialidad antes de eliminarla

**Archivo modificado:** `app/api/api_v1/endpoints/especialidades.py`
- Aumentado límite máximo de `limit` de 100 a 1000 para soportar listados completos

### 5. Endpoints
**Archivo modificado:** `app/api/api_v1/endpoints/admin_categorias.py`

Endpoint nuevo:
- `GET /admin/categorias/{categoria_id}`: Obtiene una categoría específica con sus especialidades

Endpoints actualizados:
- `GET /admin/categorias/`: Devuelve especialidades en cada categoría
- `POST /admin/categorias/`: Requiere `especialidad_ids` en el body
- `PUT /admin/categorias/{categoria_id}`: Acepta `especialidad_ids` opcional en el body

### 6. Migración de Base de Datos
**Archivo nuevo:** `alembic/versions/e3a8b12c6d45_add_requiere_especialidad.py`

Crea la tabla `requiere_especialidad` con:
- Clave primaria compuesta (id_categoria_incidente, id_especialidad)
- Foreign keys con CASCADE delete
- Índices automáticos en las claves foráneas

## Uso de la API

### Crear Categoría con Especialidades
```json
POST /admin/categorias/
{
  "nombre": "Mecánica General",
  "especialidad_ids": [1, 2, 3]
}
```

### Actualizar Solo Nombre
```json
PUT /admin/categorias/1
{
  "nombre": "Mecánica Avanzada"
}
```

### Actualizar Solo Especialidades
```json
PUT /admin/categorias/1
{
  "especialidad_ids": [1, 2, 4, 5]
}
```

### Actualizar Ambos
```json
PUT /admin/categorias/1
{
  "nombre": "Mecánica Avanzada",
  "especialidad_ids": [1, 2, 4, 5]
}
```

### Obtener Categoría con Especialidades
```json
GET /admin/categorias/1

Response:
{
  "id": 1,
  "nombre": "Mecánica General",
  "especialidad_ids": [1, 2, 3]
}
```

### Listar Categorías
```json
GET /admin/categorias/?skip=0&limit=10

Response:
{
  "items": [
    {
      "id": 1,
      "nombre": "Mecánica General",
      "especialidad_ids": [1, 2, 3]
    },
    {
      "id": 2,
      "nombre": "Electricidad",
      "especialidad_ids": [4, 5]
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 10
}
```

## Validaciones Implementadas

1. **Al crear categoría**: Debe incluir al menos una especialidad
2. **Al actualizar categoría**: Si se envían especialidades, debe haber al menos una
3. **Existencia de especialidades**: Valida que todas las especialidades existan antes de asociarlas
4. **Nombre único**: Mantiene la validación de nombre único para categorías
5. **Eliminación de categoría**: No permite eliminar si hay tipos de incidente asociados
6. **Eliminación de especialidad**: No permite eliminar si hay:
   - Técnicos asociados a esa especialidad
   - Categorías que requieren esa especialidad

## Pasos para Aplicar

1. Ejecutar la migración:
```bash
alembic upgrade head
```

2. Reiniciar el servidor FastAPI

3. Probar los endpoints actualizados

## Notas Técnicas

- La relación es bidireccional: puedes acceder a `categoria.especialidades` y `especialidad.categorias`
- El CASCADE delete asegura integridad referencial
- Los validadores de Pydantic previenen datos inválidos antes de llegar a la base de datos
- La arquitectura mantiene la separación de responsabilidades (CRUD, Service, Endpoint)
