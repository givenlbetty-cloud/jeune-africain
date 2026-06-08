"""
Social account adapter for reliable OAuth account linking.
"""

from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AutoLinkSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Automatically link OAuth logins to an existing local user with same email.
    This prevents the user from being redirected to the social signup form
    when the account already exists.
    """

    def pre_social_login(self, request, sociallogin):
        # If already linked, default allauth flow continues.
        if sociallogin.is_existing:
            return

        email = None
        if sociallogin.user and sociallogin.user.email:
            email = sociallogin.user.email

        if not email:
            return

        User = get_user_model()
        try:
            existing_user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # Link provider account to existing user and continue login flow.
        sociallogin.connect(request, existing_user)
