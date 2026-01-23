# 🔐 Google OAuth Configuration Guide

**Status**: ✅ Implementation Complete  
**Date**: December 21, 2025  
**Version**: 1.0.0

---

## 📋 Overview

This guide explains how to set up and use Google OAuth authentication in the BNC application. Users can now login with their Google account directly, which automatically creates a user profile with their Google information.

---

## ✅ What's Already Done

### Backend Configuration
- [x] django-allauth installed and configured
- [x] Google provider added to INSTALLED_APPS
- [x] OAuth settings configured in settings.py
- [x] Custom social account adapter created (users/adapters.py)
- [x] Database migrations applied
- [x] Google login button added to login template
- [x] CSRF and security configured

### Frontend Changes
- [x] Google login button on login page (login.html)
- [x] Responsive design with Google branding
- [x] Proper SVG Google icon
- [x] Fallback to email/password login

### Code Files Modified
1. **config/settings.py** - OAuth configuration
2. **templates/auth/login.html** - Google login button
3. **users/adapters.py** - Custom profile adapter (NEW)
4. **users/views.py** - Import updates for OAuth handling

---

## 🔧 Setup Instructions

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     ```
     http://localhost:8000/auth/login/google/callback/
     http://localhost:8000/fr/auth/login/google/callback/
     http://localhost:8000/en/auth/login/google/callback/
     https://yourdomain.com/auth/login/google/callback/
     ```
   - Save the Client ID and Client Secret

### Step 2: Configure Environment Variables

Create or update `.env` file:

```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_SECRET=your_client_secret_here
```

Or set them in your production environment:

```bash
export GOOGLE_OAUTH_CLIENT_ID="your_client_id_here"
export GOOGLE_OAUTH_SECRET="your_client_secret_here"
```

### Step 3: Configure in Django Admin

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Go to http://localhost:8000/admin/

3. Navigate to **Sites** and verify:
   - Domain: `localhost:8000` (development) or your actual domain
   - Display name: `BNC - Bibliothèque Numérique`

4. Navigate to **Social applications**:
   - Click "Add Social Application"
   - Fill in:
     - **Provider**: Google
     - **Name**: Google OAuth
     - **Client id**: (from Step 1)
     - **Secret key**: (from Step 1)
     - **Sites**: Select "localhost:8000" (or your domain)
   - Save

---

## 🧪 Testing OAuth Login

### Test in Development

1. Go to http://localhost:8000/login/
2. Click "Continuer avec Google"
3. You'll be redirected to Google login
4. After login, you'll be redirected back and logged in as a new user
5. Your profile will be auto-populated with:
   - First name (from Google profile)
   - Last name (from Google profile)
   - Email
   - Profile picture (if available)

### Expected Flow

```
User clicks "Google" button
    ↓
Redirected to Google login page
    ↓
User enters Google credentials
    ↓
Google asks for permission (first time only)
    ↓
Redirected back to BNC with access token
    ↓
User profile created automatically
    ↓
User logged in and redirected to home page
```

---

## 📦 Architecture

### Files Involved

```
config/settings.py
├── INSTALLED_APPS (allauth, socialaccount, google)
├── AUTHENTICATION_BACKENDS (GoogleOAuth2Backend)
├── SOCIALACCOUNT_PROVIDERS (Google config)
└── SOCIALACCOUNT_ADAPTER (CustomSocialAccountAdapter)

users/adapters.py (NEW)
├── CustomSocialAccountAdapter
│   ├── populate_user() - Extract name/email from Google
│   ├── save_user() - Save profile picture
│   └── _download_and_save_profile_picture()

templates/auth/login.html
├── Google OAuth button
├── SVG icon
└── Styling

config/urls.py
├── /auth/ - allauth URLs (includes Google callback)
└── /auth/login/google/callback/
```

### Custom Adapter Behavior

The `CustomSocialAccountAdapter` in `users/adapters.py`:

1. **Extracts user information from Google**:
   - `given_name` → first_name
   - `family_name` → last_name
   - `email` → email
   - `picture` → profile picture (downloaded automatically)

2. **Auto-downloads profile picture** from Google
   - Saves to user's media directory
   - Handles failures gracefully

3. **Ensures data consistency**:
   - Falls back to `name` field if names unavailable
   - Validates email format
   - Handles edge cases

---

## 🔒 Security Features

### ✅ Already Implemented

1. **CSRF Protection**
   - Django CSRF tokens in all forms
   - CSRF middleware configured

2. **Token Security**
   - OAuth tokens stored securely in database
   - Sensitive data not logged

3. **User Data Privacy**
   - Only requested scopes: `profile`, `email`
   - User can revoke access anytime in Google settings
   - Profile picture downloaded once during signup

4. **Session Security**
   - Secure session cookies configured
   - HTTPS recommended for production
   - SameSite cookie protection

5. **Validation**
   - Email verification optional (can be mandatory)
   - User data sanitized before storage
   - Profile picture download has timeout protection

### ⚠️ Production Recommendations

1. Set these in production:
   ```python
   CSRF_COOKIE_SECURE = True      # HTTPS only
   SESSION_COOKIE_SECURE = True   # HTTPS only
   SOCIALACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Force email verification
   ```

2. Use HTTPS in all redirects
3. Keep secrets in environment variables (never in code)
4. Regularly audit social account connections in admin
5. Monitor failed OAuth attempts in logs

---

## 🐛 Troubleshooting

### Issue: "No social account found"

**Solution**: Make sure the Social Application is configured in admin:
```bash
python manage.py shell
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
site = Site.objects.get_or_create(domain='localhost:8000')
app = SocialApp.objects.get(provider='google')
app.sites.add(site[0])
```

### Issue: "Redirect URI mismatch"

**Solution**: Ensure redirect URIs in Google Console match exactly:
- Check protocol (http vs https)
- Check domain (localhost:8000 vs 127.0.0.1)
- Check path (must end with `/callback/`)
- Add internationalization paths

### Issue: Profile picture not downloading

**Solution**: Check:
- `requests` library installed
- MEDIA_ROOT directory exists and is writable
- User model has `profile_picture` field
- No errors in application logs

### Issue: User created but not logged in

**Solution**: Check:
- `SOCIALACCOUNT_AUTO_SIGNUP = True`
- User has email in Google profile
- No validation errors in logs
- Check Django admin for created user

---

## 📚 Usage Examples

### Login Button HTML

Already implemented in `templates/auth/login.html`:

```html
<a href="{% url 'socialaccount_login' 'google' %}" class="social-btn google-btn">
    <svg><!-- Google icon --></svg>
    Continuer avec Google
</a>
```

### Checking if User Has Google Account

```python
from allauth.socialaccount.models import SocialAccount

# In a view
google_account = SocialAccount.objects.filter(
    user=request.user,
    provider='google'
).first()

if google_account:
    print(f"Google email: {google_account.extra_data.get('email')}")
```

### Getting User's Google Email

```python
user = request.user
google_account = user.socialaccount_set.filter(provider='google').first()

if google_account:
    google_email = google_account.extra_data.get('email')
```

### Programmatically Creating a User via Google

```python
from allauth.socialaccount.models import SocialAccount

# Create user from Google data
user = CustomUser.objects.create_user(
    email='user@example.com',
    first_name='John',
    last_name='Doe'
)

# Link Google account
social_account = SocialAccount.objects.create(
    user=user,
    provider='google',
    uid='google_user_id',
    extra_data={
        'email': 'user@example.com',
        'picture': 'https://...',
    }
)
```

---

## 🔗 Related URLs

### Available OAuth Endpoints

- **Login**: `/auth/login/google/`
- **Callback**: `/auth/login/google/callback/`
- **Disconnect**: `/accounts/disconnect/google/`
- **Connections**: `/accounts/social/connections/`

### Important Views (in allauth)

- Login initiation: `socialaccount_login`
- Callback handling: `socialaccount_callback`
- Adapter: `CustomSocialAccountAdapter`

---

## 📊 Database Schema

### New Tables Created

1. **socialaccount_socialapp**
   - Stores OAuth app configuration

2. **socialaccount_socialaccount**
   ```
   user_id         - FK to CustomUser
   provider        - 'google'
   uid             - Google user ID
   extra_data      - JSON with profile data
   date_joined     - Creation timestamp
   ```

3. **socialaccount_sociallogin**
   - Temporary records during login flow

---

## 🚀 Next Steps

### Phase 2: Additional OAuth Providers

Can add these after Google is working:

1. **Apple Sign-In**
   - Install: `pip install django-allauth[apple]`
   - Similar setup process

2. **GitHub OAuth**
   - Great for developer accounts
   - Setup through GitHub Settings

3. **Microsoft/Office365**
   - For enterprise users
   - Similar to Google OAuth

### Phase 3: Social Features

Once OAuth is solid:

1. Link multiple social accounts to one user
2. Share reading progress on social media
3. See what friends are reading
4. Social recommendations

---

## 📝 Checklist

- [x] django-allauth installed
- [x] Google provider configured
- [x] Custom adapter created
- [x] Settings updated
- [x] Templates updated
- [x] Login button added
- [x] Migrations applied
- [ ] Google OAuth credentials created
- [ ] Environment variables set
- [ ] Social app configured in admin
- [ ] Tested in development
- [ ] Tested in production (once deployed)

---

## 🆘 Support

### Common Issues

1. **ImportError: No module named 'jwt'**
   - Solution: `pip install PyJWT cryptography`

2. **ModuleNotFoundError: No module named 'cryptography'**
   - Solution: `pip install cryptography`

3. **CSRF token mismatch during OAuth callback**
   - Solution: Check CSRF_TRUSTED_ORIGINS in settings
   - Add your domain to CSRF settings

### Debug Mode

Enable verbose logging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'allauth': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}
```

---

## 📖 References

- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 for Web Applications](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Django Security](https://docs.djangoproject.com/en/6.0/topics/security/)

---

**Status**: ✅ **READY FOR TESTING**

Next: Configure Google OAuth credentials and test the login flow.
