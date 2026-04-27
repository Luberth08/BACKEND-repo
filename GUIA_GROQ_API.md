# 🚀 Guía: Usar Groq API en Producción

## ¿Qué es Groq?

**Groq** es una plataforma que ofrece acceso a LLMs (como Llama 3) con velocidades increíbles gracias a sus chips especializados (LPU). Lo mejor: **es GRATIS** con límites generosos.

---

## ✅ Ventajas de Groq API

| Característica | Groq API | Ollama Local |
|----------------|----------|--------------|
| **Costo** | ✅ Gratis (30 req/min) | ✅ Gratis |
| **Velocidad** | ⚡ SÚPER RÁPIDO (10-100x) | Depende de tu hardware |
| **RAM necesaria** | ✅ 0GB (corre en sus servidores) | ❌ 4-8GB |
| **Funciona en Render Free** | ✅ Sí | ❌ No |
| **Instalación** | ✅ Solo API key | ❌ Requiere Docker/Ollama |
| **Privacidad** | ⚠️ Datos van a Groq | ✅ 100% local |
| **Offline** | ❌ No | ✅ Sí |

---

## 📋 Paso 1: Obtener API Key (GRATIS)

### 1. Crear Cuenta
1. Ve a: https://console.groq.com/
2. Haz clic en "Sign Up" (puedes usar Google/GitHub)
3. Confirma tu email

### 2. Generar API Key
1. Ve a: https://console.groq.com/keys
2. Haz clic en "Create API Key"
3. Dale un nombre (ej: "Asistencia Vehicular")
4. Copia la key (empieza con `gsk_...`)
5. ⚠️ **GUÁRDALA**: No la podrás ver de nuevo

---

## 🔧 Paso 2: Configurar en tu Proyecto

### Opción A: Desarrollo Local (Probar Groq)

Edita tu `.env`:
```env
# Activar Groq API
USE_GROQ=true
GROQ_API_KEY=gsk_tu_api_key_aqui

# Modelo a usar (opciones abajo)
GROQ_MODEL=llama-3.1-8b-instant

# Whisper y CLIP siguen siendo locales
USE_REAL_AI=true
WHISPER_MODEL_SIZE=base
```

### Opción B: Producción en Render

1. **En Render Dashboard**:
   - Ve a tu servicio → "Environment"
   - Agrega variables:
     ```
     USE_GROQ=true
     GROQ_API_KEY=gsk_tu_api_key_aqui
     GROQ_MODEL=llama-3.1-8b-instant
     ```

2. **Redeploy**:
   - Render detectará los cambios
   - Usará Groq en lugar de Ollama

---

## 🎯 Paso 3: Cambiar el Código

### Opción 1: Reemplazar ai_service.py (Recomendado)

```bash
# Renombrar el actual
mv app/services/ai_service.py app/services/ai_service_ollama.py

# Usar la versión con Groq
mv app/services/ai_service_groq.py app/services/ai_service.py
```

### Opción 2: Modificar Manualmente

Ya creé `ai_service_groq.py` que detecta automáticamente si usar Ollama o Groq según la variable `USE_GROQ`.

---

## 📊 Modelos Disponibles en Groq

### Recomendados para tu Proyecto

| Modelo | Velocidad | Precisión | Uso Recomendado |
|--------|-----------|-----------|-----------------|
| **llama-3.1-8b-instant** | ⚡⚡⚡ | ⭐⭐⭐ | **Producción** (balance perfecto) |
| **llama-3.1-70b-versatile** | ⚡⚡ | ⭐⭐⭐⭐⭐ | Casos complejos |
| **llama-3.2-3b-preview** | ⚡⚡⚡ | ⭐⭐ | Desarrollo rápido |
| **mixtral-8x7b-32768** | ⚡⚡ | ⭐⭐⭐⭐ | Contexto largo |

### Mi Recomendación
```env
GROQ_MODEL=llama-3.1-8b-instant
```
- Muy rápido (responde en 1-2 segundos)
- Buena precisión para diagnósticos
- Gratis hasta 30 req/min

---

## 💰 Límites del Plan Gratuito

```
✅ 30 requests por minuto (RPM)
✅ 14,400 tokens por minuto (TPM)
✅ Sin costo
✅ Sin tarjeta de crédito
```

### ¿Es Suficiente?

**Para tu proyecto: SÍ, más que suficiente**

Ejemplo de uso:
- 1 diagnóstico = 1 request
- Tiempo promedio: 2 segundos
- Máximo teórico: 30 diagnósticos/minuto = **1,800 diagnósticos/hora**

Incluso con 100 usuarios activos, no llegarías al límite.

---

## 🧪 Paso 4: Probar Groq

### Test Rápido con cURL
```bash
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer gsk_tu_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]
  }'
```

### Test en tu Aplicación
```bash
# 1. Configurar .env con USE_GROQ=true

# 2. Iniciar servidor
uvicorn app.main:app --reload

# 3. Crear solicitud de diagnóstico
# Debería usar Groq automáticamente
```

---

## 📈 Comparación de Velocidad

### Ollama Local (CPU)
```
Transcripción: ~5 segundos
Análisis imágenes: ~2 segundos
Generación diagnóstico: ~10-30 segundos
TOTAL: ~17-37 segundos
```

### Con Groq API
```
Transcripción: ~5 segundos (local)
Análisis imágenes: ~2 segundos (local)
Generación diagnóstico: ~1-2 segundos (Groq)
TOTAL: ~8-9 segundos ⚡
```

**Mejora: 2-4x más rápido**

---

## 🔒 Seguridad

### ¿Qué Datos se Envían a Groq?
- ✅ Descripción del problema
- ✅ Transcripción del audio
- ✅ Resultados del análisis de imágenes (solo texto)
- ❌ **NO** se envían las imágenes originales
- ❌ **NO** se envía el audio original

### Privacidad
- Groq **NO** entrena modelos con tus datos
- Datos **NO** se comparten con terceros
- Puedes revisar su política: https://groq.com/privacy-policy/

---

## 🚀 Estrategia Recomendada

### Fase 1: Desarrollo (Ahora)
```env
USE_GROQ=false  # Usar Ollama local
```
- Aprende cómo funciona
- No dependes de internet
- 100% privado

### Fase 2: Testing (Antes de Producción)
```env
USE_GROQ=true  # Probar Groq
```
- Verifica que funcione
- Mide velocidad
- Prueba límites

### Fase 3: Producción (Render)
```env
USE_GROQ=true  # Usar Groq en producción
```
- Funciona en Render Free
- Rápido y confiable
- Sin costo

---

## 🆘 Troubleshooting

### Error: "Invalid API Key"
```bash
# Verificar que la key esté correcta
echo $GROQ_API_KEY

# Debe empezar con "gsk_"
```

### Error: "Rate Limit Exceeded"
```
Solución: Esperar 1 minuto
Causa: Más de 30 requests en 1 minuto
```

### Error: "Model not found"
```bash
# Verificar modelos disponibles:
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer gsk_tu_key"
```

### Groq muy lento
```
Causa: Problema de red/internet
Solución: Verificar conexión
```

---

## 📊 Monitoreo de Uso

### Ver Uso en Dashboard
1. Ve a: https://console.groq.com/
2. Sección "Usage"
3. Verás:
   - Requests por día
   - Tokens usados
   - Modelos más usados

### Alertas
Groq te avisa por email si:
- Llegas al 80% del límite
- Hay errores frecuentes

---

## 💡 Tips y Mejores Prácticas

### 1. Caché de Respuestas
```python
# Si el mismo problema se repite, cachear respuesta
# Ahorra requests y es más rápido
```

### 2. Fallback a Ollama
```python
# Si Groq falla, intentar con Ollama local
# Ya está implementado en ai_service_groq.py
```

### 3. Optimizar Prompts
```python
# Prompts más cortos = menos tokens = más rápido
# Ya está optimizado en el código
```

### 4. Batch Processing
```python
# Si tienes muchas solicitudes, procesarlas en lotes
# Respeta el límite de 30/min
```

---

## 🎓 Conclusión

### ¿Cuándo Usar Groq?

✅ **USA GROQ SI**:
- Vas a desplegar en Render (plan free)
- Quieres velocidad máxima
- No te importa enviar datos a un tercero
- Quieres 0 configuración de infraestructura

❌ **USA OLLAMA SI**:
- Privacidad es crítica
- Tienes servidor con buena RAM/CPU
- Quieres funcionar offline
- Tienes presupuesto para VPS

### Para tu Proyecto Académico

**Recomendación**:
1. **Desarrollo**: Ollama local (aprendes más)
2. **Demo/Producción**: Groq API (más fácil, gratis)

---

## 📞 Soporte

- **Documentación Groq**: https://console.groq.com/docs
- **Discord Groq**: https://discord.gg/groq
- **Status**: https://status.groq.com/

---

## 🎯 Próximos Pasos

1. ✅ Crear cuenta en Groq
2. ✅ Obtener API key
3. ✅ Configurar `.env` con `USE_GROQ=true`
4. ✅ Reemplazar `ai_service.py` con `ai_service_groq.py`
5. ✅ Probar localmente
6. ✅ Desplegar en Render
7. ✅ Monitorear uso en dashboard

¡Listo! Tu sistema funcionará en producción sin problemas de RAM ni Docker. 🚀
