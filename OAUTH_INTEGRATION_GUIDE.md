# 🔐 OAuth Integration Guide - BNC

## Overview

This document explains how to setup and use OAuth (Google, Apple, Windows) authentication in BNC.

## ✅ What's Already Configured

- ✅ django-allauth installed and configured
- ✅ Google OAuth provider configured in settings
- ✅ Login template with OAuth buttons (`/templates/auth/login.html`)
- ✅ Management command for easy OAuth setup
- ✅ Database migrations applied

## 🚀 Quick Start (For Development)

### Option 1: Using Test Credentials (Fastest)

```bash
# Interactive setup
./setup_oauth.sh
# Then choose option 2

# Or direct command
python manage.py setup_oauth --provider google \
    --client-id "test-client-id.apps.googleusercontent.com" \
    --client-secret "test-client-secret"
```

### Option 2: Using Real Google OAuth Credentials

#### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a Project" → "NEW PROJECT"
3. Name it "BNC Development"
4. Click "CREATE"

#### Step 2: Enable Google+ API

1. Navigate to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click the result and press **ENABLE**

#### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth 2.0 Client IDs"**
3. Select **"Web application"**
4. Set name to "BNC Local Development"
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/auth/google/callback/
   http://127.0.0.1:8000/auth/google/callback/
   ```
6. Click **CREATE**
7. Copy the **Client ID** and **Client Secret**

#### Step 4: Configure in BNC

```bash
python manage.py setup_oauth --provider google \
    --client-id "YOUR_CLIENT_ID.apps.googleusercontent.com" \
    --client-secret "YOUR_CLIENT_SECRET"
```

Or use the interactive script:

```bash
./setup_oauth.sh
# Choose option 3
```

## 🔍 Verify OAuth Setup

### Check Configured Apps

```bash
python manage.py setup_oauth --list
```

Expected output:
```
✅ Configured OAuth Applications:
================================================================================

📱 Google
   Provider: google
   Client ID: 1234567890-abc...
   Sites: example.com
```

### Test the Login Page

1. Start Django server: `python manage.py runserver`
2. Visit http://localhost:8000/auth/login/
3. You should see "Continue with Google" button
4. Click it and test the flow

## 🌐 OAuth Flow

When user clicks "Continue with Google":

1. **Redirect to Google**: User is redirected to Google login
2. **User Authenticates**: User enters Google credentials
3. **Authorization**: User grants permission to BNC
4. **Callback**: Google redirects back to `http://localhost:8000/auth/google/callback/`
5. **Account Linking**: 
   - If first time: New account is created (SOCIALACCOUNT_AUTO_SIGNUP = True)
   - If returning: Existing account is linked
6. **Login**: User is logged in and redirected to catalogue page

## 📁 Project Structure

```
templates/
├── auth/
│   ├── login.html          # ✅ OAuth buttons added
│   └── register.html       # Can be updated with OAuth options
│
config/
├── settings.py             # ✅ OAuth configured
└── urls.py                 # ✅ allauth.urls included

catalogue/management/commands/
└── setup_oauth.py          # ✅ Management command for setup

setup_oauth.sh              # ✅ Interactive setup script
```

## 🔧 Key Settings in config/settings.py

```python
# OAuth Configuration
SITE_ID = 1  # Required for django-allauth

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Account Configuration
ACCOUNT_LOGIN_METHODS = {'email'}  # Email-only login (not username)
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1', 'password2']
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Can be 'mandatory' or 'none'

# Social Account Configuration
SOCIALACCOUNT_AUTO_SIGNUP = True  # Auto-create accounts on first OAuth login

# Redirect URLs
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'catalogue:catalogue'
ACCOUNT_LOGOUT_REDIRECT_URL = 'catalogue:catalogue'
```

## 🔐 OAuth Buttons in Templates

### Login Template (`templates/auth/login.html`)

```django
{% load socialaccount %}

<!-- Google Login -->
<a href="{% provider_login_url 'google' %}" class="social-btn">
    <i class="fab fa-google"></i>
    Continue with Google
</a>

<!-- Apple Login -->
<a href="{% provider_login_url 'apple' %}" class="social-btn">
    <i class="fab fa-apple"></i>
    Continue with Apple
</a>
```

The `{% provider_login_url %}` tag automatically generates the correct OAuth initiation URL.

## 🐛 Troubleshooting

### Issue: "Google OAuth not configured" Warning

**Cause**: OAuth app not created in Django admin
**Solution**: 
```bash
python manage.py setup_oauth --provider google --client-id YOUR_ID --client-secret YOUR_SECRET
```

### Issue: "Invalid redirect URI" Error

**Cause**: Redirect URI in Google Console doesn't match BNC
**Solution**:
1. Go to https://console.cloud.google.com/
2. Find your project's OAuth app
3. Edit and add correct redirect URIs:
   - `http://localhost:8000/auth/google/callback/`
   - `http://YOUR_DOMAIN/auth/google/callback/` (for production)

### Issue: OAuth button doesn't work

**Cause**: JavaScript disabled or caching issue
**Solution**:
1. Clear browser cache (Ctrl+Shift+Del)
2. Hard refresh page (Ctrl+Shift+R)
3. Check browser console for errors (F12)

### Issue: Account not created after OAuth login

**Cause**: SOCIALACCOUNT_AUTO_SIGNUP is False
**Solution**: Ensure in settings.py:
```python
SOCIALACCOUNT_AUTO_SIGNUP = True
```

## 🚀 Production Deployment

### Before Going to Production

1. **Use Real OAuth Credentials**
   ```bash
   python manage.py setup_oauth --provider google \
       --client-id "PRODUCTION_CLIENT_ID" \
       --client-secret "PRODUCTION_CLIENT_SECRET"
   ```

2. **Update Redirect URIs in Google Console**
   ```
   https://your-domain.com/auth/google/callback/
   ```

3. **Update Django Settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Update Site Domain in Django Admin**
   - Go to `/admin/sites/site/`
   - Change domain from `example.com` to your actual domain

5. **Test Complete Flow**
   ```bash
   python manage.py setup_oauth --list
   # Verify app is assigned to correct site
   ```

## 📚 Additional Providers

### Setup Apple OAuth

1. Get Apple credentials from https://developer.apple.com/
2. Run:
   ```bash
   python manage.py setup_oauth --provider apple \
       --client-id "YOUR_APPLE_ID" \
       --client-secret "YOUR_APPLE_SECRET"
   ```

### Setup Windows/GitHub/Facebook

Similar process - update the management command or use Django admin directly.

## 🔗 Useful Links

- [allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Documentation](https://developer.apple.com/sign-in-with-apple/)

## ✅ Completion Checklist

- [ ] OAuth apps created and configured
- [ ] Google OAuth tested and working
- [ ] Users can login with OAuth
- [ ] New accounts created automatically
- [ ] Redirect to catalogue after login works
- [ ] All HTTPS issues resolved (for production)

## 🎯 Progress Indicator

**OAuth Implementation: 90% Complete**

✅ Backend setup (django-allauth, settings, URLs, migrations)
✅ Frontend (login template with OAuth buttons)
⏳ Testing (verify complete OAuth flow)
⏳ Production deployment (real credentials, HTTPS, domain setup)

---

**Last Updated**: December 19, 2025
**Status**: Ready for OAuth testing and deployment
