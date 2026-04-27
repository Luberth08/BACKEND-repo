# 📸 CÓMO PROBAR CON ARCHIVOS REALES

## 🎯 OPCIÓN 1: Usar archivos que ya tengas

Si tienes fotos y audio en tu computadora, usa este comando:

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/web/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"luberthgutierrez@gmail.com","password":"123456"}'

# 2. Copiar el token
TOKEN="tu_token_aqui"

# 3. Enviar con tus archivos (ajusta las rutas)
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=El motor hace un ruido extraño al acelerar" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=TEST123" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020" \
  -F "foto1=@C:/Users/TuUsuario/Pictures/foto1.jpg" \
  -F "foto2=@C:/Users/TuUsuario/Pictures/foto2.jpg" \
  -F "audio=@C:/Users/TuUsuario/Music/audio.ogg"
```

**Nota:** Reemplaza las rutas con las de tus archivos reales.

---

## 🎯 OPCIÓN 2: Crear archivos de prueba simples

### En Windows (PowerShell):

```powershell
# Crear carpeta temporal
New-Item -ItemType Directory -Force -Path "temp_test"

# Crear archivos de texto como placeholder
"Imagen de prueba 1" | Out-File -FilePath "temp_test/foto1.jpg"
"Imagen de prueba 2" | Out-File -FilePath "temp_test/foto2.jpg"
"Audio de prueba" | Out-File -FilePath "temp_test/audio.ogg"

# Ahora usa estos archivos en el curl
```

### En Linux/Mac:

```bash
# Crear carpeta temporal
mkdir -p temp_test

# Crear archivos de texto como placeholder
echo "Imagen de prueba 1" > temp_test/foto1.jpg
echo "Imagen de prueba 2" > temp_test/foto2.jpg
echo "Audio de prueba" > temp_test/audio.ogg

# Ahora usa estos archivos en el curl
```

---

## 🎯 OPCIÓN 3: Usar el script automático

```bash
cd BACKEND-repo
bash test_diagnostico_con_archivos.sh
```

Este script:
1. ✅ Crea archivos de prueba automáticamente
2. ✅ Hace login
3. ✅ Envía la solicitud con archivos
4. ✅ Muestra las evidencias guardadas
5. ✅ Limpia los archivos temporales

---

## 🔍 VERIFICAR EN BASE DE DATOS

Después de ejecutar el test, verifica que se guardaron las evidencias:

```sql
-- Ver la última solicitud creada
SELECT * FROM solicitud_diagnostico ORDER BY id DESC LIMIT 1;

-- Ver las evidencias de esa solicitud (reemplaza 5 con el ID real)
SELECT * FROM evidencia WHERE id_solicitud_diagnostico = 5;

-- Deberías ver algo como:
-- id | url                                    | transcripcion                          | tipo   | id_solicitud
-- 1  | /static/uploads/diagnosticos/abc.jpg   | CLIP Analysis: falla_motor (85.00%)   | imagen | 5
-- 2  | /static/uploads/diagnosticos/def.jpg   | CLIP Analysis: falla_motor (78.00%)   | imagen | 5
-- 3  | /static/uploads/diagnosticos/ghi.ogg   | El motor hace un ruido extraño...     | audio  | 5
```

---

## 📋 QUÉ ESPERAR

### ✅ CON ARCHIVOS:
- **Evidencias:** 2-3 registros en tabla `evidencia`
- **Imágenes:** `tipo='imagen'`, `transcripcion` con análisis CLIP
- **Audio:** `tipo='audio'`, `transcripcion` con texto transcrito por Whisper
- **Archivos físicos:** Guardados en `BACKEND-repo/static/uploads/diagnosticos/`

### ❌ SIN ARCHIVOS:
- **Evidencias:** 0 registros en tabla `evidencia`
- **Diagnóstico:** Se crea solo con la descripción de texto
- **IA:** GROQ analiza solo el texto, sin imágenes ni audio

---

## 🎨 CREAR IMÁGENES REALES DE PRUEBA

Si quieres crear imágenes reales (no solo texto):

### Con Python:
```python
from PIL import Image

# Crear imagen roja 200x200
img1 = Image.new('RGB', (200, 200), color='red')
img1.save('foto1.jpg')

# Crear imagen azul 200x200
img2 = Image.new('RGB', (200, 200), color='blue')
img2.save('foto2.jpg')
```

### Con ImageMagick (si está instalado):
```bash
convert -size 200x200 xc:red foto1.jpg
convert -size 200x200 xc:blue foto2.jpg
```

---

## 🎵 CREAR AUDIO REAL DE PRUEBA

### Con ffmpeg (si está instalado):
```bash
# Crear 2 segundos de silencio en formato OGG
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 2 -q:a 9 -acodec libopus audio.ogg
```

### O simplemente:
Graba un audio de 2-3 segundos con tu teléfono describiendo el problema y conviértelo a .ogg o .mp3

---

## 💡 TIPS

1. **Formatos soportados:**
   - Imágenes: `.jpg`, `.jpeg`, `.png`
   - Audio: `.ogg`, `.mp3`, `.wav`, `.m4a`

2. **Tamaños recomendados:**
   - Imágenes: < 5 MB cada una
   - Audio: < 10 MB

3. **Para probar CLIP:**
   - Usa imágenes reales de motores, frenos, etc.
   - CLIP analizará el contenido visual

4. **Para probar Whisper:**
   - Graba audio describiendo el problema
   - Whisper transcribirá el audio a texto

5. **Sin archivos:**
   - El sistema funciona igual
   - Solo usa la descripción de texto
   - No se guardan evidencias
