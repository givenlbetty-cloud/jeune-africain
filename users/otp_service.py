import random
import logging
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Génère un code OTP numérique."""
    digits = "0123456789"
    return "".join(random.choice(digits) for _ in range(length))

def send_otp_via_whatsapp(phone, otp_code):
    """
    Simule l'envoi d'un OTP via WhatsApp.
    À connecter plus tard à l'API Meta/Twilio.
    """
    message = f"Votre code de connexion BNC est : {otp_code}"
    
    # En Dev, on affiche juste dans la console
    logger.info(f"🔑 [WHATSAPP MOCK] To: {phone} | Msg: {message}")
    print(f"🔑 [WHATSAPP MOCK] To: {phone} | Msg: {message}")
    
    return True
