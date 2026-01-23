# 🧪 TEST PAIEMENTS - GUIDE COMPLET

**Date:** 26 December 2025  
**Objectif:** Vérifier que tous les paiements fonctionnent  
**Durée:** 1-2 heures

---

## 📋 PRÉ-REQUIS

1. ✅ .env configuré avec toutes les clés
2. ✅ Application Django en local: `python manage.py runserver`
3. ✅ ngrok installé: `brew install ngrok` (pour webhooks)
4. ✅ Postman ou curl pour tester API

---

# 1️⃣ VÉRIFIER CONFIGURATION

## Étape 1: Lancer le script de vérification

```bash
cd /workspaces/bnc
python check_payment_config.py
```

**Résultat attendu:**
```
✅ STRIPE_API_KEY = sk_live_***
✅ PAYPAL_CLIENT_ID = ***
✅ MPESA_CONSUMER_KEY = ***
...
✅ TOUS LES PAIEMENTS CONFIGURÉS!
```

Si vous voyez des ❌, remplir les variables manquantes dans `.env`.

---

## Étape 2: Vérifier dans Django Shell

```bash
python manage.py shell
```

Puis taper:

```python
# Tester imports
from django.conf import settings
import stripe
import requests

# Vérifier Stripe
print("STRIPE_API_KEY:", settings.STRIPE_API_KEY[:20] + "***")
stripe.api_key = settings.STRIPE_API_KEY
print("✅ Stripe configuré")

# Vérifier PayPal
print("PAYPAL_CLIENT_ID:", settings.PAYPAL_CLIENT_ID[:20] + "***")
print("✅ PayPal configuré")

# Vérifier M-Pesa
print("MPESA_CONSUMER_KEY:", settings.MPESA_CONSUMER_KEY[:20] + "***")
print("✅ M-Pesa configuré")

# Quitter
exit()
```

---

# 2️⃣ TESTER STRIPE

## Test 1: Créer un PaymentIntent

```bash
python manage.py shell
```

```python
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

# Créer un paiement
intent = stripe.PaymentIntent.create(
    amount=5000,  # 50 USD en centimes
    currency="usd",
    metadata={
        "order_id": "TEST_001",
        "user_id": 1
    }
)

print("PaymentIntent créé!")
print(f"ID: {intent.id}")
print(f"Client Secret: {intent.client_secret}")
print(f"Status: {intent.status}")
print(f"Montant: {intent.amount / 100} {intent.currency.upper()}")
```

**Résultat attendu:**
```
PaymentIntent créé!
ID: pi_1234567890...
Client Secret: pi_1234567890...secret_abcdef...
Status: requires_payment_method
Montant: 50.0 USD
```

---

## Test 2: Tester avec une carte de test Stripe

1. Ouvrir http://localhost:8000/payment/
2. Entrer données du livre
3. Utiliser carte de test:
   ```
   4242 4242 4242 4242
   Expiration: 12/25
   CVC: 123
   ```
4. Cliquer "Pay"

**Résultat attendu:**
- ✅ Paiement approuvé
- ✅ Webhook reçu
- ✅ Statut = COMPLETED dans DB
- ✅ Email de confirmation envoyé
- ✅ Accès au livre accordé

---

## Test 3: Tester une carte refusée

```
4000 0000 0000 0002
Expiration: 12/25
CVC: 123
```

**Résultat attendu:**
- ❌ Paiement refusé
- ✅ Webhook reçu
- ✅ Statut = FAILED dans DB
- ✅ Email d'erreur envoyé

---

# 3️⃣ TESTER PAYPAL

## Test 1: Créer un paiement PayPal

```bash
python manage.py shell
```

```python
import requests
from django.conf import settings
import base64

# Obtenir token d'accès
auth = base64.b64encode(
    f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
).decode()

response = requests.post(
    "https://api.sandbox.paypal.com/v1/oauth2/token",  # Sandbox!
    headers={"Authorization": f"Basic {auth}"},
    data={"grant_type": "client_credentials"}
)

token = response.json()["access_token"]
print(f"✅ Token d'accès: {token[:50]}...")

# Créer paiement
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"
    },
    "transactions": [
        {
            "amount": {
                "total": "50.00",
                "currency": "USD",
                "details": {
                    "subtotal": "50.00"
                }
            },
            "description": "Test Book Purchase",
            "item_list": {
                "items": [
                    {
                        "name": "Test Book",
                        "sku": "TEST_001",
                        "price": "50.00",
                        "quantity": 1,
                        "currency": "USD"
                    }
                ]
            }
        }
    ],
    "redirect_urls": {
        "return_url": "https://yourdomain.com/payment/success/",
        "cancel_url": "https://yourdomain.com/payment/cancel/"
    }
}

response = requests.post(
    "https://api.sandbox.paypal.com/v1/payments/payment",
    headers=headers,
    json=payload
)

payment = response.json()
print(f"✅ Paiement créé: {payment['id']}")
print(f"Status: {payment['state']}")

# Trouver URL d'approbation
approval_url = next(
    link['href'] for link in payment['links'] 
    if link['rel'] == 'approval_url'
)
print(f"Cliquer: {approval_url}")
```

---

## Test 2: Webhook PayPal

1. Dashboard PayPal → Webhooks
2. Voir "Webhook Simulator"
3. Tester avec event `PAYMENT.SALE.COMPLETED`
4. URL: `https://yourdomain.com/api/payments/paypal/webhook/`

**Vérifier:**
- ✅ Webhook reçu (voir logs)
- ✅ Statut mis à jour dans DB
- ✅ Email envoyé

---

# 4️⃣ TESTER M-PESA

## Test 1: Obtenir Access Token

```bash
python manage.py shell
```

```python
import requests
import base64
from django.conf import settings

# Encoder credentials
credentials = base64.b64encode(
    f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
).decode()

response = requests.get(
    "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
    headers={"Authorization": f"Basic {credentials}"}
)

token = response.json()["access_token"]
print(f"✅ M-Pesa Token: {token[:50]}...")
```

---

## Test 2: Initier STK Push (sur téléphone réel)

```python
import requests
from django.conf import settings
import base64
from datetime import datetime

def get_mpesa_password():
    """Générer le password pour STK Push"""
    import base64
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(data.encode()).decode()

# Obtenir token
credentials = base64.b64encode(
    f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
).decode()

response = requests.get(
    "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
    headers={"Authorization": f"Basic {credentials}"}
)

token = response.json()["access_token"]

# STK Push
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
password = get_mpesa_password()

payload = {
    "BusinessShortCode": settings.MPESA_SHORTCODE,
    "Password": password,
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": "100",
    "PartyA": "254712345678",  # Numéro test
    "PartyB": settings.MPESA_SHORTCODE,
    "PhoneNumber": "254712345678",
    "CallBackURL": "https://yourdomain.com/api/payments/mpesa/webhook/",
    "AccountReference": "TEST_001",
    "TransactionDesc": "Test Payment"
}

response = requests.post(
    "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    headers={"Authorization": f"Bearer {token}"},
    json=payload
)

result = response.json()
print(f"✅ STK Push envoyé!")
print(f"CheckoutRequestID: {result.get('CheckoutRequestID')}")
print(f"Message: {result.get('ResponseDescription')}")

# Numéro test M-Pesa répondra avec prompt
# Suivre les instructions sur le téléphone
```

---

# 5️⃣ TESTER WEBHOOKS AVEC NGROK

Les webhooks nécessitent une URL HTTPS publique. Utiliser ngrok pour tester en local:

## Étape 1: Lancer ngrok

```bash
ngrok http 8000
```

**Résultat:**
```
Session Status                online
Account                       user@email.com
Session Token                 1234567890...
Version                        3.3.0

Web Interface                 http://localhost:4040
Forwarding                    https://abcd1234.ngrok.io -> http://localhost:8000
```

---

## Étape 2: Mettre à jour les webhooks

Dans les dashboards de chaque provider, remplacer:
```
https://yourdomain.com/api/payments/stripe/webhook/
```

Par:
```
https://abcd1234.ngrok.io/api/payments/stripe/webhook/
```

---

## Étape 3: Simuler un webhook

```bash
curl -X POST https://abcd1234.ngrok.io/api/payments/stripe/webhook/ \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=123456789,v1=signature" \
  -d '{
    "type": "payment_intent.succeeded",
    "data": {
      "object": {
        "id": "pi_1234567890",
        "amount": 5000,
        "currency": "usd",
        "status": "succeeded",
        "metadata": {
          "order_id": "TEST_001"
        }
      }
    }
  }'
```

---

## Étape 4: Vérifier les logs

```bash
# Terminal 1: Application Django
python manage.py runserver

# Terminal 2: Voir logs de paiement
tail -f logs/payments.log

# Terminal 3: ngrok interface
# http://localhost:4040 → voir tous les requêtes
```

---

# 📊 CHECKLIST DE TEST COMPLÈTE

## Stripe
- [ ] Script de config accepte les clés
- [ ] PaymentIntent créé
- [ ] Paiement réussi (4242...)
- [ ] Paiement échoué (4000...)
- [ ] Webhook reçu et traité
- [ ] Email de confirmation envoyé
- [ ] Accès au livre accordé

## PayPal
- [ ] Token d'accès obtenu
- [ ] Paiement créé
- [ ] URL d'approbation générée
- [ ] Webhook simulé
- [ ] Statut mis à jour
- [ ] Email envoyé

## M-Pesa
- [ ] Token d'accès obtenu
- [ ] STK Push initié (nombre de test)
- [ ] Réponse reçue
- [ ] Webhook mockée
- [ ] Statut mis à jour

## Airtel Money
- [ ] Token d'accès obtenu
- [ ] Paiement initié
- [ ] Réponse reçue

## Orange Money
- [ ] Credentials testées
- [ ] Paiement possible (optionnel)

---

# 🐛 TROUBLESHOOTING

### "API key not found"
```bash
# Vérifier .env
cat .env | grep STRIPE_API_KEY

# Redémarrer Django
python manage.py runserver
```

### "Webhook signature invalid"
```bash
# Vérifier le secret webhook est correct
# Dans Stripe Dashboard → Signing secret

# Vérifier la clé est dans .env
grep STRIPE_WEBHOOK_SECRET .env
```

### "Connection refused"
```bash
# Vérifier l'application tourne
curl http://localhost:8000/

# Si ngrok, vérifier URL correcte
ngrok http 8000
```

### "Email not sending"
```bash
# Vérifier SMTP config
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])

# Vérifier app password (pas mot de passe normal)
# Gmail: https://myaccount.google.com/apppasswords
```

---

# ✅ SUCCÈS!

Une fois tous les tests passés, vous êtes prêt à:
1. ✅ Passer les clés en mode LIVE (pas test)
2. ✅ Déployer en production
3. ✅ Activer les paiements pour les utilisateurs

---

**Besoin d'aide? Consulter PAYMENT_SYSTEM_COMPLETE_GUIDE.md**

Temps estimé: 1-2 heures pour tous les tests ⏱️
