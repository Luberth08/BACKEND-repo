# 🚀 Instalación Rápida - Sistema de Diagnóstico con IA

## ⚡ Configuración en 5 Minutos

### Paso 1: Obtener API Key de Groq (2 minutos)

1. Ve a: **https://console.groq.com/**
2. Haz clic en **"Sign Up"** (puedes usar Google/GitHub)
3. Ve a: **https://console.groq.com/keys**
4. Haz clic en **"Create API Key"**
5. Copia la key (empieza con `gsk_...`)

### Paso 2: Configurar Variables de Entorno (1 minuto)

Edita el archivo `.env` y pega tu API key:

```env
# Pega tu API key aquí
GROQ_API_KEY=gsk_tu_api_key_aqui

# Modelo a usar (recomendado)
GROQ_MODEL=llama-3.1-8b-instant

# Whisper para audio
WHISPER_MODEL_SIZE=base

# Activar IA
USE_REAL_AI=true
```

### Paso 3: Instalar Dependencias (2 minutos)

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 4: Iniciar Servidor

```bash
# Ejecutar migraciones (solo primera vez)
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Paso 5: Probar

Abre tu navegador en: **http://localhost:8000/docs**

---

## ✅ ¡Listo!

Tu sistema ya está funcionando con:
- ✅ **Groq API** para diagnósticos (LLM)
- ✅ **CLIP** para análisis de imágenes (local)
- ✅ **Whisper** para transcripción de audio (local)

---

## 🎯 Modelos Disponibles

Puedes cambiar el modelo en `.env`:

```env
# Rápido y eficiente (recomendado)
GROQ_MODEL=llama-3.1-8b-instant

# Más potente pero más lento
GROQ_MODEL=llama-3.1-70b-versatile

# Contexto muy largo
GROQ_MODEL=mixtral-8x7b-32768
```

---

## 💰 Límites Gratuitos

```
✅ 30 requests por minuto
✅ 14,400 tokens por minuto
✅ Sin costo
✅ Sin tarjeta de crédito
```

**Más que suficiente para desarrollo y producción inicial.**

---

## 🆘 Problemas Comunes

### Error: "Invalid API Key"
```
Solución: Verifica que copiaste bien la key en .env
Debe empezar con "gsk_"
```

### Error: "Module 'groq' not found"
```bash
pip install groq
```

### Error: "Module 'torch' not found"
```bash
pip install torch
```

### Whisper muy lento
```env
# Usa modelo más pequeño
WHISPER_MODEL_SIZE=tiny
```

---

## 📊 Verificar que Funciona

### Test Rápido con cURL

```bash
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hola"}]
  }'
```

Si responde, tu API key funciona correctamente.

---

## 🚀 Desplegar en Render

### 1. Configurar Variables de Entorno en Render

En tu dashboard de Render, agrega:

```
GROQ_API_KEY=gsk_tu_api_key_aqui
GROQ_MODEL=llama-3.1-8b-instant
WHISPER_MODEL_SIZE=base
USE_REAL_AI=true
```

### 2. Push a GitHub

```bash
git add .
git commit -m "Configurar Groq API"
git push
```

### 3. Render Detecta y Despliega Automáticamente

¡Listo! Tu app funciona en producción sin Docker ni configuración compleja.

---

## 📚 Documentación Completa

- **Groq Docs**: https://console.groq.com/docs
- **Modelos disponibles**: https://console.groq.com/docs/models
- **Límites y pricing**: https://console.groq.com/settings/limits

---

## 🎓 Resumen

**Antes (con Ollama)**:
- ❌ Instalar Docker
- ❌ Descargar modelo (2GB)
- ❌ 4-8GB RAM necesaria
- ❌ Configuración compleja
- ❌ No funciona en Render Free

**Ahora (con Groq)**:
- ✅ Solo API key
- ✅ 0GB RAM extra
- ✅ Configuración en 5 minutos
- ✅ Funciona en Render Free
- ✅ 10x más rápido

**¡Mucho más simple!** 🎉
