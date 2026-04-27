# ✅ Checklist: Configurar Groq API

## 📋 Pasos a Seguir (en orden)

### ☐ 1. Obtener API Key de Groq

- [ ] Ir a https://console.groq.com/
- [ ] Crear cuenta (Sign Up con Google/GitHub)
- [ ] Ir a https://console.groq.com/keys
- [ ] Hacer clic en "Create API Key"
- [ ] Copiar la key (empieza con `gsk_...`)
- [ ] Guardarla en un lugar seguro

**Tiempo estimado**: 2 minutos

---

### ☐ 2. Configurar Variables de Entorno

- [ ] Abrir archivo `.env` en la raíz del proyecto
- [ ] Buscar la línea `GROQ_API_KEY=gsk_pon_tu_api_key_aqui`
- [ ] Reemplazar con tu API key real
- [ ] Verificar que `GROQ_MODEL=llama-3.1-8b-instant`
- [ ] Verificar que `USE_REAL_AI=true`
- [ ] Guardar el archivo

**Ejemplo**:
```env
GROQ_API_KEY=gsk_abc123xyz789...
GROQ_MODEL=llama-3.1-8b-instant
WHISPER_MODEL_SIZE=base
USE_REAL_AI=true
```

**Tiempo estimado**: 1 minuto

---

### ☐ 3. Instalar/Actualizar Dependencias

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias nuevas**:
- `groq` - Cliente de Groq API

**Tiempo estimado**: 2-5 minutos (depende de tu conexión)

---

### ☐ 4. Verificar Instalación

```bash
# Verificar que groq esté instalado
python -c "import groq; print('✅ Groq instalado')"

# Verificar que torch esté instalado
python -c "import torch; print('✅ Torch instalado')"

# Verificar que clip esté instalado
python -c "import clip; print('✅ CLIP instalado')"

# Verificar que faster_whisper esté instalado
python -c "import faster_whisper; print('✅ Whisper instalado')"
```

**Todos deben mostrar "✅ ... instalado"**

**Tiempo estimado**: 30 segundos

---

### ☐ 5. Probar API Key de Groq

```bash
# Test rápido con cURL (reemplaza TU_API_KEY)
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hola"}]
  }'
```


**Debe responder con un JSON que contiene un mensaje**

**Tiempo estimado**: 30 segundos

---

### ☐ 6. Iniciar Servidor

```bash
# Ejecutar migraciones (solo primera vez)
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

**Debe mostrar**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Tiempo estimado**: 1 minuto

---

curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsdWJlcnRoZ3V0aWVycmV6QGdtYWlsLmNvbSIsInBlcnNvbmFfaWQiOjI1LCJyb2xlcyI6WyJjbGllbnRlIiwidGVjbmljbyIsImFkbWluX3RhbGxlciIsInN1cGVyX2FkbWluX3RhbGxlciIsImFkbWluX3Npc3RlbWEiXSwiZXhwIjoxNzc3MDM5NzgwfQ.IWbmIw3DkD0JL9xhyvugAgiOshcWIGG9i_cIynrz2HU" \
  -F "descripcion=Mi auto hace un ruido extraño en el motor" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "foto1=@C:\Users\Luberth\Downloads\pr1.jpg" \
  -F "foto2=@C:\Users\Luberth\Downloads\pr2.jpg" \
  -F "audio=@C:\Users\Luberth\Downloads\audio1.ogg"



### ☐ 7. Probar en Swagger UI

- [ ] Abrir navegador en http://localhost:8000/docs
- [ ] Buscar endpoint `POST /api/v1/diagnosticos/`
- [ ] Hacer clic en "Try it out"
- [ ] Llenar campos:
  - `descripcion`: "El motor hace ruido"
  - `ubicacion`: "-17.783333,-63.182222"
  - `fotos`: Subir 1-2 imágenes
  - `audio`: Subir un audio (opcional)
- [ ] Hacer clic en "Execute"
- [ ] Verificar respuesta (debe incluir diagnóstico generado)

**Tiempo estimado**: 2-3 minutos

---

### ☐ 8. Verificar Logs

En la consola donde corre el servidor, debes ver:

```
✅ CLIP listo
✅ Whisper listo
✅ Transcripción completada: 45 caracteres
✅ Imagen analizada: bateria_descargada (confianza 0.85)
🤖 Generando diagnóstico con Groq (llama-3.1-8b-instant)...
✅ Respuesta Groq recibida (523 chars)
```

**Si ves estos logs, todo funciona correctamente**

---

### ☐ 9. Configurar para Producción (Render)

- [ ] Ir a Render Dashboard
- [ ] Seleccionar tu servicio
- [ ] Ir a "Environment"
- [ ] Agregar variables:
  ```
  GROQ_API_KEY=gsk_tu_key_aqui
  GROQ_MODEL=llama-3.1-8b-instant
  WHISPER_MODEL_SIZE=base
  USE_REAL_AI=true
  ```
- [ ] Hacer clic en "Save Changes"
- [ ] Render redesplegará automáticamente

**Tiempo estimado**: 2 minutos

---

### ☐ 10. Commit y Push

```bash
git add .
git commit -m "Implementar Groq API para diagnósticos con IA"
git push
```

**Render detectará los cambios y desplegará automáticamente**

**Tiempo estimado**: 1 minuto

---

## 🎯 Checklist Rápido (Resumen)

```
☐ Obtener API key de Groq
☐ Configurar .env con tu API key
☐ pip install -r requirements.txt
☐ Probar API key con cURL
☐ uvicorn app.main:app --reload
☐ Probar en http://localhost:8000/docs
☐ Verificar logs (✅ CLIP, Whisper, Groq)
☐ Configurar variables en Render
☐ git push
☐ Verificar en producción
```

---

## ⏱️ Tiempo Total Estimado

- **Primera vez**: 15-20 minutos
- **Si ya tienes todo instalado**: 5 minutos

---

## 🆘 Si Algo Falla

### Error: "Invalid API Key"
```
✅ Verificar que copiaste bien la key
✅ Verificar que empiece con "gsk_"
✅ Verificar que esté en .env sin espacios
```

### Error: "Module 'groq' not found"
```bash
pip install groq
```

### Error: "Module 'torch' not found"
```bash
pip install torch
```

### Servidor no inicia
```bash
# Verificar que el puerto 8000 esté libre
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000
```

### Groq muy lento
```
✅ Verificar conexión a internet
✅ Probar con otro modelo más rápido
```

---

## 📊 Verificación Final

### ✅ Todo Funciona Si:

1. Servidor inicia sin errores
2. Swagger UI carga en http://localhost:8000/docs
3. Puedes crear una solicitud de diagnóstico
4. Recibes respuesta con diagnóstico generado
5. Los logs muestran "✅ Respuesta Groq recibida"

### ❌ Hay Problema Si:

1. Error "Invalid API Key" → Revisar .env
2. Error "Module not found" → Reinstalar dependencias
3. Error "Rate limit" → Esperar 1 minuto
4. Sin respuesta de Groq → Verificar internet

---

## 🎉 ¡Listo!

Una vez completado este checklist, tu sistema estará funcionando con:

- ✅ Groq API (LLM)
- ✅ CLIP (análisis de imágenes)
- ✅ Whisper (transcripción de audio)
- ✅ FastAPI (backend)
- ✅ PostgreSQL (base de datos)

**¡Todo funcionando en desarrollo y listo para producción!** 🚀

---

## 📞 Ayuda

Si tienes problemas, revisa:
- `INSTALACION_RAPIDA.md` - Guía paso a paso
- `RESUMEN_IMPLEMENTACION_GROQ.md` - Resumen completo
- `GUIA_GROQ_API.md` - Guía detallada de Groq
