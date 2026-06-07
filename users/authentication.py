from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PhoneBackend(ModelBackend):
    """
    Authentification via Numéro de téléphone + OTP (simulé ou réel).
    """
    def authenticate(self, request, phone=None, otp=None, **kwargs):
        if phone is None or otp is None:
            return None
        
        try:
            user = User.objects.get(phone=phone)

            # Défense en profondeur: OTP téléphone interdit pour comptes sensibles.
            if user.is_staff or user.is_superuser or getattr(user, "role", None) in {"super_admin", "library_admin"}:
                return None

            if not user.is_active:
                return None

            if user.otp_attempts >= 5:
                return None

            if not user.otp_code or not user.otp_created_at:
                return None

            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                user.otp_code = None
                user.save(update_fields=["otp_code"])
                return None

            if user.otp_code == otp:
                user.otp_code = None
                user.otp_attempts = 0
                user.is_phone_verified = True
                user.save(update_fields=["otp_code", "otp_attempts", "is_phone_verified"])
                return user

            user.otp_attempts += 1
            user.save(update_fields=["otp_attempts"])
            return None
        except User.DoesNotExist:
            return None
