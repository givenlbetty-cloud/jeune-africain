# ⚙️ PRODUCTION DEPLOYMENT CONFIGURATION GUIDE

**Date:** 26 December 2025  
**Purpose:** Final security configuration for production deployment  
**Status:** Required before Phase 1 deployment

---

## 🔒 SECURITY CONFIGURATION CHECKLIST

The Django system identified 6 security warnings for production. These are expected and must be configured before deploying to production.

### Critical Configurations Required

#### 1. SECRET_KEY Configuration
**Current Status:** ⚠️ Development key  
**Action Required:** ✅ Update in production

```python
# In config/settings.py or config/.env

# Generate a secure secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Result example:
# jw%5@_(-sz_w!+#7&=^j@$n7r&(1=)5=c@*-j8*f!e1$4#q!-+

# Add to config/.env:
SECRET_KEY=jw%5@_(-sz_w!+#7&=^j@$n7r&(1=)5=c@*-j8*f!e1$4#q!-+
```

#### 2. DEBUG Setting
**Current Status:** ⚠️ DEBUG=True  
**Action Required:** ✅ Set to False

```python
# In config/settings.py or config/.env
DEBUG = False  # Production

# During development/testing:
DEBUG = True   # Only development
```

#### 3. HTTPS/SSL Configuration
**Current Status:** ⚠️ Not configured  
**Action Required:** ✅ Enable SSL

```python
# In config/settings.py for production:

# Force HTTPS redirect
SECURE_SSL_REDIRECT = True

# HTTP Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

#### 4. Allowed Hosts Configuration
**Current Status:** ⚠️ Not configured  
**Action Required:** ✅ Set production domain

```python
# In config/settings.py:
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'api.yourdomain.com',
]

# Or in config/.env:
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Environment Configuration
- [ ] SECRET_KEY is 50+ characters long
- [ ] SECRET_KEY has 5+ unique characters
- [ ] SECRET_KEY does NOT start with 'django-insecure-'
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured with production domain
- [ ] Database configured (PostgreSQL recommended)
- [ ] EMAIL backend configured (SMTP)
- [ ] Static files configured
- [ ] Media files configured

### Security Configuration
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SECURE_HSTS_SECONDS configured
- [ ] SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_HTTPONLY = True

### Payment Configuration
- [ ] STRIPE_SECRET_KEY configured
- [ ] STRIPE_PUBLISHABLE_KEY configured
- [ ] PAYPAL_CLIENT_ID configured
- [ ] PAYPAL_CLIENT_SECRET configured
- [ ] AIRTEL_CLIENT_ID configured
- [ ] AIRTEL_CLIENT_SECRET configured
- [ ] MPESA_CONSUMER_KEY configured
- [ ] MPESA_CONSUMER_SECRET configured

### OAuth Configuration
- [ ] GOOGLE_OAUTH_CLIENT_ID configured
- [ ] GOOGLE_OAUTH_CLIENT_SECRET configured
- [ ] APPLE_OAUTH_TEAM_ID configured
- [ ] APPLE_OAUTH_CLIENT_ID configured
- [ ] APPLE_OAUTH_KEY_ID configured
- [ ] APPLE_OAUTH_PRIVATE_KEY configured

### Email Configuration
- [ ] EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
- [ ] EMAIL_HOST configured
- [ ] EMAIL_PORT = 587
- [ ] EMAIL_USE_TLS = True
- [ ] EMAIL_HOST_USER configured
- [ ] EMAIL_HOST_PASSWORD configured
- [ ] DEFAULT_FROM_EMAIL configured

### Database Configuration
- [ ] DATABASE_ENGINE = 'django.db.backends.postgresql'
- [ ] DATABASE_NAME configured
- [ ] DATABASE_USER configured
- [ ] DATABASE_PASSWORD configured
- [ ] DATABASE_HOST configured
- [ ] DATABASE_PORT = 5432
- [ ] All migrations applied
- [ ] Backup automated

### Static & Media Files
- [ ] STATIC_URL configured
- [ ] STATIC_ROOT configured
- [ ] MEDIA_URL configured
- [ ] MEDIA_ROOT configured
- [ ] Static files collected (collectstatic)
- [ ] CDN integration tested (optional)

### Monitoring & Logging
- [ ] LOGGING configured
- [ ] Sentry/Error tracking enabled
- [ ] Uptime monitoring configured
- [ ] Performance monitoring configured
- [ ] Log rotation configured

---

## 🔧 PRODUCTION SETTINGS TEMPLATE

Create `config/settings/production.py`:

```python
# Production Django Settings
from .base import *
import os

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

---

## 🌍 ENVIRONMENT VARIABLES TEMPLATE

Create `config/.env.production`:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=<your-secure-secret-key-50-chars>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=bnc_production
DATABASE_USER=bnc_user
DATABASE_PASSWORD=<secure-password>
DATABASE_HOST=your-db-host.com
DATABASE_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/var/www/bnc/staticfiles

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/bnc/media

# Payment Keys
STRIPE_SECRET_KEY=sk_live_<your-key>
STRIPE_PUBLISHABLE_KEY=pk_live_<your-key>
PAYPAL_CLIENT_ID=<your-id>
PAYPAL_CLIENT_SECRET=<your-secret>
AIRTEL_CLIENT_ID=<your-id>
AIRTEL_CLIENT_SECRET=<your-secret>
MPESA_CONSUMER_KEY=<your-key>
MPESA_CONSUMER_SECRET=<your-secret>

# OAuth Keys
GOOGLE_OAUTH_CLIENT_ID=<your-id>.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=<your-secret>
APPLE_OAUTH_TEAM_ID=<your-team-id>
APPLE_OAUTH_CLIENT_ID=com.yourdomain.auth
APPLE_OAUTH_KEY_ID=<your-key-id>
APPLE_OAUTH_PRIVATE_KEY=<your-private-key>

# Redis Cache
REDIS_URL=redis://localhost:6379/1

# Site Configuration
SITE_URL=https://yourdomain.com
SITE_NAME=BNC Digital Library
```

---

## 🚀 PRODUCTION DEPLOYMENT COMMANDS

### 1. Before Deployment
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Check production settings
python manage.py check --deploy
```

### 2. Deployment
```bash
# Using Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Using uWSGI
uwsgi --http :8000 --wsgi-file config/wsgi.py --master --processes 4 --threads 2

# Using Waitress (Windows-friendly)
waitress-serve config.wsgi:application --host 0.0.0.0 --port 8000
```

### 3. Background Tasks (Celery)
```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat (for scheduled tasks)
celery -A config beat -l info
```

### 4. Monitoring
```bash
# Check system health
python manage.py check

# Monitor logs
tail -f /var/log/django/django.log

# Check database
python manage.py dbshell
```

---

## 📊 PRODUCTION MONITORING

### Critical Metrics to Monitor
1. **Application Health**
   - Error rate (target: < 0.1%)
   - Response time (target: < 200ms)
   - Uptime (target: > 99.9%)

2. **Database Performance**
   - Query time (target: < 50ms)
   - Connection pool usage
   - Backup status

3. **Payment System**
   - Webhook processing time
   - Failed transactions
   - Reconciliation status

4. **OAuth System**
   - Login success rate
   - Social account linkages
   - Failed authentications

5. **User Activity**
   - Active users
   - API usage
   - File downloads

---

## 🆘 TROUBLESHOOTING

### Common Production Issues

**1. SECRET_KEY Warning**
```
Problem: "SECRET_KEY has less than 50 characters"
Solution: Generate new key with:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**2. SSL/HTTPS Issues**
```
Problem: "SECURE_SSL_REDIRECT is not set"
Solution: Set in settings.py:
SECURE_SSL_REDIRECT = True
```

**3. Database Connection**
```
Problem: "Could not connect to database"
Solution: 
1. Verify DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD
2. Check database server is running
3. Verify firewall allows connection
```

**4. Static Files Not Loading**
```
Problem: "/static/ returning 404"
Solution:
1. Run: python manage.py collectstatic
2. Configure web server to serve STATIC_ROOT
3. Verify STATIC_ROOT path exists
```

**5. Email Not Sending**
```
Problem: "Error sending email"
Solution:
1. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
2. Check SMTP server allows your IP
3. Verify DEFAULT_FROM_EMAIL is configured
4. Enable "Less secure app access" if using Gmail
```

---

## 📞 DEPLOYMENT SUPPORT

### Before You Deploy
1. ✅ Complete all checklist items above
2. ✅ Test in staging environment first
3. ✅ Review DEPLOYMENT_CHECKLIST_PRODUCTION.md
4. ✅ Have rollback plan ready
5. ✅ Monitor logs during and after deployment

### Quick Reference
- **Main Guide:** DEPLOYMENT_CHECKLIST_PRODUCTION.md
- **Payment Setup:** PAYMENT_SYSTEM_COMPLETE_GUIDE.md
- **OAuth Setup:** OAUTH_GOOGLE_APPLE_COMPLETE_GUIDE.md
- **API Docs:** API_DOCUMENTATION_COMPLETE.md

---

**Generated:** 26 December 2025  
**Status:** Ready for production deployment  
**Next Step:** Follow DEPLOYMENT_CHECKLIST_PRODUCTION.md

🚀 **Good luck with your deployment!**
