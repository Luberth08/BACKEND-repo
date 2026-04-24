#!/bin/bash

# ============================================================
# TEST SCRIPT: DIAGNÓSTICO CON ARCHIVOS REALES
# ============================================================
# Usa los archivos reales del usuario
# ============================================================

# Configuración
API_URL="http://localhost:8000/api/v1"
EMAIL="luberthgutierrez@gmail.com"
PASSWORD="106347"

# Rutas de tus archivos (Windows paths - curl las maneja automáticamente)
FOTO1="C:/Users/Luberth/Downloads/pr1.jpg"
FOTO2="C:/Users/Luberth/Downloads/pr2.jpg"
AUDIO="C:/Users/Luberth/Downloads/audio1.ogg"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   TEST: DIAGNÓSTICO CON ARCHIVOS REALES               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# PASO 0: VERIFICAR ARCHIVOS
# ============================================================
echo "📁 PASO 0: Verificando archivos..."
echo ""

if [ ! -f "$FOTO1" ]; then
    echo "❌ ERROR: No se encuentra $FOTO1"
    exit 1
fi

if [ ! -f "$FOTO2" ]; then
    echo "❌ ERROR: No se encuentra $FOTO2"
    exit 1
fi

if [ ! -f "$AUDIO" ]; then
    echo "❌ ERROR: No se encuentra $AUDIO"
    exit 1
fi

echo "✅ Archivos encontrados:"
echo "   📸 Foto 1: $FOTO1"
echo "   📸 Foto 2: $FOTO2"
echo "   🎵 Audio:  $AUDIO"
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
  exit 1
fi

echo "✅ Login exitoso!"
echo "   Token: ${TOKEN:0:50}..."
echo ""

# ============================================================
# PASO 2: CREAR SOLICITUD CON ARCHIVOS REALES
# ============================================================
echo "╔════════════════════════════════════════════════════════╗"
echo "║   PASO 2: Crear solicitud con archivos reales         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📤 Enviando solicitud con archivos..."
echo "   Descripción: El motor hace un ruido extraño al acelerar"
echo "   Ubicación: -17.783333,-63.182222 (Santa Cruz, Bolivia)"
echo "   Vehículo: Toyota Corolla 2020 (TEST123) - Tipo: auto"
echo "   Archivos: 2 fotos + 1 audio"
echo ""
echo "⏳ Procesando (esto puede tomar 5-10 segundos)..."
echo ""

RESPONSE=$(curl -s -X POST "${API_URL}/diagnosticos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "descripcion=El motor hace un ruido extraño al acelerar, especialmente en subidas. También noto vibraciones en el volante y un poco de humo del escape." \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=TEST123" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020" \
  -F "color=Blanco" \
  -F "tipo_vehiculo=auto" \
  -F "foto1=@${FOTO1}" \
  -F "foto2=@${FOTO2}" \
  -F "audio=@${AUDIO}")

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
  
  echo "✅ ¡Solicitud creada exitosamente!"
  echo ""
  echo "📊 RESUMEN:"
  echo "   ID de solicitud: $SOLICITUD_ID"
  echo "   Estado: $ESTADO"
  echo ""
  
  # Mostrar evidencias
  echo "📎 EVIDENCIAS GUARDADAS:"
  echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    evidencias = data.get('evidencias', [])
    print(f'   Total: {len(evidencias)} evidencias')
    print()
    for idx, ev in enumerate(evidencias, 1):
        tipo = ev.get('tipo', 'desconocido')
        url = ev.get('url', '')
        transcripcion = ev.get('transcripcion', '')
        print(f'   {idx}. {tipo.upper()}')
        print(f'      URL: {url}')
        if transcripcion:
            # Mostrar primeras 150 caracteres
            trans_preview = transcripcion[:150] + ('...' if len(transcripcion) > 150 else '')
            print(f'      Análisis: {trans_preview}')
        print()
except Exception as e:
    print(f'   Error procesando evidencias: {e}')
" 2>/dev/null
  
  if [ "$ESTADO" = "diagnosticada" ]; then
    echo "✅ Diagnóstico completado por IA"
    echo ""
    echo "🔍 DETALLES DEL DIAGNÓSTICO:"
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    diag = data.get('diagnostico', {})
    desc = diag.get('descripcion', 'N/A')
    confianza = float(diag.get('nivel_confianza', 0)) * 100
    incidentes = diag.get('incidentes', [])
    
    print(f'   Descripción: {desc[:200]}...')
    print(f'   Confianza general: {confianza:.1f}%')
    print(f'   Incidentes detectados: {len(incidentes)}')
    print()
    print('   📋 INCIDENTES DETECTADOS POR LA IA:')
    for inc in incidentes:
        concepto = inc.get('concepto', 'desconocido')
        conf = float(inc.get('nivel_confianza', 0)) * 100
        sugerido = inc.get('sugerido_por', 'ia')
        print(f'      • {concepto}')
        print(f'        └─ Confianza: {conf:.1f}% (sugerido por: {sugerido})')
except Exception as e:
    print(f'   Error procesando diagnóstico: {e}')
" 2>/dev/null
    
    echo ""
    echo "🗂️  ARCHIVOS GUARDADOS EN:"
    echo "   BACKEND-repo/static/uploads/diagnosticos/"
    echo ""
    echo "💡 VERIFICAR EN BASE DE DATOS:"
    echo "   SELECT * FROM evidencia WHERE id_solicitud_diagnostico = $SOLICITUD_ID;"
    echo "   SELECT * FROM diagnostico WHERE id_solicitud_diagnostico = $SOLICITUD_ID;"
    echo "   SELECT i.*, ti.concepto FROM incidente i"
    echo "   JOIN tipo_incidente ti ON i.id_tipo_incidente = ti.id"
    echo "   WHERE i.id_diagnostico = (SELECT id FROM diagnostico WHERE id_solicitud_diagnostico = $SOLICITUD_ID);"
    
  elif [ "$ESTADO" = "error" ]; then
    echo "❌ Error durante el procesamiento de IA"
    echo ""
    echo "💡 Posibles causas:"
    echo "   1. GROQ_API_KEY no configurada o inválida"
    echo "   2. No hay tipos de incidente en la base de datos"
    echo "   3. Error en los modelos de IA (Whisper/CLIP)"
    echo ""
    echo "🔄 Puedes reintentar con:"
    echo "   curl -X POST \"${API_URL}/diagnosticos/${SOLICITUD_ID}/reintentar\" \\"
    echo "        -H \"Authorization: Bearer ${TOKEN}\""
  elif [ "$ESTADO" = "pendiente" ]; then
    echo "⏳ Solicitud en estado pendiente (procesamiento en curso)"
    echo ""
    echo "💡 Espera unos segundos y consulta el estado:"
    echo "   curl -X GET \"${API_URL}/diagnosticos/${SOLICITUD_ID}\" \\"
    echo "        -H \"Authorization: Bearer ${TOKEN}\""
  fi
  
else
  echo "❌ ERROR: No se pudo crear la solicitud"
  echo ""
  echo "Detalles del error:"
  echo "$RESPONSE"
  echo ""
  
  # Verificar errores comunes
  if echo "$RESPONSE" | grep -q "GROQ_API_KEY"; then
    echo "💡 SOLUCIÓN: Configura tu GROQ_API_KEY en el archivo .env"
    echo "   1. Obtén tu key en: https://console.groq.com/keys"
    echo "   2. Edita BACKEND-repo/.env"
    echo "   3. Agrega: GROQ_API_KEY=gsk_tu_key_aqui"
    echo "   4. Reinicia el backend"
  fi
  
  if echo "$RESPONSE" | grep -q "Authorization"; then
    echo "💡 SOLUCIÓN: Problema de autenticación"
    echo "   Verifica que el token sea válido"
  fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   FIN DEL TEST                                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📝 NOTA: Los archivos originales NO se modifican."
echo "   Se copian a: BACKEND-repo/static/uploads/diagnosticos/"
