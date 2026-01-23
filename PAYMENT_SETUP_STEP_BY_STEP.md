# 💳 CONFIGURATION PAIEMENT - ÉTAPE PAR ÉTAPE

**Date:** 26 December 2025  
**Durée estimée:** 3-4 heures pour tous les paiements  
**Status:** READY TO CONFIGURE

---

## 🎯 OBJECTIF

Configurer 5 méthodes de paiement:
1. ✅ Stripe (Cartes bancaires) - 20 min
2. ✅ PayPal (Comptes) - 20 min
3. ✅ Airtel Money (Mobile) - 15 min
4. ✅ M-Pesa (Mobile Kenya) - 15 min
5. ✅ Orange Money (Mobile RDC) - 15 min

**Total: ~1.5 heures pour setup + 2 heures pour testing**

---

# 1️⃣ STRIPE (Cartes bancaires)

## Étape 1: Créer un compte Stripe

1. Aller à: https://stripe.com
2. Cliquer "Sign Up"
3. Entrer email + mot de passe
4. Vérifier email
5. Compléter profil: Pays, Nom, Adresse

**Temps:** 10 min

---

## Étape 2: Obtenir les API Keys

1. Se connecter à: https://dashboard.stripe.com
2. Menu → Developers → API Keys
3. Copier:
   - **Secret Key**: `sk_live_XXXXXXXXXX` (garde privé!)
   - **Publishable Key**: `pk_live_XXXXXXXXXX` (peut être public)

**⚠️ IMPORTANT:** 
- Secret Key = Ne JAMAIS partager (sauvegarder dans .env)
- Publishable Key = Peut être en frontend

---

## Étape 3: Ajouter à .env

```bash
# .env ou .env.production
STRIPE_API_KEY=sk_live_VOTRE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_live_VOTRE_CLE_PUBLIQUE
STRIPE_WEBHOOK_SECRET=whsec_live_VOTRE_WEBHOOK_SECRET
```

---

## Étape 4: Configurer Webhook

1. Dashboard Stripe → Developers → Webhooks
2. Cliquer "Add endpoint"
3. URL du webhook: `https://yourdomain.com/api/payments/stripe/webhook/`
4. Sélectionner events:
   - ✅ `payment_intent.succeeded`
   - ✅ `payment_intent.payment_failed`
   - ✅ `charge.refunded`
5. Cliquer "Create endpoint"
6. Voir "Signing secret" → Copier dans .env comme `STRIPE_WEBHOOK_SECRET`

**Temps:** 5 min

---

## Étape 5: Tester en Mode Test

Stripe fournit des numéros de carte de test:

```
Visa de test:
  Numéro: 4242 4242 4242 4242
  Expiration: 12/25
  CVC: 123
  
Visa refusée:
  Numéro: 4000 0000 0000 0002
  Expiration: 12/25
  CVC: 123
```

**Dans le code:**
```python
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

# Créer un PaymentIntent
intent = stripe.PaymentIntent.create(
    amount=5000,  # 50 USD en centimes
    currency="usd",
    metadata={"order_id": payment.id}
)
```

---

## Étape 6: Passer en Mode Live

1. Dans Stripe Dashboard → Settings
2. Activer "Live mode"
3. Obtenir vraies API Keys de production
4. Remplacer dans .env

---

# 2️⃣ PAYPAL

## Étape 1: Créer un compte PayPal

1. Aller à: https://developer.paypal.com
2. Cliquer "Sign Up"
3. Choisir "Business Account"
4. Compléter profil

**Temps:** 10 min

---

## Étape 2: Obtenir Credentials

1. Dashboard → Apps & Credentials
2. Choisir "Sandbox" puis "Production"
3. Section "REST API signature":
   - **Client ID**: `XXXXXXX.XXX`
   - **Secret**: `XXXXXX` (garde privé!)

---

## Étape 3: Ajouter à .env

```bash
PAYPAL_CLIENT_ID=YOUR_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_SECRET
PAYPAL_MODE=live
```

---

## Étape 4: Configurer Webhook

1. Dashboard → Webhooks
2. Cliquer "Create new webhook"
3. URL: `https://yourdomain.com/api/payments/paypal/webhook/`
4. Sélectionner events:
   - ✅ PAYMENT.SALE.COMPLETED
   - ✅ PAYMENT.SALE.DENIED
   - ✅ PAYMENT.SALE.REFUNDED
5. Copier "Webhook ID" dans .env

```bash
PAYPAL_WEBHOOK_ID=YOUR_WEBHOOK_ID
```

---

## Étape 5: Tester PayPal Sandbox

**Compte de test (Sandbox):**
```
Email: sb-xxxxx@personal.example.com
Password: À créer dans Sandbox settings
```

1. Dashboard → Accounts
2. "Buyer" account → Créer
3. Utiliser pour tester paiements

---

# 3️⃣ AIRTEL MONEY (Mobile Money)

## Étape 1: Créer compte Airtel Africa

1. Aller à: https://airtel.africa/
2. Créer compte business
3. Remplir: Pays, Business type, Revenue

**Temps:** 15 min

---

## Étape 2: Accès API

1. Aller à: https://developer.airtel.africa/
2. Register application
3. Obtenir:
   - **API Key** (conservation)
   - **API Secret** (gardé privé)

---

## Étape 3: Ajouter à .env

```bash
AIRTEL_API_KEY=YOUR_KEY
AIRTEL_API_SECRET=YOUR_SECRET
AIRTEL_MERCHANT_ID=YOUR_MERCHANT_ID
AIRTEL_API_URL=https://api.airtel.africa/standard/v1
```

---

## Étape 4: Configurer Webhook

1. Aller à Dashboard → Webhooks
2. URL: `https://yourdomain.com/api/payments/airtel/webhook/`
3. Activer pour: Payment notifications

---

## Étape 5: Obtenir Token d'Accès

```python
import requests

def get_airtel_token():
    url = "https://api.airtel.africa/auth/oauth2/token"
    
    auth = (settings.AIRTEL_API_KEY, settings.AIRTEL_API_SECRET)
    payload = {
        "grant_type": "client_credentials"
    }
    
    response = requests.post(url, auth=auth, data=payload)
    return response.json()["access_token"]
```

---

# 4️⃣ M-PESA (Mobile Kenya)

## Étape 1: Safaricom Account

1. Aller à: https://safaricom.co.ke/
2. Créer compte Business
3. Demander "Daraja API" access

**Note:** M-Pesa est spécifique à Kenya. Nécessite:
- Compte Safaricom Business
- Shortcode (numéro de 5-6 chiffres)
- Passkey

**Temps:** 30 min (processus plus long)

---

## Étape 2: Obtenir Credentials

À partir de Daraja Dashboard:
- **Consumer Key**
- **Consumer Secret**
- **Shortcode** (votre numéro de commerçant)
- **Passkey** (pour STK Push)

---

## Étape 3: Ajouter à .env

```bash
MPESA_CONSUMER_KEY=YOUR_CONSUMER_KEY
MPESA_CONSUMER_SECRET=YOUR_CONSUMER_SECRET
MPESA_SHORTCODE=173379  # Exemple
MPESA_PASSKEY=YOUR_PASSKEY
MPESA_API_URL=https://api.safaricom.co.ke
```

---

## Étape 4: Configurer Webhook

1. Dashboard Safaricom → Webhooks
2. URL: `https://yourdomain.com/api/payments/mpesa/webhook/`
3. Activer pour: STK Push callback

---

## Étape 5: Générer Access Token

```python
import requests
import base64

def get_mpesa_access_token():
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    auth = base64.b64encode(
        f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    
    headers = {"Authorization": f"Basic {auth}"}
    
    response = requests.get(url, headers=headers)
    return response.json()["access_token"]
```

---

# 5️⃣ ORANGE MONEY (Mobile RDC)

## Étape 1: Créer Compte

1. Aller à: https://orangemoney.cd/ (ou votre pays)
2. Business registration
3. Obtenir Merchant ID

---

## Étape 2: Credentials

À partir de Orange Money Dashboard:
- **API Key**
- **API Secret**
- **Merchant ID**

---

## Étape 3: Ajouter à .env

```bash
ORANGE_MONEY_API_KEY=YOUR_KEY
ORANGE_MONEY_API_SECRET=YOUR_SECRET
ORANGE_MONEY_MERCHANT_ID=YOUR_MERCHANT_ID
ORANGE_MONEY_API_URL=https://api.orange.com/moneyrdc/v1
```

---

# 📝 FICHIER .env COMPLET

Créer `.env` ou `.env.production` avec:

```bash
# =============== STRIPE ===============
STRIPE_API_KEY=sk_live_YOUR_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_WEBHOOK_SECRET

# =============== PAYPAL ===============
PAYPAL_CLIENT_ID=YOUR_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_SECRET
PAYPAL_MODE=live
PAYPAL_WEBHOOK_ID=YOUR_WEBHOOK_ID

# =============== AIRTEL MONEY ===============
AIRTEL_API_KEY=YOUR_KEY
AIRTEL_API_SECRET=YOUR_SECRET
AIRTEL_MERCHANT_ID=YOUR_MERCHANT_ID
AIRTEL_API_URL=https://api.airtel.africa/standard/v1

# =============== M-PESA ===============
MPESA_CONSUMER_KEY=YOUR_KEY
MPESA_CONSUMER_SECRET=YOUR_SECRET
MPESA_SHORTCODE=173379
MPESA_PASSKEY=YOUR_PASSKEY
MPESA_API_URL=https://api.safaricom.co.ke

# =============== ORANGE MONEY ===============
ORANGE_MONEY_API_KEY=YOUR_KEY
ORANGE_MONEY_API_SECRET=YOUR_SECRET
ORANGE_MONEY_MERCHANT_ID=YOUR_ID
ORANGE_MONEY_API_URL=https://api.orange.com/moneyrdc/v1

# =============== GENERAL ===============
DEBUG=False
SECRET_KEY=your-very-long-secret-key-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host/db
PAYMENT_CURRENCY_DEFAULT=XOF

# =============== EMAIL ===============
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

# 🔧 MISE À JOUR settings.py

```python
# config/settings.py

import os
from pathlib import Path

# =============== PAYMENT CONFIG ===============
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')

AIRTEL_API_KEY = os.getenv('AIRTEL_API_KEY')
AIRTEL_API_SECRET = os.getenv('AIRTEL_API_SECRET')
AIRTEL_API_URL = os.getenv('AIRTEL_API_URL', 'https://api.airtel.africa/standard/v1')

MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')

ORANGE_MONEY_API_KEY = os.getenv('ORANGE_MONEY_API_KEY')
ORANGE_MONEY_API_SECRET = os.getenv('ORANGE_MONEY_API_SECRET')
ORANGE_MONEY_MERCHANT_ID = os.getenv('ORANGE_MONEY_MERCHANT_ID')

# Redirect URLs (après paiement réussi/échoué)
PAYMENT_SUCCESS_REDIRECT = 'https://yourdomain.com/payment/success/'
PAYMENT_CANCEL_REDIRECT = 'https://yourdomain.com/payment/cancel/'

# Currency default
PAYMENT_CURRENCY_DEFAULT = os.getenv('PAYMENT_CURRENCY_DEFAULT', 'XOF')

# =============== EMAIL CONFIG ===============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# =============== LOGGING ===============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'payment_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/payments.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'catalogue.payment_webhooks': {
            'handlers': ['payment_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

# ✅ CHECKLIST DE CONFIGURATION

## Stripe
- [ ] Créer compte https://stripe.com
- [ ] Obtenir API Keys
- [ ] Ajouter à .env
- [ ] Configurer webhook
- [ ] Copier Webhook Secret dans .env
- [ ] Tester avec cartes de test

## PayPal
- [ ] Créer compte https://developer.paypal.com
- [ ] Obtenir Client ID + Secret
- [ ] Ajouter à .env
- [ ] Configurer webhook
- [ ] Copier Webhook ID dans .env
- [ ] Tester avec compte Sandbox

## Airtel Money
- [ ] Créer compte https://developer.airtel.africa/
- [ ] Obtenir API Key + Secret
- [ ] Ajouter à .env
- [ ] Configurer webhook
- [ ] Tester (note: simulé ou avec vrai téléphone)

## M-Pesa
- [ ] Créer compte Safaricom
- [ ] Demander Daraja API access
- [ ] Obtenir Consumer Key + Secret
- [ ] Obtenir Shortcode + Passkey
- [ ] Ajouter à .env
- [ ] Configurer webhook
- [ ] Tester

## Orange Money
- [ ] Créer compte https://orangemoney.cd/
- [ ] Obtenir API credentials
- [ ] Ajouter à .env
- [ ] Configurer webhook
- [ ] Tester

---

# 🧪 TESTER LES PAIEMENTS

Une fois configuré, tester:

```bash
# 1. Vérifier config
python manage.py shell
>>> from django.conf import settings
>>> settings.STRIPE_API_KEY
'sk_live_...'

# 2. Tester Stripe
>>> import stripe
>>> stripe.api_key = settings.STRIPE_API_KEY
>>> intent = stripe.PaymentIntent.create(amount=1000, currency="usd")
>>> intent.client_secret
'pi_1234...secret_...'

# 3. Tester webhooks
# Utiliser curl ou Postman pour simuler webhook

# 4. Tester endpoint
curl -X POST https://yourdomain.com/api/payments/stripe/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"type":"payment_intent.succeeded",...}'
```

---

# 🚀 PROCHAINES ÉTAPES

1. ✅ Configurer .env avec toutes les clés
2. ✅ Mettre à jour settings.py
3. ✅ Redémarrer l'application
4. ✅ Tester chaque méthode de paiement
5. ✅ Activer en production

**Durée totale:** 3-4 heures (setup + testing)

---

**Prêt à configurer? 🚀**

Besoin d'aide pour une méthode de paiement spécifique?
