import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# Almacenamiento en memoria: email -> {"code": str, "expires_at": datetime, "temp_data": dict}
_otp_storage: Dict[str, dict] = {}

def generate_otp() -> str:
    """Genera un código OTP de 6 dígitos."""
    return f"{random.randint(100000, 999999)}"

def store_otp(
    email: str,
    otp: str,
    expires_minutes: int = 10,
    temp_data: Optional[dict] = None
) -> None:
    """
    Almacena un OTP con su fecha de expiración y datos temporales asociados.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    _otp_storage[email] = {
        "code": otp,
        "expires_at": expires_at,
        "temp_data": temp_data or {}
    }

def get_otp_data(email: str) -> Optional[dict]:
    """
    Recupera los datos del OTP sin eliminarlos.
    Si el OTP ha expirado, lo elimina y retorna None.
    """
    record = _otp_storage.get(email)
    if not record:
        return None
    if datetime.now(timezone.utc) > record["expires_at"]:
        delete_otp(email)
        return None
    return record

def verify_otp(email: str, code: str) -> bool:
    """
    Verifica si el código OTP es correcto (sin eliminar el registro).
    Útil para primero obtener los datos temporales y luego eliminarlos manualmente.
    """
    record = get_otp_data(email)
    if not record or record["code"] != code:
        return False
    return True

def delete_otp(email: str) -> None:
    """Elimina el OTP del almacenamiento."""
    _otp_storage.pop(email, None)

def send_otp_sms(email: str, otp: str) -> None:
    """
    Envía el OTP por SMS (simulado).
    En producción, reemplazar con integración real (Twilio, AWS SNS, etc.).
    """
    print(f"[MOCK SMS] Enviando OTP {otp} a {email}")
    # Aquí iría la llamada a la API de SMS real

def send_otp_email(email: str, otp: str) -> None:
    """
    Envía el OTP por correo electrónico usando SMTP.
    """
    subject = "Tu código de verificación"
    body = f"""
    <h2>Hola,</h2>
    <p>Tu código de verificación es: <strong>{otp}</strong></p>
    <p>Este código expira en 10 minutos.</p>
    <p>Si no solicitaste este código, ignora este mensaje.</p>
    """
    
    # Crear mensaje
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        # Conectar al servidor SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Habilitar TLS
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] OTP enviado a {email}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el email a {email}: {e}")
        # Opcional: relanzar la excepción o manejarla

async def send_otp_email_safe(email: str, action: str, expires_minutes: int = 10) -> str:
    """
    Genera un OTP, lo envía por email y lo guarda en memoria con la acción especificada.
    """
    otp = generate_otp()
    store_otp(email, otp, expires_minutes=expires_minutes, temp_data={"action": action})
    send_otp_email(email, otp)
    return otp
