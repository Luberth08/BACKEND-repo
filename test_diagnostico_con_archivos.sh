#!/bin/bash

# ============================================================
# TEST SCRIPT: DIAGNÓSTICO CON ARCHIVOS (FOTOS Y AUDIO)
# ============================================================
# Este script crea archivos de prueba y los envía al endpoint
# ============================================================

# Configuración
API_URL="http://localhost:8000/api/v1"
EMAIL="luberthgutierrez@gmail.com"
PASSWORD="106347"
TEMP_DIR="./temp_test_files"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   TEST: DIAGNÓSTICO CON ARCHIVOS                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# PASO 0: CREAR ARCHIVOS DE PRUEBA
# ============================================================
echo "📁 PASO 0: Creando archivos de prueba..."
mkdir -p "$TEMP_DIR"

# Crear imagen de prueba 1 (100x100 píxeles rojo)
convert -size 100x100 xc:red "$TEMP_DIR/foto1.jpg" 2>/dev/null || {
    # Si ImageMagick no está instalado, crear un archivo de texto como placeholder
    echo "Imagen de prueba 1 - Motor" > "$TEMP_DIR/foto1.jpg"
}

# Crear imagen de prueba 2 (100x100 píxeles azul)
convert -size 100x100 xc:blue "$TEMP_DIR/foto2.jpg" 2>/dev/null || {
    echo "Imagen de prueba 2 - Compartimento del motor" > "$TEMP_DIR/foto2.jpg"
}

# Crear audio de prueba (silencio de 1 segundo)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -q:a 9 -acodec libopus "$TEMP_DIR/audio.ogg" -y 2>/dev/null || {
    # Si ffmpeg no está instalado, crear un archivo de texto como placeholder
    echo "Audio de prueba - El motor hace ruido" > "$TEMP_DIR/audio.ogg"
}

if [ -f "$TEMP_DIR/foto1.jpg" ] && [ -f "$TEMP_DIR/foto2.jpg" ] && [ -f "$TEMP_DIR/audio.ogg" ]; then
    echo "✅ Archivos creados:"
    echo "   - $TEMP_DIR/foto1.jpg ($(stat -f%z "$TEMP_DIR/foto1.jpg" 2>/dev/null || stat -c%s "$TEMP_DIR/foto1.jpg" 2>/dev/null || echo "?") bytes)"
    echo "   - $TEMP_DIR/foto2.jpg ($(stat -f%z "$TEMP_DIR/foto2.jpg" 2>/dev/null || stat -c%s "$TEMP_DIR/foto2.jpg" 2>/dev/null || echo "?") bytes)"
    echo "   - $TEMP_DIR/audio.ogg ($(stat -f%z "$TEMP_DIR/audio.ogg" 2>/dev/null || stat -c%s "$TEMP_DIR/audio.ogg" 2>/dev/null || echo "?") bytes)"
else
    echo "❌ Error creando archivos de prueba"
    exit 1
fi
echo ""

# ============================================================
# PASO 1: LOGIN
# ============================================================
echo "📝 PASO 1: Autenticación..."
echo "   Email: $EMAIL"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/web/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Login falló!"
  echo "Respuesta del servidor:"
  echo "$LOGIN_RESPONSE"
  rm -rf "$TEMP_DIR"
  exit 1
fi

echo "✅ Login exitoso!"
echo "   Token: ${TOKEN:0:50}..."
echo ""

# ============================================================
# PASO 2: CREAR SOLICITUD CON ARCHIVOS
# ============================================================
echo "╔════════════════════════════════════════════════════════╗"
echo "║   PASO 2: Crear solicitud con archivos                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📤 Enviando solicitud con archivos..."
echo "   Descripción: El motor hace un ruido extraño"
echo "   Ubicación: -17.783333,-63.182222"
echo "   Archivos: 2 fotos + 1 audio"
echo ""

RESPONSE=$(curl -s -X POST "${API_URL}/diagnosticos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "descripcion=El motor hace un ruido extraño al acelerar, especialmente en subidas. También noto vibraciones en el volante y humo del escape." \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=TEST999" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020" \
  -F "color=Blanco" \
  -F "tipo_vehiculo=sedan" \
  -F "foto1=@${TEMP_DIR}/foto1.jpg" \
  -F "foto2=@${TEMP_DIR}/foto2.jpg" \
  -F "audio=@${TEMP_DIR}/audio.ogg")

echo "📥 Respuesta del servidor:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================
# PASO 3: VERIFICAR RESULTADO
# ============================================================
if echo "$RESPONSE" | grep -q '"id"'; then
  SOLICITUD_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  ESTADO=$(echo "$RESPONSE" | grep -o '"estado":"[^"]*' | cut -d'"' -f4)
  NUM_EVIDENCIAS=$(echo "$RESPONSE" | grep -o '"evidencias":\[' | wc -l)
  
  echo "✅ ¡Solicitud creada exitosamente!"
  echo ""
  echo "📊 RESUMEN:"
  echo "   ID de solicitud: $SOLICITUD_ID"
  echo "   Estado: $ESTADO"
  echo ""
  
  # Contar evidencias
  echo "📎 EVIDENCIAS GUARDADAS:"
  echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    evidencias = data.get('evidencias', [])
    print(f'   Total: {len(evidencias)} evidencias')
    for ev in evidencias:
        tipo = ev.get('tipo')
        url = ev.get('url')
        transcripcion = ev.get('transcripcion', '')
        print(f'   • {tipo.upper()}: {url}')
        if transcripcion:
            print(f'     └─ {transcripcion[:100]}...')
except:
    pass
" 2>/dev/null
  echo ""
  
  if [ "$ESTADO" = "diagnosticada" ]; then
    echo "✅ Diagnóstico completado por IA"
    echo ""
    echo "🔍 DETALLES DEL DIAGNÓSTICO:"
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    diag = data.get('diagnostico', {})
    print(f\"   Descripción: {diag.get('descripcion', 'N/A')[:150]}...\")
    print(f\"   Confianza: {float(diag.get('nivel_confianza', 0)) * 100:.1f}%\")
    print(f\"   Incidentes detectados: {len(diag.get('incidentes', []))}\")
    print()
    print('   📋 INCIDENTES:')
    for inc in diag.get('incidentes', []):
        print(f\"      • {inc.get('concepto')} (confianza: {float(inc.get('nivel_confianza', 0)) * 100:.1f}%)\")
except:
    pass
" 2>/dev/null
  fi
  
  echo ""
  echo "💡 VERIFICAR EN BASE DE DATOS:"
  echo "   SELECT * FROM evidencia WHERE id_solicitud_diagnostico = $SOLICITUD_ID;"
  
else
  echo "❌ ERROR: No se pudo crear la solicitud"
  echo ""
  echo "Detalles del error:"
  echo "$RESPONSE"
fi

# ============================================================
# LIMPIEZA
# ============================================================
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf "$TEMP_DIR"
echo "✅ Archivos temporales eliminados"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   FIN DEL TEST                                         ║"
echo "╚════════════════════════════════════════════════════════╝"
