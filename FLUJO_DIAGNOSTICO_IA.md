# 🚗 FLUJO COMPLETO: DIAGNÓSTICO VEHICULAR CON IA

## 📋 RESUMEN
Sistema de diagnóstico automático que usa 3 IAs para analizar problemas vehiculares:
- **Whisper** (transcripción de audio)
- **CLIP** (análisis de imágenes)
- **GROQ/Llama** (diagnóstico final)

---

## 🔄 FLUJO PASO A PASO

### 1️⃣ RECEPCIÓN DE SOLICITUD
**Endpoint:** `POST /api/v1/diagnosticos/`

**Datos recibidos:**
- `descripcion` (requerido): Texto del conductor describiendo el problema
- `ubicacion` (requerido): Coordenadas "lat,lon" (ej: "-17.783333,-63.182222")
- `matricula` (opcional): Matrícula del vehículo
- `marca, modelo, anio, color, tipo_vehiculo` (opcional): Datos del vehículo
- `foto1, foto2, foto3` (opcional): Hasta 3 imágenes del problema
- `audio` (opcional): Grabación de audio describiendo el problema

**Autenticación:** Bearer token (JWT)

---

### 2️⃣ PROCESAMIENTO INICIAL

#### A. Validación de ubicación
```python
lat, lon = map(float, ubicacion_str.split(","))
point = Point(lon, lat)  # PostGIS Geography
```

#### B. Gestión de vehículo
- Si existe `matricula` → buscar en BD
- Si no existe → crear nuevo vehículo con los datos proporcionados
- Asociar vehículo a la persona actual

#### C. Crear solicitud
```sql
INSERT INTO solicitud_diagnostico (
    descripcion, ubicacion, id_persona, id_vehiculo, estado
) VALUES (
    'El motor hace ruido...', POINT(-63.18, -17.78), 25, 1, 'pendiente'
);
```

---

### 3️⃣ GUARDADO DE EVIDENCIAS

#### A. Guardar archivos físicos
**Ubicación:** `static/uploads/diagnosticos/`
**Nombre:** UUID aleatorio + extensión original

```
static/uploads/diagnosticos/
├── a3f2b1c4d5e6.jpg  (foto1)
├── b7c8d9e0f1a2.jpg  (foto2)
└── c3d4e5f6a7b8.ogg  (audio)
```

#### B. Registrar en tabla `evidencia`

**Para imágenes (inicial):**
```sql
INSERT INTO evidencia (url, tipo, id_solicitud_diagnostico, transcripcion)
VALUES ('/static/uploads/diagnosticos/a3f2b1c4d5e6.jpg', 'imagen', 1, NULL);
```

**Para audio:**
```sql
INSERT INTO evidencia (url, tipo, id_solicitud_diagnostico, transcripcion)
VALUES ('/static/uploads/diagnosticos/c3d4e5f6a7b8.ogg', 'audio', 1, 'El motor hace un ruido...');
```

---

### 4️⃣ ANÁLISIS CON IA

#### A. Obtener conceptos válidos
```sql
SELECT concepto FROM tipo_incidente;
-- Resultado: ['falla_motor', 'fuga_aceite', 'problema_frenos', ...]
```

#### B. Transcripción de audio (Whisper)
```python
transcripcion = await ai_service.transcribe_audio(audio_path)
# Resultado: "El motor hace un ruido extraño cuando acelero en subida"
```
✅ **Se guarda en:** `evidencia.transcripcion` (tipo='audio')

#### C. Análisis de imágenes (CLIP)
```python
image_analysis = await ai_service.analyze_multiple_images(
    image_paths=['./static/.../foto1.jpg', './static/.../foto2.jpg'],
    candidate_labels=['falla_motor', 'fuga_aceite', 'problema_frenos', ...]
)
# Resultado: [
#   {'falla_motor': 0.85, 'fuga_aceite': 0.10, 'problema_frenos': 0.05},
#   {'falla_motor': 0.78, 'fuga_aceite': 0.15, 'problema_frenos': 0.07}
# ]
```

**Formato del análisis guardado:**
```
CLIP Analysis: falla_motor (confianza: 85.00%) | Top 3: falla_motor: 85.00%, fuga_aceite: 10.00%, problema_frenos: 5.00%
```
✅ **Se guarda en:** `evidencia.transcripcion` (tipo='imagen')

---

### 5️⃣ DIAGNÓSTICO FINAL (GROQ/Llama)

#### A. Construcción del prompt
```
Eres un experto mecánico automotriz. Genera un diagnóstico en JSON.

### CONCEPTOS VÁLIDOS (solo usa estos nombres exactos):
falla_motor, fuga_aceite, problema_frenos, bateria_descargada, ...

### INFORMACIÓN DEL VEHÍCULO ###
- Matrícula: ABC123
- Marca/Modelo: Toyota Corolla
- Año: 2020

### DESCRIPCIÓN DEL CONDUCTOR ###
El motor hace un ruido extraño al acelerar

### TRANSCRIPCIÓN DE AUDIO ###
El motor hace un ruido extraño cuando acelero en subida

### ANÁLISIS DE IMÁGENES (CLIP) ###
- Imagen 1: falla_motor (confianza 85.00%)
- Imagen 2: falla_motor (confianza 78.00%)

### INSTRUCCIONES ###
Genera ÚNICAMENTE un JSON válido con esta estructura:
{
    "descripcion": "texto explicativo en español del diagnóstico",
    "nivel_confianza": 0.85,
    "incidentes": [
        {"concepto": "falla_motor", "nivel_confianza": 0.9, "sugerido_por": "ia"},
        {"concepto": "problema_escape", "nivel_confianza": 0.7, "sugerido_por": "ia"}
    ]
}
```

#### B. Respuesta de GROQ
```json
{
    "descripcion": "Basado en el análisis de las imágenes y la descripción, se detecta una posible falla en el sistema de escape o motor. El ruido al acelerar sugiere un problema en el tubo de escape o en los componentes internos del motor.",
    "nivel_confianza": 0.82,
    "incidentes": [
        {"concepto": "falla_motor", "nivel_confianza": 0.85, "sugerido_por": "ia"},
        {"concepto": "problema_escape", "nivel_confianza": 0.78, "sugerido_por": "ia"}
    ]
}
```

---

### 6️⃣ PERSISTENCIA EN BASE DE DATOS

#### A. Crear diagnóstico
```sql
INSERT INTO diagnostico (
    descripcion, nivel_confianza, id_solicitud_diagnostico
) VALUES (
    'Basado en el análisis...', 0.82, 1
);
-- Retorna: id_diagnostico = 1
```

#### B. Crear incidentes
Para cada incidente en la respuesta de GROQ:

1. Buscar `tipo_incidente` por concepto exacto:
```sql
SELECT id FROM tipo_incidente WHERE concepto = 'falla_motor';
-- Retorna: id_tipo_incidente = 5
```

2. Insertar en tabla `incidente`:
```sql
INSERT INTO incidente (
    id_diagnostico, id_tipo_incidente, sugerido_por, nivel_confianza
) VALUES (
    1, 5, 'ia', 0.85
);

INSERT INTO incidente (
    id_diagnostico, id_tipo_incidente, sugerido_por, nivel_confianza
) VALUES (
    1, 8, 'ia', 0.78
);
```

#### C. Actualizar estado de solicitud
```sql
UPDATE solicitud_diagnostico 
SET estado = 'diagnosticada' 
WHERE id = 1;
```

---

### 7️⃣ RESPUESTA AL CLIENTE

```json
{
    "id": 1,
    "descripcion": "El motor hace un ruido extraño al acelerar",
    "fecha": "2026-04-24T09:45:30.123Z",
    "estado": "diagnosticada",
    "ubicacion": "-17.783333,-63.182222",
    "id_vehiculo": 1,
    "evidencias": [
        {
            "id": 1,
            "url": "/static/uploads/diagnosticos/a3f2b1c4d5e6.jpg",
            "tipo": "imagen",
            "transcripcion": "CLIP Analysis: falla_motor (confianza: 85.00%) | Top 3: falla_motor: 85.00%, fuga_aceite: 10.00%, problema_frenos: 5.00%"
        },
        {
            "id": 2,
            "url": "/static/uploads/diagnosticos/b7c8d9e0f1a2.jpg",
            "tipo": "imagen",
            "transcripcion": "CLIP Analysis: falla_motor (confianza: 78.00%) | Top 3: falla_motor: 78.00%, fuga_aceite: 15.00%, problema_frenos: 7.00%"
        },
        {
            "id": 3,
            "url": "/static/uploads/diagnosticos/c3d4e5f6a7b8.ogg",
            "tipo": "audio",
            "transcripcion": "El motor hace un ruido extraño cuando acelero en subida"
        }
    ],
    "diagnostico": {
        "id": 1,
        "descripcion": "Basado en el análisis de las imágenes y la descripción, se detecta una posible falla en el sistema de escape o motor...",
        "nivel_confianza": 0.82,
        "fecha": "2026-04-24T09:45:31.456Z",
        "incidentes": [
            {
                "id_tipo_incidente": 5,
                "concepto": "falla_motor",
                "nivel_confianza": 0.85,
                "sugerido_por": "ia"
            },
            {
                "id_tipo_incidente": 8,
                "concepto": "problema_escape",
                "nivel_confianza": 0.78,
                "sugerido_por": "ia"
            }
        ]
    }
}
```

---

## 🔧 MANEJO DE ERRORES

### Si falla la IA:
```sql
UPDATE solicitud_diagnostico 
SET estado = 'error' 
WHERE id = 1;
```

### Reintentar procesamiento:
```bash
POST /api/v1/diagnosticos/1/reintentar
```
- Reutiliza evidencias ya guardadas
- Vuelve a ejecutar análisis CLIP y GROQ
- Reemplaza diagnóstico anterior

---

## 📊 TABLAS INVOLUCRADAS

```
solicitud_diagnostico (estado: pendiente → diagnosticada)
    ├── evidencia (tipo: imagen/audio, transcripcion: análisis)
    ├── vehiculo (opcional)
    └── diagnostico
            └── incidente (N incidentes)
                    └── tipo_incidente (conceptos predefinidos)
```

---

## ✅ VALIDACIONES IMPORTANTES

1. **GROQ solo puede elegir conceptos existentes** en `tipo_incidente.concepto`
2. **Máximo 3 fotos** por solicitud
3. **Audio opcional** pero recomendado para mejor diagnóstico
4. **Nivel de confianza** entre 0.0 y 1.0
5. **Si un concepto no existe** en BD, se omite (no se crea automáticamente)

---

## 🧪 CÓMO PROBAR

Ver archivo: `test_diagnostico.sh`

```bash
cd BACKEND-repo
bash test_diagnostico.sh
```
