# 🔒 GUIDE COMPLET - FINALISATION SYSTÈME PAIEMENTS

**Date:** 26 Décembre 2025  
**Version:** 1.0  
**Status:** Production Ready (après configuration)

---

## 📋 TABLE DES MATIÈRES

1. [Architecture Paiements](#architecture)
2. [Configuration Production](#configuration)
3. [Intégrations](#integrations)
4. [Webhooks](#webhooks)
5. [Réconciliation](#reconciliation)
6. [Testing](#testing)
7. [Déploiement](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARCHITECTURE {#architecture}

### **Structure des paiements**

```
┌─────────────────────────────────────────┐
│        Frontend (Lecteur/Shop)          │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ Initiate Payment │
        │ (payment_views.py)
        └────────┬─────────┘
                 │
        ┌────────▼──────────────────────────┐
        │  Payment Gateway Selection        │
        │  (payment_gateways.py)            │
        └────────┬──────────────────────────┘
                 │
   ┌─────┴──────┬──────┬──────────┬─────────┐
   │             │      │          │         │
  Stripe      PayPal  Airtel   M-Pesa    Bank
                │      │          │
   ┌────────────▼──────▼──────┬───▼──────────┐
   │     Payment Gateway      │  External    │
   │     API Calls            │  Provider    │
   └────────────┬─────────────┴──────────────┘
                │
   ┌────────────▼─────────┐
   │  Webhook Callback    │
   │ (payment_webhooks.py)│
   └────────────┬─────────┘
                │
   ┌────────────▼──────────────┐
   │  Update Payment Status    │
   │  Mark Book as Purchased   │
   │  Send Confirmation Email  │
   └──────────────────────────┘
```

### **Modèle Payment**

```python
class Payment(models.Model):
    # Relations
    user = ForeignKey(User)
    book = ForeignKey(Book)
    
    # Payment details
    amount = DecimalField
    currency = CharField  # XOF, USD, etc.
    
    # Tracking
    transaction_id = CharField  # Notre ID unique
    external_transaction_id = CharField  # ID du gateway
    
    # Status
    status = CharField  # PENDING, COMPLETED, FAILED, REFUNDED
    payment_method = CharField  # STRIPE, PAYPAL, MPESA, etc.
    
    # Timestamps
    created_at = DateTimeField
    processed_at = DateTimeField  # Quand le paiement a réussi
    refunded_at = DateTimeField   # Si remboursé
    
    # Additional
    error_message = TextField  # Si échoué
    webhook_data = JSONField   # Données brutes du gateway
    
    # Mobile Money specific
    checkout_request_id = CharField  # M-Pesa
    merchant_request_id = CharField  # M-Pesa
```

---

## ⚙️ CONFIGURATION PRODUCTION {#configuration}

### **1. Variables d'Environnement**

Créer un fichier `.env` avec:

```bash
# ==================== STRIPE ====================
STRIPE_API_KEY=sk_live_YOUR_REAL_SECRET_KEY
STRIPE_PUBLIC_KEY=pk_live_YOUR_REAL_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_WEBHOOK_SECRET

# ==================== PAYPAL ====================
PAYPAL_CLIENT_ID=YOUR_PRODUCTION_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_PRODUCTION_SECRET
PAYPAL_MODE=live
PAYPAL_WEBHOOK_ID=YOUR_WEBHOOK_ID

# ==================== MOBILE MONEY ====================
# Airtel Money
AIRTEL_API_KEY=YOUR_PRODUCTION_KEY
AIRTEL_API_SECRET=YOUR_PRODUCTION_SECRET
AIRTEL_MERCHANT_ID=YOUR_MERCHANT_ID

# M-Pesa (Safaricom)
MPESA_CONSUMER_KEY=YOUR_PRODUCTION_CONSUMER_KEY
MPESA_CONSUMER_SECRET=YOUR_PRODUCTION_CONSUMER_SECRET
MPESA_SHORTCODE=173379  # Votre shortcode
MPESA_PASSKEY=YOUR_PASSKEY

# Orange Money (RDC)
ORANGE_MONEY_API_KEY=YOUR_KEY
ORANGE_MONEY_API_SECRET=YOUR_SECRET
ORANGE_MONEY_MERCHANT_ID=YOUR_ID

# ==================== GENERAL ====================
PAYMENT_CURRENCY_DEFAULT=XOF
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host/db
SECRET_KEY=your-very-long-secret-key
```

### **2. Mise à jour de settings.py**

```python
# config/settings.py

# Paiements
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')

# Mobile Money
AIRTEL_API_KEY = os.getenv('AIRTEL_API_KEY')
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
ORANGE_MONEY_API_KEY = os.getenv('ORANGE_MONEY_API_KEY')

# Webhook URLs doivent être en HTTPS en production
PAYMENT_SUCCESS_REDIRECT = 'https://yourdomain.com/payment/success/'
PAYMENT_CANCEL_REDIRECT = 'https://yourdomain.com/payment/cancel/'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Logging pour les paiements
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'payment_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/payments.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'catalogue.payment_webhooks': {
            'handlers': ['payment_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### **3. Mise à jour des URLs**

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments/', include('catalogue.payment_webhook_urls')),
    # ... autres URLs
]
```

---

## 🔌 INTÉGRATIONS {#integrations}

### **STRIPE**

#### Setup

```bash
# 1. Créer compte: https://stripe.com
# 2. API Keys: https://dashboard.stripe.com/apikeys
# 3. Webhook Endpoint: https://dashboard.stripe.com/webhooks
```

#### Webhook Configuration

```
URL: https://yourdomain.com/api/payments/stripe/webhook/
Events à écouter:
  ✓ payment_intent.succeeded
  ✓ payment_intent.payment_failed
  ✓ charge.refunded
```

#### Code Example

```python
import stripe

stripe.api_key = settings.STRIPE_API_KEY

# Créer un PaymentIntent
intent = stripe.PaymentIntent.create(
    amount=int(book.price * 100),  # En centimes
    currency='usd',
    metadata={
        'order_id': payment.id,
        'user_id': request.user.id,
    }
)

# Retourner au frontend
return {
    'clientSecret': intent.client_secret
}
```

### **PAYPAL**

#### Setup

```bash
# 1. Créer compte: https://developer.paypal.com
# 2. App Credentials: https://developer.paypal.com/dashboard/apps/
# 3. Webhook Setup: https://developer.paypal.com/dashboard/webhooks/
```

#### Webhook Configuration

```
URL: https://yourdomain.com/api/payments/paypal/webhook/
Events à écouter:
  ✓ PAYMENT.SALE.COMPLETED
  ✓ PAYMENT.SALE.DENIED
  ✓ PAYMENT.SALE.REFUNDED
```

### **MOBILE MONEY**

#### Airtel Money

```python
# Configuration
AIRTEL_API_URL = 'https://api.airtel.africa/standard/v1/payments/mobile/checkout'

def initiate_airtel_payment(payment):
    """Initier un paiement Airtel Money"""
    headers = {
        'Authorization': f'Bearer {get_airtel_token()}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'reference': payment.transaction_id,
        'subscriber': {
            'country': 'SN',  # Code pays
            'currency': 'XOF',
            'msisdn': payment.user_phone,  # +221XXXXXXXXX
        },
        'transaction': {
            'amount': str(payment.amount),
            'country': 'SN',
            'currency': 'XOF',
            'id': payment.transaction_id,
        },
        'merchant': {
            'consumerKey': settings.AIRTEL_API_KEY,
            'displayName': 'BNC Digital Library',
        },
    }
    
    response = requests.post(AIRTEL_API_URL, json=payload, headers=headers)
    return response.json()
```

#### M-Pesa (Safaricom)

```python
# Configuration
MPESA_BASE_URL = 'https://api.safaricom.co.ke'

def initiate_mpesa_payment(payment):
    """Initier un paiement M-Pesa"""
    
    # Obtenir le token d'accès
    token = get_mpesa_access_token()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': get_mpesa_password(),
        'Timestamp': datetime.now().strftime('%Y%m%d%H%M%S'),
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(payment.amount),
        'PartyA': payment.user_phone,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': payment.user_phone,
        'CallBackURL': 'https://yourdomain.com/api/payments/mpesa/webhook/',
        'AccountReference': payment.transaction_id,
        'TransactionDesc': f'Book Purchase: {payment.book.title}',
    }
    
    response = requests.post(
        f'{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest',
        json=payload,
        headers=headers
    )
    
    result = response.json()
    
    # Sauvegarder les IDs pour réconciliation
    payment.checkout_request_id = result.get('CheckoutRequestID')
    payment.merchant_request_id = result.get('MerchantRequestID')
    payment.save()
    
    return result
```

---

## 🪝 WEBHOOKS {#webhooks}

### **Configuration des Webhooks**

Pour chaque provider, configurer:

1. **URL du webhook** (doit être HTTPS public)
2. **Secret de signature** (sauvegarder dans .env)
3. **Events à écouter**
4. **Retry policy** (généralement auto)

### **Test des Webhooks en Local**

Utiliser `ngrok` pour exposer le serveur local:

```bash
# 1. Installer ngrok: https://ngrok.com/download
# 2. Créer tunnel:
ngrok http 8000

# 3. Utiliser URL ngrok dans webhook config:
# https://abc123.ngrok.io/api/payments/stripe/webhook/

# 4. Tester avec des événements webhook:
# Stripe CLI:
stripe listen --forward-to localhost:8000/api/payments/stripe/webhook/
stripe trigger payment_intent.succeeded
```

### **Sécurité des Webhooks**

```python
# ✅ Toujours vérifier la signature
@csrf_exempt  # Nécessaire pour webhooks
def webhook_handler(request):
    # 1. Vérifier signature
    if not verify_signature(request):
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    # 2. Vérifier les données
    if not validate_webhook_data(request.body):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
    # 3. Traiter de manière idempotente
    # → Vérifier que le paiement n'existe pas déjà
    
    # 4. Enregistrer logs
    logger.info(f"Webhook processed: {webhook_id}")
    
    return JsonResponse({'status': 'success'})
```

---

## 🔄 RÉCONCILIATION {#reconciliation}

### **Processus de Réconciliation**

```bash
# Exécuter manuellement:
python manage.py reconcile_payments

# Avec filtres:
python manage.py reconcile_payments --payment-method STRIPE
python manage.py reconcile_payments --hours 24
python manage.py reconcile_payments --all

# Exécuter périodiquement avec Celery:
from celery import shared_task
from catalogue.payment_webhooks import reconcile_pending_payments

@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def reconcile_payments_task():
    reconcile_pending_payments()
```

### **Logique de Réconciliation**

```python
# 1. Trouver paiements PENDING
# 2. Pour chaque:
#    a. Appeler le gateway API pour vérifier statut
#    b. Mettre à jour Payment.status
#    c. Si COMPLETED:
#       - Ajouter book à user.purchased_books
#       - Envoyer email de confirmation
#    d. Si FAILED:
#       - Enregistrer message d'erreur
#       - Notifier utilisateur
# 3. Enregistrer résultats
```

---

## 🧪 TESTING {#testing}

### **Exécuter les Tests de Paiement**

```bash
# Tous les tests de paiement
python manage.py test catalogue.tests.test_payments_complete -v 2

# Tests spécifiques
python manage.py test catalogue.tests.test_payments_complete.StripePaymentTests
python manage.py test catalogue.tests.test_payments_complete.PayPalPaymentTests
python manage.py test catalogue.tests.test_payments_complete.MobileMoneyPaymentTests

# Avec couverture
coverage run --source='catalogue' manage.py test catalogue.tests.test_payments_complete
coverage report
```

### **Test Manual - Sandbox**

#### Stripe Sandbox

```bash
# 1. Activer Test Mode dans Stripe Dashboard
# 2. Utiliser keys de test (sk_test_...)
# 3. Cartes de test:
#    ✓ Succès: 4242 4242 4242 4242
#    ✓ Échec: 4000 0000 0000 0002
#    Exp: 12/25, CVC: 123
```

#### PayPal Sandbox

```bash
# 1. https://www.sandbox.paypal.com
# 2. Créer comptes de test (Buyer + Seller)
# 3. Utiliser sandbox.paypal.com au lieu de paypal.com
```

#### M-Pesa Sandbox

```bash
# 1. Utiliser environnement Safaricom: https://developer.safaricom.co.ke
# 2. Obtenir credentials de test
# 3. Mode: 'sandbox' dans settings
```

---

## 🚀 DÉPLOIEMENT {#deployment}

### **Checklist Pré-Déploiement**

```
✓ Environnement:
  [ ] SECRET_KEY configurée et sécurisée
  [ ] DEBUG = False
  [ ] ALLOWED_HOSTS configuré
  [ ] SSL/HTTPS activé

✓ Paiements:
  [ ] STRIPE_API_KEY configurée
  [ ] STRIPE_WEBHOOK_SECRET configurée
  [ ] PAYPAL credentials configurées
  [ ] Mobile Money credentials configurées
  [ ] Webhooks URLs configurées chez les providers
  [ ] Tester webhooks en sandbox
  [ ] Clés de production (pas de test!)

✓ Base de données:
  [ ] Migrations appliquées
  [ ] Indexes créés
  [ ] Backups configurés

✓ Email:
  [ ] SMTP configuré
  [ ] Templates email testés
  [ ] Adresse from configurée

✓ Logging:
  [ ] Logs de paiement configurés
  [ ] Rotation des logs activée
  [ ] Sentry configuré (optionnel)

✓ Tests:
  [ ] Tests unitaires passent (100%)
  [ ] Tests d'intégration passent
  [ ] Coverage 85%+
  [ ] Tests manuels complets en sandbox
```

### **Déploiement Étapé**

```
Phase 1: Sans paiements en ligne
  - Déployer code (webhooks prêts)
  - Tester fonctionnalités de base
  - Voir si les logs tournent bien

Phase 2: Paiements Sandbox
  - Configurer webhooks sandbox
  - Tester workflow complet
  - Vérifier logs et emails

Phase 3: Paiements Production
  - Configurer webhooks production
  - Tester avec montants réels minimes
  - Monitorer logs 24h/jour
  - Augmenter montants graduellement
```

### **Post-Déploiement**

```bash
# 1. Vérifier les webhooks
curl -X POST https://yourdomain.com/api/payments/stripe/webhook/ \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{"type": "ping"}'

# 2. Vérifier les logs
tail -f logs/payments.log

# 3. Tester paiement complet
# → Via frontend, effectuer paiement de test
# → Vérifier email reçu
# → Vérifier livre accessible

# 4. Monitorer
# → Stripe Dashboard: https://dashboard.stripe.com
# → PayPal Dashboard: https://www.paypal.com/signin
# → Email logs de confirmations
```

---

## 🔧 TROUBLESHOOTING {#troubleshooting}

### **Paiement reste PENDING**

```python
# 1. Vérifier les logs
tail -f logs/payments.log

# 2. Vérifier statut chez le gateway
# Stripe: https://dashboard.stripe.com/payments
# PayPal: https://www.paypal.com/reports

# 3. Exécuter réconciliation manuelle
python manage.py reconcile_payments

# 4. Vérifier webhooks
# → Stripe: https://dashboard.stripe.com/webhooks
# → PayPal: https://www.paypal.com/myaccount/webhook
```

### **Webhook non reçu**

```
Causes possibles:
1. URL du webhook incorrecte
   → Vérifier dans settings
   → Vérifier HTTPS actif
   
2. Signature webhook invalide
   → Vérifier secret key
   → Vérifier endpoint correct
   
3. Firewall bloque les requêtes
   → Vérifier pare-feu
   → Vérifier CORS si nécessaire
   
4. Serveur retourne erreur
   → Vérifier logs Django
   → Vérifier exceptions non capturées
```

### **Webhook reçu mais paiement pas mis à jour**

```
Solutions:
1. Vérifier que la signature webhook est vérifiée
2. Vérifier que l'ID transaction matche
3. Vérifier que le user/book existe
4. Vérifier les logs d'erreur de la fonction handler
```

### **Email de confirmation non envoyé**

```python
# 1. Vérifier configuration email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test',
...     'Test message',
...     'noreply@yourdomain.com',
...     ['yourtest@example.com'],
...     fail_silently=False,
... )

# 2. Vérifier les logs Django
# 3. Vérifier que SMTP n'est pas bloqué
```

### **Clés API incorrectes**

```bash
# Test Stripe:
python manage.py shell
>>> import stripe
>>> stripe.api_key = 'sk_test_...'
>>> stripe.Account.retrieve()

# Test PayPal:
>>> import requests
>>> response = requests.post(
...     'https://api.sandbox.paypal.com/v1/oauth2/token',
...     auth=('client_id', 'client_secret'),
... )

# Vérifier messages d'erreur dans logs
```

---

## 📞 SUPPORT

### **Ressources**

- **Stripe:** https://stripe.com/docs
- **PayPal:** https://developer.paypal.com/docs
- **Safaricom M-Pesa:** https://developer.safaricom.co.ke
- **Airtel Money:** https://africastalking.com/airtel-money

### **Contacts Support**

```
Stripe Support: https://support.stripe.com
PayPal Support: https://www.paypal.com/en/smarthelp
Safaricom Tech: developer@safaricom.co.ke
```

---

## ✅ CHECKLIST FINALISATION

```
Avant mise en production:

[ ] Configuration .env complète
[ ] settings.py updated
[ ] URLs configurées
[ ] Webhooks tests réussis
[ ] Tests unitaires ✓
[ ] Tests d'intégration ✓
[ ] Tests manuels sandbox ✓
[ ] Logs configurés
[ ] Email configuré
[ ] HTTPS actif
[ ] SSL certificate valide
[ ] Monitoring en place
[ ] Backups configurés
[ ] Team formée au troubleshooting
[ ] Documentation partagée
[ ] Runbook de déploiement prêt
[ ] Plan de rollback défini

PRÊT POUR PRODUCTION ✅
```

---

**Document généré:** 26 Décembre 2025  
**Statut:** Production Ready  
**Prochaine étape:** Configuration des API Keys + Tests Sandbox

