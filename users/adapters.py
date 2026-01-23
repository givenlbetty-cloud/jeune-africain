"""
Custom adapters for django-allauth social account integration.
Handles user profile population from OAuth providers (Google, Apple, Microsoft).
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging
import requests

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to populate user profile from social account data.
    Automatically extracts name, email, and profile picture from OAuth provider.
    Supports: Google, Apple, Microsoft
    """

    def get_app(self, request, provider, client_id=None):
        """
        Custom get_app to handle both DB-configured apps and settings-configured apps.
        Fallback to settings if DB query fails or recurses.
        """
        from django.conf import settings
        from allauth.socialaccount.models import SocialApp
        
        # 1. First, try to fetch from settings since that's what we want to prioritize/ensure exists
        # This avoids the DB recursion issue entirely for providers configured in settings.
        try:
            provider_config = settings.SOCIALACCOUNT_PROVIDERS.get(provider)
            if provider_config and 'APP' in provider_config:
                app_config = provider_config['APP']
                # Create an in-memory SocialApp instance
                return SocialApp(
                    provider=provider,
                    name=provider.capitalize(),
                    client_id=app_config.get('client_id'),
                    secret=app_config.get('secret'),
                    key=app_config.get('key', '')
                )
        except Exception as e:
            logger.warning(f"Failed to load {provider} app from settings: {e}")

        # 2. If not in settings, try the default behavior (DB)
        try:
            return super().get_app(request, provider, client_id)
        except Exception:
            # If everything fails, return None (which might raise missing: app upstream, but avoids crash loop)
            return None

    def populate_user(self, request, sociallogin):
        """
        Override to populate user fields from social account data.
        
        Args:
            request: HTTP request
            sociallogin: SocialLogin instance with provider data
            
        Returns:
            CustomUser instance with populated fields
        """
        user = super().populate_user(request, sociallogin)
        
        # Extract data from social account
        extra_data = sociallogin.account.extra_data
        provider = sociallogin.account.provider
        
        # Set email
        if not user.email and 'email' in extra_data:
            user.email = extra_data['email']
        
        # Provider-specific field mapping
        if provider == 'google':
            self._populate_from_google(user, extra_data)
        elif provider == 'apple':
            self._populate_from_apple(user, extra_data)
        elif provider == 'microsoft':
            self._populate_from_microsoft(user, extra_data)
        
        return user
    
    def _populate_from_google(self, user, extra_data):
        """Handle Google-specific field mapping."""
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        # Fallback to 'name' field if given_name not available
        if not user.first_name and 'name' in extra_data:
            name_parts = extra_data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
    
    def _populate_from_apple(self, user, extra_data):
        """Handle Apple-specific field mapping."""
        # Apple may not provide name on first login
        # Name is provided in the id_token claims
        
        if 'name' in extra_data:
            # Apple provides full name in 'name' field
            name_parts = extra_data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
        
        # Apple may provide separate given_name and family_name
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        logger.info(f"Apple OAuth user: {user.email} ({user.first_name} {user.last_name})")
    
    def _populate_from_microsoft(self, user, extra_data):
        """Handle Microsoft/Azure AD-specific field mapping."""
        # Microsoft uses 'given_name' and 'family_name'
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        # Fallback to 'displayName' if available
        if not user.first_name and 'displayName' in extra_data:
            name_parts = extra_data['displayName'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
        
        logger.info(f"Microsoft OAuth user: {user.email} ({user.first_name} {user.last_name})")
    
    def save_user(self, request, sociallogin):
        """
        Override to handle additional user profile data.
        """
        user = super().save_user(request, sociallogin)
        
        # Download and save profile picture if available
        self._download_and_save_profile_picture(user, sociallogin)
        
        return user
    
    def _download_and_save_profile_picture(self, user, sociallogin):
        """
        Download profile picture from OAuth provider and save to user.
        
        Args:
            user: CustomUser instance
            sociallogin: SocialLogin instance
        """
        from django.core.files.base import ContentFile
        extra_data = sociallogin.account.extra_data
        provider = sociallogin.account.provider
        
        # Check for picture URL in different provider formats
        picture_url = None
        
        if provider == 'google':
            picture_url = extra_data.get('picture')  # Google uses 'picture'
        
        elif provider == 'apple':
            # Apple doesn't provide picture in OAuth response
            # Users must set it manually
            picture_url = None
        
        elif provider == 'microsoft':
            # Microsoft doesn't provide picture URL in token response
            # Would need separate API call to Microsoft Graph
            picture_url = None
        
        if picture_url:
            try:
                # Download the image
                response = requests.get(picture_url, timeout=5)
                if response.status_code == 200:
                    # Extract filename from URL
                    filename = f"avatar_{user.id}_{provider}_oauth.jpg"
                    
                    # Save to user avatar
                    user.avatar.save(
                        filename,
                        ContentFile(response.content),
                        save=True
                    )
                    logger.info(f"Avatar saved for user {user.id} from {provider}")
            except Exception as e:
                # Silently fail - avatar is optional
                logger.warning(f"Failed to download avatar from {provider}: {e}")
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully logs in via a social provider.
        Useful for additional validation or data syncing.
        """
        provider = sociallogin.account.provider
        email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else None
        
        logger.info(f"Pre-social-login hook: provider={provider}, email={email}")
        
        # You can add custom logic here:
        # - Sync user data with external systems
        # - Validate user before allowing login
        # - Map custom user fields
        pass



# OAuth Provider Adapter Classes
class GoogleOAuth2Adapter:
    """
    Helper class for Google OAuth2 configuration.
    """
    
    @staticmethod
    def get_authorization_url():
        """Get Google authorization URL."""
        return "https://accounts.google.com/o/oauth2/v2/auth"
    
    @staticmethod
    def get_token_url():
        """Get Google token URL."""
        return "https://www.googleapis.com/oauth2/v4/token"
    
    @staticmethod
    def get_profile_url():
        """Get Google profile URL."""
        return "https://www.googleapis.com/oauth2/v1/userinfo"


class AppleOAuth2Adapter:
    """
    Helper class for Apple Sign In configuration.
    """
    
    @staticmethod
    def get_authorization_url():
        """Get Apple authorization URL."""
        return "https://appleid.apple.com/auth/authorize"
    
    @staticmethod
    def get_token_url():
        """Get Apple token URL."""
        return "https://appleid.apple.com/auth/token"
    
    @staticmethod
    def get_profile_url():
        """Get Apple user info from token (no separate endpoint)."""
        return None  # Apple provides info in the ID token


class MicrosoftOAuth2Adapter:
    """
    Helper class for Microsoft OAuth2 configuration.
    """
    
    @staticmethod
    def get_authorization_url(tenant='common'):
        """Get Microsoft authorization URL."""
        return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
    
    @staticmethod
    def get_token_url(tenant='common'):
        """Get Microsoft token URL."""
        return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    
    @staticmethod
    def get_profile_url():
        """Get Microsoft profile URL (Microsoft Graph)."""
        return "https://graph.microsoft.com/v1.0/me"
