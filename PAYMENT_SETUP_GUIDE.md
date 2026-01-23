# 📖 Guide de Configuration des Passerelles de Paiement

## 🎯 Vue d'ensemble

La plateforme BNC supporte 5 méthodes de paiement:
1. **Stripe** (Cartes bancaires internationales)
2. **PayPal** (Global, très populaire)
3. **Airtel Money** (Afrique de l'Ouest)
4. **M-Pesa** (Kenya & Afrique de l'Est)
5. **Orange Money** (RDC, Afrique Centrale)

---

## 🔐 Configuration par Passerelle

### 1️⃣ STRIPE (Cartes Bancaires Internationales)

**URL:** https://stripe.com/

**Étapes:**
1. Créer un compte Stripe
2. Aller à Dashboard → API Keys
3. Copier les clés TEST (développement) ou LIVE (production)

**Variables d'environnement:**
```
STRIPE_API_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**Test:**
- Carte test: `4242 4242 4242 4242`
- Expiration: `12/25`
- CVC: `123`

**Coûts:** 2.9% + 0.30 USD par transaction

---

### 2️⃣ PAYPAL (Global)

**URL:** https://developer.paypal.com/

**Étapes:**
1. Créer un compte PayPal Business
2. Aller à Apps & Credentials
3. Créer une application "merchant"
4. Copier Client ID et Secret

**Variables d'environnement:**
```
PAYPAL_MODE=sandbox  # ou 'live' en production
PAYPAL_CLIENT_ID=AZxxx
PAYPAL_CLIENT_SECRET=xxxxx
```

**Test (Sandbox):**
- Email: `sb-xxxxx@business.example.com`
- Password: Test password from dashboard

**Coûts:** 3.49% + 0.49 USD par transaction

---

### 3️⃣ AIRTEL MONEY (Afrique de l'Ouest)

**URL:** https://www.airtelmoneyadmin.com/

**Pays supportés:** Senegal, Benin, Burkina Faso, Niger, Mali, RDC, etc.

**Étapes:**
1. S'inscrire comme marchand
2. Compléter KYC (vérification d'identité)
3. Recevoir credentials
4. Tester en mode sandbox

**Variables d'environnement:**
```
AIRTEL_CLIENT_ID=xxx
AIRTEL_CLIENT_SECRET=xxx
AIRTEL_PIN=1234  # PIN confidentiel
```

**Coûts:** 2.5-3% par transaction

---

### 4️⃣ M-PESA (Kenya & Afrique de l'Est)

**URL:** https://developer.safaricom.co.ke/

**Pays supportés:** Kenya, Tanzania, Uganda, DRC, etc.

**Étapes:**
1. Créer compte SafariCom Developer
2. Créer une application
3. Recevoir Consumer Key et Secret
4. Demander code court (shortcode)

**Variables d'environnement:**
```
MPESA_CONSUMER_KEY=xxx
MPESA_CONSUMER_SECRET=xxx
MPESA_SHORTCODE=123456
MPESA_PASSKEY=xxx
```

**Coûts:** 0.79% du montant (minimum KES 10)

---

### 5️⃣ ORANGE MONEY (RDC & Afrique Centrale)

**URL:** https://developer.orange.com/

**Pays supportés:** RDC, Cameroun, Côte d'Ivoire, etc.

**Étapes:**
1. S'inscrire comme développeur
2. Créer une API subscription
3. Recevoir API Key et Secret
4. Tester en sandbox

**Variables d'environnement:**
```
ORANGE_MONEY_API_KEY=xxx
ORANGE_MONEY_API_SECRET=xxx
```

**Coûts:** 2-3% par transaction

---

## 🚀 Mise en Production

### Checklist de déploiement:

- [ ] Tous les API keys configurés en variables d'environnement
- [ ] Mode paiement changé de SANDBOX à PRODUCTION/LIVE
- [ ] HTTPS activé sur le domaine
- [ ] Webhooks configurés pour chaque passerelle
- [ ] Email de confirmation envoyé après paiement
- [ ] Système de refund implémenté
- [ ] Logging et monitoring en place
- [ ] Tests de paiement réels (montant minimum)

### Variables d'environnement PRODUCTION:

```bash
# Stripe (LIVE)
STRIPE_API_KEY=sk_live_xxx

# PayPal (LIVE)
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=AZxxx_live

# Site
SITE_URL=https://votre-domaine.com
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📊 Modèle de Données

```python
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('CREDIT_CARD', 'Carte Bancaire'),
        ('PAYPAL', 'PayPal'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Virement Bancaire'),
        ('CASH', 'Paiement en Espèces'),
    ]
    
    STATUSES = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
        ('REFUNDED', 'Remboursé'),
    ]
    
    user = ForeignKey(User)
    book = ForeignKey(Book)
    amount = DecimalField()
    currency = CharField(default='XOF')
    transaction_id = CharField(unique=True)
    payment_method = CharField(choices=PAYMENT_METHODS)
    status = CharField(choices=STATUSES, default='PENDING')
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

---

## 🧪 Tests Locaux

```bash
# Tester Stripe
python manage.py shell
>>> from catalogue.payment_gateways import StripePaymentGateway
>>> from catalogue.models import Payment

# Créer un paiement de test
# payment = Payment.objects.create(...)
# gateway = StripePaymentGateway(payment)
# result = gateway.initiate_payment()
```

---

## ⚠️ Sécurité

**NE JAMAIS:**
- Committer les API keys dans Git
- Stocker les numéros de carte en clair
- Logger les tokens d'authentification
- Laisser CSRF_EXEMPT sur webhook sans vérification

**À FAIRE:**
- Utiliser variables d'environnement
- Vérifier signature des webhooks
- Valider montant côté serveur
- Utiliser HTTPS en production
- Rate-limit les endpoints de paiement

---

## 📞 Support

Pour chaque passerelle, contacter:
- **Stripe:** support.stripe.com
- **PayPal:** developer.paypal.com/support
- **Airtel:** airtelmoneyadmin.com
- **M-Pesa:** developer.safaricom.co.ke
- **Orange:** developer.orange.com
