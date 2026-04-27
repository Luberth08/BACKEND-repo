# 🚀 Guía de Instalación y Uso del Sistema de Diagnóstico con IA

## 📋 Requisitos Previos

### Hardware Mínimo
- **RAM**: 8GB (16GB recomendado)
- **Disco**: 10GB libres
- **CPU**: 4 cores (8 recomendado)
- **GPU**: Opcional (acelera CLIP y Whisper)

### Software
- Python 3.10 o superior
- PostgreSQL 14+ con PostGIS
- Docker y Docker Compose (opcional)
- Git

---

## 🔧 Instalación Local (Sin Docker)

### 1. Instalar Ollama

#### Windows
```bash
# Descargar desde: https://ollama.com/download
# O usar winget:
winget install Ollama.Ollama
```

#### Linux/Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Descargar Modelo LLM
```bash
# Modelo pequeño (3B parámetros, ~2GB)
ollama pull llama3.2:3b

# Alternativas:
# ollama pull llama3.2:1b  # Más rápido, menos preciso
# ollama pull mistral:7b   # Más preciso, más lento
```

### 3. Verificar Ollama
```bash
ollama list
# Debe mostrar: llama3.2:3b

# Probar el modelo
ollama run llama3.2:3b "Hola, ¿cómo estás?"
```

### 4. Configurar Base de Datos
```bash
# Crear base de datos
createdb ASISTENCIA_VEHICULAR

# Habilitar PostGIS
psql ASISTENCIA_VEHICULAR -c "CREATE EXTENSION postgis;"
```

### 5. Instalar Dependencias Python
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 6. Configurar Variables de Entorno
Editar `.env`:
```env
# Base de datos local
DATABASE_URL="postgresql+asyncpg://postgres:106347@localhost:5432/ASISTENCIA_VEHICULAR"
SYNC_DATABASE_URL="postgresql://postgres:106347@localhost:5432/ASISTENCIA_VEHICULAR"

# Ollama local
OLLAMA_HOST=http://localhost:11434

# IA activada
USE_REAL_AI=true
WHISPER_MODEL_SIZE=base
LLM_MODEL_NAME=llama3.2:3b
```

### 7. Ejecutar Migraciones
```bash
alembic upgrade head
```

### 8. Iniciar Servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 9. Verificar Instalación
```bash
# En otro terminal:
curl http://localhost:8000/docs
# Debe abrir Swagger UI
```

---

## 🐳 Instalación con Docker

### 1. Construir y Levantar Servicios
```bash
# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### 2. Esperar a que Ollama Descargue el Modelo
```bash
# Esto puede tomar 5-10 minutos la primera vez
docker-compose logs -f ollama
```

### 3. Verificar Estado
```bash
# Ver servicios corriendo
docker-compose ps

# Probar API
curl http://localhost:8000/docs
```

### 4. Comandos Útiles
```bash
# Detener servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart backend

# Ver logs de un servicio
docker-compose logs -f ollama

# Ejecutar comando en contenedor
docker-compose exec backend bash
```

---

## 🧪 Probar el Sistema

### 1. Crear Usuario y Autenticarse
```bash
# Usar Swagger UI: http://localhost:8000/docs
# O Postman/Insomnia
```

### 2. Crear Solicitud de Diagnóstico

#### Usando cURL
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "descripcion=El motor hace un ruido extraño" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=ABC123" \
  -F "fotos=@foto1.jpg" \
  -F "fotos=@foto2.jpg" \
  -F "audio=@audio.mp3"
```

#### Usando Python
```python
import requests

url = "http://localhost:8000/api/v1/diagnosticos/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {
    "fotos": [
        ("fotos", open("foto1.jpg", "rb")),
        ("fotos", open("foto2.jpg", "rb"))
    ],
    "audio": ("audio", open("audio.mp3", "rb"))
}
data = {
    "descripcion": "El motor hace un ruido extraño",
    "ubicacion": "-17.783333,-63.182222",
    "matricula": "ABC123"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### 3. Ver Resultado
```bash
# Listar mis solicitudes
curl -X GET "http://localhost:8000/api/v1/diagnosticos/mis-solicitudes" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ver detalle de una solicitud
curl -X GET "http://localhost:8000/api/v1/diagnosticos/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Troubleshooting

### Problema: Ollama no responde
```bash
# Verificar que esté corriendo
curl http://localhost:11434/api/tags

# Si no responde, reiniciar
# Sin Docker:
ollama serve

# Con Docker:
docker-compose restart ollama
```

### Problema: Error de memoria con Whisper
```bash
# Usar modelo más pequeño en .env:
WHISPER_MODEL_SIZE=tiny  # o base
```

### Problema: LLM muy lento
```bash
# Opciones:
# 1. Usar modelo más pequeño
LLM_MODEL_NAME=llama3.2:1b

# 2. Reducir temperatura (más rápido, menos creativo)
# En ai_service.py, cambiar temperature a 0.1

# 3. Usar GPU si está disponible
# Ollama detecta GPU automáticamente
```

### Problema: CLIP no encuentra imágenes
```bash
# Verificar rutas en logs
docker-compose logs backend | grep "imagen"

# Verificar que /static esté montado
ls -la static/uploads/diagnosticos/
```

### Problema: Error "concepto no válido"
```bash
# Verificar que existan tipos de incidente en BD
psql ASISTENCIA_VEHICULAR -c "SELECT concepto FROM tipo_incidente;"

# Si está vacío, insertar algunos:
psql ASISTENCIA_VEHICULAR -c "
INSERT INTO tipo_incidente (concepto, prioridad, requiere_remolque) VALUES
('bateria_descargada', 3, false),
('neumatico_pinchado', 2, false),
('motor_sobrecalentado', 4, true),
('falla_electrica', 3, false),
('informacion_insuficiente', 1, false);
"
```

---

## 📊 Monitoreo

### Ver Uso de Recursos
```bash
# Sin Docker:
htop  # o top

# Con Docker:
docker stats
```

### Ver Logs en Tiempo Real
```bash
# Backend
docker-compose logs -f backend

# Ollama
docker-compose logs -f ollama

# Base de datos
docker-compose logs -f db
```

### Métricas de IA
Los logs del backend muestran:
- Tiempo de transcripción de audio
- Tiempo de análisis de imágenes
- Tiempo de generación de diagnóstico
- Confianza de cada predicción

---

## 🚀 Optimizaciones

### Para Desarrollo
```env
# Modelos más rápidos
WHISPER_MODEL_SIZE=tiny
LLM_MODEL_NAME=llama3.2:1b
```

### Para Producción
```env
# Modelos más precisos
WHISPER_MODEL_SIZE=medium
LLM_MODEL_NAME=llama3.2:3b
```

### Con GPU
```bash
# Verificar que CUDA esté disponible
python -c "import torch; print(torch.cuda.is_available())"

# Si es True, los modelos usarán GPU automáticamente
```

---

## 📝 Notas Importantes

1. **Primera ejecución**: La descarga del modelo LLM toma 5-10 minutos
2. **Modelos en caché**: Los modelos se descargan una sola vez
3. **Archivos temporales**: Las imágenes/audios se guardan en `static/uploads/`
4. **Límites**: Máximo 3 fotos y 1 audio por solicitud
5. **Formatos soportados**: 
   - Imágenes: JPG, PNG, WEBP
   - Audio: MP3, WAV, M4A, OGG

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica que Ollama esté corriendo: `curl http://localhost:11434/api/tags`
3. Verifica la base de datos: `psql ASISTENCIA_VEHICULAR -c "\dt"`
4. Revisa el archivo de análisis: `ANALISIS_SISTEMA_DIAGNOSTICO_IA.md`
