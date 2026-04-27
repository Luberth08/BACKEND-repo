#!/bin/bash

# ============================================================
# TEST SCRIPT: DIAGNÓSTICO VEHICULAR CON IA
# ============================================================
# Este script prueba el endpoint POST /api/v1/diagnosticos/
# sin necesidad de usar Swagger UI
#
# Requisitos:
# - Backend corriendo en http://localhost:8000
# - Usuario registrado con email y password
# - curl instalado
# ============================================================

# Configuración
API_URL="http://localhost:8000/api/v1"
EMAIL="luberthgutierrez@gmail.com"
PASSWORD="106347"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   TEST: DIAGNÓSTICO VEHICULAR CON IA                  ║"
echo "╚════════════════════════════════════════════════════════╝"
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
  echo ""
  echo "Verifica que:"
  echo "  1. El backend esté corriendo (http://localhost:8000)"
  echo "  2. El email y password sean correctos"
  echo "  3. El usuario exista en la base de datos"
  exit 1
fi

echo "✅ Login exitoso!"
echo "   Token: ${TOKEN:0:50}..."
echo ""

# ============================================================
# PASO 2: CREAR SOLICITUD DE DIAGNÓSTICO
# ============================================================
echo "╔════════════════════════════════════════════════════════╗"
echo "║   PASO 2: Crear solicitud de diagnóstico              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📤 Enviando solicitud..."
echo "   Descripción: El motor hace un ruido extraño al acelerar"
echo "   Ubicación: -17.783333,-63.182222 (Santa Cruz, Bolivia)"
echo "   Vehículo: Toyota Corolla 2020 (ABC123)"
echo ""

RESPONSE=$(curl -s -X POST "${API_URL}/diagnosticos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "descripcion=El motor hace un ruido extraño al acelerar, especialmente en subidas. También noto vibraciones en el volante." \
  -F "ubicacion=-17.783333,-63.182222" \
  -F "matricula=ABC123" \
  -F "marca=Toyota" \
  -F "modelo=Corolla" \
  -F "anio=2020" \
  -F "color=Blanco" \
  -F "tipo_vehiculo=sedan")

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
  
  if [ "$ESTADO" = "diagnosticada" ]; then
    echo "✅ Diagnóstico completado por IA"
    echo ""
    echo "🔍 DETALLES DEL DIAGNÓSTICO:"
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    diag = data.get('diagnostico', {})
    print(f\"   Descripción: {diag.get('descripcion', 'N/A')[:100]}...\")
    print(f\"   Confianza: {float(diag.get('nivel_confianza', 0)) * 100:.1f}%\")
    print(f\"   Incidentes detectados: {len(diag.get('incidentes', []))}\")
    print()
    print('   📋 INCIDENTES:')
    for inc in diag.get('incidentes', []):
        print(f\"      • {inc.get('concepto')} (confianza: {float(inc.get('nivel_confianza', 0)) * 100:.1f}%)\")
    print()
    print('   📎 EVIDENCIAS:')
    for ev in data.get('evidencias', []):
        print(f\"      • {ev.get('tipo')}: {ev.get('url')}\")
        if ev.get('transcripcion'):
            print(f\"        └─ {ev.get('transcripcion')[:80]}...\")
except:
    pass
" 2>/dev/null
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
