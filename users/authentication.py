from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneBackend(ModelBackend):
    """
    Authentification via Numéro de téléphone + OTP (simulé ou réel).
    """
    def authenticate(self, request, phone=None, otp=None, **kwargs):
        if phone is None:
            return None
        
        try:
            user = User.objects.get(phone=phone)
            # Vérification OTP
            # Dans un cas réel, on vérifierait user.otp_code == otp et expiration
            # Pour l'instant, on accepte si l'OTP correspond au code stocké
            if user.otp_code and user.otp_code == otp:
                 # Optionnel: vérifier expiration (otp_created_at)
                return user
            return None
        except User.DoesNotExist:
            return None
