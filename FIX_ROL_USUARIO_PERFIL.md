# Fix - Agregar Rol de Usuario al Perfil

## 🐛 Problema Identificado

El usuario técnico no podía ver la pestaña "Técnico" en la app móvil porque:

1. La app móvil verifica si el usuario es técnico llamando a `/api/v1/perfil/me`
2. El endpoint `/perfil/me` **NO devolvía el rol del usuario**
3. Sin el rol, la app no podía determinar si mostrar la pestaña de técnico

## ✅ Solución Implementada

Se agregó el campo `rol` al perfil del usuario para que la app móvil pueda identificar correctamente el rol.

---

## 📝 Cambios Realizados

### 1. Schema Actualizado

**Archivo:** `app/schemas/perfil.py`

```python
class PerfilResponse(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    url_img_perfil: Optional[str] = None
    nombre: Optional[str] = None
    apellido_p: Optional[str] = None
    apellido_m: Optional[str] = None
    ci: Optional[str] = None
    complemento: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    rol: Optional[str] = None  # ⭐ NUEVO CAMPO
```

### 2. Endpoint GET /perfil/me Actualizado

**Archivo:** `app/api/api_v1/endpoints/perfiles.py`

```python
@router.get("/me", response_model=PerfilResponse)
async def get_my_profile(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el perfil completo del usuario autenticado."""
    from sqlalchemy import select
    from app.models.rol_usuario import RolUsuario
    from app.models.rol import Rol
    
    usuario = await crud_usuario.get_by_id_persona(db, current_persona.id)
    
    # ⭐ Obtener el rol principal del usuario
    rol_nombre = None
    if usuario:
        result = await db.execute(
            select(Rol.nombre)
            .join(RolUsuario, RolUsuario.id_rol == Rol.id)
            .where(RolUsuario.id_usuario == usuario.id)
            .limit(1)
        )
        rol_nombre = result.scalar_one_or_none()
    
    return PerfilResponse(
        # ... otros campos
        rol=rol_nombre,  # ⭐ NUEVO
    )
```

### 3. Otros Endpoints Actualizados

También se actualizaron:
- `PUT /perfil/me` - Actualizar perfil
- `POST /perfil/create-usuario` - Crear usuario

Todos ahora incluyen el campo `rol` en la respuesta.

---

## 🔍 Cómo Funciona

### Flujo Completo:

```
1. Usuario inicia sesión en app móvil
   ↓
2. App llama a GET /api/v1/perfil/me
   ↓
3. Backend obtiene:
   - Datos de persona
   - Datos de usuario
   - Rol del usuario (NUEVO)
   ↓
4. Backend retorna JSON con rol:
   {
     "email": "tecnico@example.com",
     "nombre": "Juan",
     "rol": "tecnico"  ← NUEVO
   }
   ↓
5. App móvil verifica:
   if (rol == "tecnico" || rol == "empleado") {
     mostrar pestaña "Técnico"
   }
   ↓
6. Usuario ve pestaña "Técnico" ✅
```

---

## 📊 Respuesta del Endpoint

### Antes:
```json
{
  "email": "tecnico@example.com",
  "username": "juan_tecnico",
  "nombre": "Juan",
  "apellido_p": "Pérez",
  "telefono": "+593987654321"
  // ❌ Sin campo "rol"
}
```

### Ahora:
```json
{
  "email": "tecnico@example.com",
  "username": "juan_tecnico",
  "nombre": "Juan",
  "apellido_p": "Pérez",
  "telefono": "+593987654321",
  "rol": "tecnico"  // ✅ Campo agregado
}
```

---

## 🎯 Roles Soportados

El campo `rol` puede contener:
- `"tecnico"` - Usuario técnico de taller
- `"empleado"` - Empleado de taller (también puede ser técnico)
- `"admin"` - Administrador del sistema
- `"cliente"` - Cliente normal (por defecto)
- `null` - Usuario sin rol asignado

---

## 📱 Verificación en App Móvil

### Código en `lib/services/user_service.dart`:

```dart
static Future<bool> esTecnico(String token) async {
  try {
    final info = await obtenerInfoUsuario(token);
    if (info != null) {
      // Verificar si tiene rol de técnico o empleado
      final rol = info['rol']?.toString().toLowerCase();
      return rol == 'tecnico' || rol == 'empleado';
    }
    return false;
  } catch (e) {
    print('Error verificando si es técnico: $e');
    return false;
  }
}
```

### Código en `lib/screens/home_screen.dart`:

```dart
Future<void> _verificarRolUsuario() async {
  try {
    final token = await Session.getToken();
    if (token != null) {
      final esTecnico = await UserService.esTecnico(token);
      setState(() {
        _esTecnico = esTecnico;
        _configurarTabs();  // Configura pestañas según rol
      });
    }
  } catch (e) {
    print('Error verificando rol: $e');
  }
}
```

---

## ✅ Testing

### Prueba Manual:

1. **Crear usuario técnico en la base de datos:**
```sql
-- Asignar rol de técnico a un usuario
INSERT INTO rol_usuario (id_usuario, id_rol, id_taller)
VALUES (1, (SELECT id FROM rol WHERE nombre = 'tecnico'), 1);
```

2. **Probar endpoint:**
```bash
curl -X GET "http://localhost:8000/api/v1/perfil/me" \
  -H "Authorization: Bearer {token}"
```

3. **Verificar respuesta:**
```json
{
  "email": "usuario@example.com",
  "rol": "tecnico"  ← Debe aparecer
}
```

4. **Probar en app móvil:**
   - Iniciar sesión con usuario técnico
   - Verificar que aparece pestaña "Técnico" en la barra inferior
   - Tap en pestaña "Técnico"
   - Debe mostrar selector de talleres

---

## 🔒 Consideraciones de Seguridad

1. **Rol Principal:**
   - Se devuelve solo el primer rol encontrado
   - Si el usuario tiene múltiples roles, se retorna el primero

2. **Privacidad:**
   - El rol solo es visible para el propio usuario
   - No se expone información de roles de otros usuarios

3. **Validación:**
   - El rol se obtiene directamente de la base de datos
   - No se puede falsificar desde el cliente

---

## 📝 Notas Importantes

1. **Múltiples Roles:**
   - Si un usuario tiene múltiples roles (ej: técnico en varios talleres)
   - Se retorna solo el primer rol encontrado
   - Esto es suficiente para determinar si mostrar la pestaña

2. **Usuarios Sin Rol:**
   - Si el usuario no tiene rol asignado, `rol` será `null`
   - La app móvil lo tratará como cliente normal

3. **Compatibilidad:**
   - El cambio es backward compatible
   - Clientes antiguos que no esperan el campo `rol` seguirán funcionando

---

## 🚀 Resultado

Ahora cuando un usuario técnico inicia sesión en la app móvil:

1. ✅ El endpoint `/perfil/me` devuelve el rol
2. ✅ La app detecta que es técnico
3. ✅ Se muestra la pestaña "Técnico" en la barra inferior
4. ✅ El técnico puede seleccionar talleres y ver servicios

---

**Estado:** ✅ Completado y Funcional  
**Fecha:** 2026-04-26  
**Archivos Modificados:** 2  
**Breaking Changes:** No
