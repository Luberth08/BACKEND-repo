# 🧪 CÓMO PROBAR EL ENDPOINT DE DIAGNÓSTICO

## 📋 REQUISITOS PREVIOS

1. **Backend corriendo:**
   ```bash
   cd BACKEND-repo
   source venv/bin/activate  # o venv\Scripts\activate en Windows
   uvicorn app.main:app --reload
   ```

2. **Base de datos con datos:**
   - Al menos 1 usuario registrado
   - Tabla `tipo_incidente` con conceptos (ej: falla_motor, fuga_aceite, etc.)

3. **GROQ_API_KEY configurada:**
   - Archivo `.env` debe tener: `GROQ_API_KEY=gsk_tu_key_aqui`
   - Obtén tu key en: https://console.groq.com/keys

---

## 🚀 MÉTODO 1: SCRIPT BASH (RECOMENDADO)

### Paso 1: Dar permisos de ejecución
```bash
cd BACKEND-repo
chmod +x test_diagnostico.sh
```

### Paso 2: Ejecutar
```bash
bash test_diagnostico.sh
```

### Paso 3: Ver resultado
El script mostrará:
- ✅ Login exitoso
- 📤 Solicitud enviada
- 📥 Respuesta del servidor
- 📊 Resumen del diagnóstico
- 🔍 Incidentes detectados
- 📎 Evidencias guardadas

---

## 🌐 MÉTODO 2: CURL MANUAL

### Paso 1: Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/web/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"luberthgutierrez@gmail.com","password":"123456"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Paso 2: Copiar el token
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Paso 3: Crear solicitud (sin archivos)
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=El motor hace un ruido extraño al acelerar" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=ABC123" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020"
```

### Paso 4: Crear solicitud (con archivos)
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=El motor hace un ruido extraño" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=ABC123" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020" \
  -F "foto1=@/ruta/a/imagen1.jpg" \
  -F "foto2=@/ruta/a/imagen2.jpg" \
  -F "audio=@/ruta/a/audio.ogg"
```

---

## 📱 MÉTODO 3: POSTMAN

### Configuración:
1. **Método:** POST
2. **URL:** `http://localhost:8000/api/v1/diagnosticos/`
3. **Headers:**
   - `Authorization: Bearer {tu_token}`
4. **Body:** form-data
   - `descripcion` (text): "El motor hace un ruido extraño"
   - `ubicacion` (text): "-17.783333,-63.182222"
   - `matricula` (text): "ABC123"
   - `marca` (text): "Toyota"
   - `modelo` (text): "Corolla"
   - `anio` (text): "2020"
   - `foto1` (file): seleccionar imagen
   - `foto2` (file): seleccionar imagen
   - `audio` (file): seleccionar audio

---

## 🔍 VERIFICAR RESULTADOS

### 1. Revisar respuesta JSON
```json
{
  "id": 1,
  "descripcion": "El motor hace un ruido extraño",
  "fecha": "2026-04-24T09:45:30.123Z",
  "estado": "diagnosticada",  // ← Debe ser "diagnosticada"
  "ubicacion": "-17.783333,-63.182222",
  "evidencias": [
    {
      "tipo": "imagen",
      "url": "/static/uploads/diagnosticos/abc123.jpg",
      "transcripcion": "CLIP Analysis: falla_motor (confianza: 85.00%)"
    },
    {
      "tipo": "audio",
      "url": "/static/uploads/diagnosticos/def456.ogg",
      "transcripcion": "El motor hace un ruido extraño cuando acelero"
    }
  ],
  "diagnostico": {
    "descripcion": "Basado en el análisis...",
    "nivel_confianza": 0.82,
    "incidentes": [
      {
        "concepto": "falla_motor",
        "nivel_confianza": 0.85,
        "sugerido_por": "ia"
      }
    ]
  }
}
```

### 2. Verificar archivos guardados
```bash
ls -la BACKEND-repo/static/uploads/diagnosticos/
```

### 3. Verificar en base de datos
```sql
-- Ver solicitud
SELECT * FROM solicitud_diagnostico WHERE id = 1;

-- Ver evidencias
SELECT * FROM evidencia WHERE id_solicitud_diagnostico = 1;

-- Ver diagnóstico
SELECT * FROM diagnostico WHERE id_solicitud_diagnostico = 1;

-- Ver incidentes
SELECT i.*, ti.concepto 
FROM incidente i 
JOIN tipo_incidente ti ON i.id_tipo_incidente = ti.id
WHERE i.id_diagnostico = 1;
```

---

## ❌ ERRORES COMUNES

### Error 1: "GROQ_API_KEY no configurada"
**Causa:** Falta la API key en `.env`

**Solución:**
```bash
# Editar .env
nano BACKEND-repo/.env

# Agregar:
GROQ_API_KEY=gsk_tu_key_aqui

# Reiniciar backend
```

### Error 2: "Field required: Authorization"
**Causa:** No se envió el token

**Solución:**
```bash
# Asegúrate de incluir el header:
-H "Authorization: Bearer {tu_token}"
```

### Error 3: Estado "error" en la respuesta
**Causa:** Error durante el procesamiento de IA

**Solución:**
```bash
# Ver logs del backend para más detalles
# Reintentar procesamiento:
curl -X POST "http://localhost:8000/api/v1/diagnosticos/1/reintentar" \
  -H "Authorization: Bearer $TOKEN"
```

### Error 4: "No se encontró TipoIncidente con concepto 'X'"
**Causa:** La IA sugirió un concepto que no existe en la BD

**Solución:**
```sql
-- Agregar conceptos faltantes:
INSERT INTO tipo_incidente (concepto, prioridad, requiere_remolque)
VALUES 
  ('falla_motor', 3, false),
  ('fuga_aceite', 2, false),
  ('problema_frenos', 4, true),
  ('bateria_descargada', 1, false);
```

---

## 📊 CONCEPTOS RECOMENDADOS

Para que la IA funcione bien, asegúrate de tener estos conceptos en `tipo_incidente`:

```sql
INSERT INTO tipo_incidente (concepto, prioridad, requiere_remolque) VALUES
('falla_motor', 4, true),
('fuga_aceite', 3, false),
('problema_frenos', 5, true),
('bateria_descargada', 2, false),
('neumatico_pinchado', 2, false),
('problema_transmision', 4, true),
('sobrecalentamiento', 3, true),
('problema_escape', 2, false),
('falla_electrica', 3, false),
('problema_suspension', 3, false),
('fuga_refrigerante', 3, true),
('problema_direccion', 4, true),
('desconocido', 1, false),
('informacion_insuficiente', 1, false);
```

---

## 🎯 CASOS DE PRUEBA

### Caso 1: Solo descripción (sin archivos)
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=El motor no arranca" \
  -F "ubicacion=-17.783333,-63.182222"
```

### Caso 2: Con vehículo nuevo
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=Ruido en los frenos" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=XYZ789" \
  -F "marca=Honda" \
  -F "modelo=Civic" \
  -F "anio=2019"
```

### Caso 3: Con fotos y audio
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosticos/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "descripcion=Fuga de líquido" \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "foto1=@imagen1.jpg" \
  -F "foto2=@imagen2.jpg" \
  -F "audio=@audio.ogg"
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **Flujo completo:** Ver `FLUJO_DIAGNOSTICO_IA.md`
- **Configuración GROQ:** Ver `GUIA_GROQ_API.md`
- **Instalación IA:** Ver `GUIA_INSTALACION_IA.md`
