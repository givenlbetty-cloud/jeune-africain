# 💳 PayPal Sandbox Setup - Guide Complet (20 min)

## 🎯 Objectif

Configurer PayPal Sandbox pour tester les paiements sans utiliser de vraies cartes bancaires.

---

## ⏱️ ÉTAPE 1: Aller sur PayPal Developer (2 min)

### 1.1 Ouvre le navigateur et va à:
```
https://developer.paypal.com/
```

### 1.2 Clique sur "Sign in" en haut à droite
- Si tu as un compte PayPal: Connecte-toi
- Si tu n'as pas de compte: Crée-en un (gratuit)

---

## ⏱️ ÉTAPE 2: Créer une Application Sandbox (3 min)

### 2.1 Après connexion, va à "Apps & Credentials" (dans le menu gauche)

```
Dashboard → Apps & Credentials
```

### 2.2 Assure-toi que "Sandbox" est sélectionné (en haut)

```
┌─────────────────────┐
│ Live  │  Sandbox ✓  │
└─────────────────────┘
```

### 2.3 Clique sur "Create App" sous "Merchant Accounts"

- Nomme l'app: `BNC Digital Library`
- Clique "Create"

---

## ⏱️ ÉTAPE 3: Récupérer les Credentials (2 min)

### 3.1 Tu viens de créer l'app. Maintenant clique dessus dans la liste.

Tu devrais voir une page avec:

```
┌──────────────────────────────────────────┐
│  App Name: BNC Digital Library           │
├──────────────────────────────────────────┤
│  Sandbox Signature Signature              │
│  ─────────────────────────────────────    │
│  Client ID:                               │
│  ┌──────────────────────────────────┐    │
│  │ AeBz....... (très long)          │    │
│  └──────────────────────────────────┘    │
│                                           │
│  Secret:                                  │
│  ┌──────────────────────────────────┐    │
│  │ EKF2....... (très long)          │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

### 3.2 Copie le "Client ID"
- Garde-le de côté (tu en auras besoin)

### 3.3 Copie le "Secret"
- Garde-le de côté (tu en auras besoin)

> ⚠️ **NE JAMAIS** partage ces clés avec personne!

---

## ⏱️ ÉTAPE 4: Récupérer les Test Accounts (2 min)

### 4.1 En haut à gauche, clique sur "Sandbox" dans le menu

```
Dashboard → Sandbox → Accounts
```

### 4.2 Tu verras 2 comptes de test:
- **Business Account** (pour recevoir les paiements)
- **Personal Account** (pour tester les paiements)

```
Business Account:
  Email: sb-xxx@business.example.com
  Password: ~xxxxxx

Personal Account:
  Email: sb-xxx@personal.example.com
  Password: ~xxxxxx
```

Copie les 2 emails (tu en auras besoin pour tester plus tard).

---

## ⏱️ ÉTAPE 5: Configurer le .env (3 min)

Ajoute ces lignes à ton fichier `.env`:

```env
# PayPal Sandbox Configuration
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox  # Change à 'live' pour production
PAYPAL_API_URL=https://api-m.sandbox.paypal.com
```

**Exemple complet:**

```env
PAYPAL_CLIENT_ID=AeBz7rZZxxxxxyyy
PAYPAL_CLIENT_SECRET=EKF2xxxyyy
PAYPAL_MODE=sandbox
PAYPAL_API_URL=https://api-m.sandbox.paypal.com
```

---

## ⏱️ ÉTAPE 6: Configurer Django (5 min)

### 6.1 Installe le SDK PayPal

```bash
pip install paypalrestsdk
```

### 6.2 Crée le fichier de client PayPal

Crée `/workspaces/bnc/catalogue/payment_paypal.py`:

```python
import os
import logging
import paypalrestsdk

logger = logging.getLogger(__name__)

class PayPalClient:
    """Client pour interactions avec l'API PayPal"""
    
    def __init__(self):
        # Configuration PayPal
        paypalrestsdk.configure({
            'mode': os.getenv('PAYPAL_MODE', 'sandbox'),
            'client_id': os.getenv('PAYPAL_CLIENT_ID'),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
        })
        
        self.api_url = os.getenv('PAYPAL_API_URL', 
                                 'https://api-m.sandbox.paypal.com')
        
    def create_payment(self, amount, currency, description, 
                      return_url, cancel_url, order_id=None):
        """
        Crée un paiement PayPal
        
        Returns:
            (success: bool, approval_url: str, payment_id: str)
        """
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency,
                        "details": {
                            "subtotal": str(amount)
                        }
                    },
                    "description": description,
                    "invoice_number": order_id or f"ORDER-{int(order_id)}"
                }]
            })
            
            if payment.create():
                logger.info(f"Payment created: {payment.id}")
                
                # Récupère l'URL d'approbation
                approval_url = None
                for link in payment.links:
                    if link.rel == 'approval_url':
                        approval_url = link.href
                        break
                
                return True, approval_url, payment.id
            else:
                logger.error(f"Payment creation failed: {payment.error}")
                return False, None, None
                
        except Exception as e:
            logger.error(f"PayPal error: {str(e)}")
            return False, None, None
    
    def execute_payment(self, payment_id, payer_id):
        """
        Exécute un paiement après l'approbation
        
        Returns:
            (success: bool, transaction_id: str)
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logger.info(f"Payment executed: {payment.id}")
                
                # Récupère l'ID de transaction
                transaction_id = None
                if payment.transactions and len(payment.transactions) > 0:
                    transaction_id = payment.transactions[0].related_resources[0].sale.id
                
                return True, transaction_id
            else:
                logger.error(f"Payment execution failed: {payment.error}")
                return False, None
                
        except Exception as e:
            logger.error(f"PayPal execution error: {str(e)}")
            return False, None
    
    def get_payment_details(self, payment_id):
        """Récupère les détails d'un paiement"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return {
                'id': payment.id,
                'state': payment.state,
                'amount': payment.transactions[0].amount.total,
                'currency': payment.transactions[0].amount.currency,
            }
        except Exception as e:
            logger.error(f"Error getting payment details: {str(e)}")
            return None


def initiate_paypal_payment(amount, currency, description, 
                           return_url, cancel_url, order_id=None):
    """
    Fonction de commodité pour initier un paiement PayPal
    
    Usage:
        success, approval_url, payment_id = initiate_paypal_payment(
            amount=Decimal('100.00'),
            currency='USD',
            description='Book purchase',
            return_url='https://yourdomain.com/paypal/success/',
            cancel_url='https://yourdomain.com/paypal/cancel/',
            order_id='ORDER-12345'
        )
        
        if success:
            return redirect(approval_url)
    """
    client = PayPalClient()
    return client.create_payment(amount, currency, description, 
                                 return_url, cancel_url, order_id)
```

---

## ⏱️ ÉTAPE 7: Webhook PayPal (3 min)

Crée `/workspaces/bnc/catalogue/payment_paypal_webhook.py`:

```python
import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from catalogue.models import Order, Payment
from catalogue.payment_paypal import PayPalClient

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(['POST'])
def paypal_webhook(request):
    """
    Webhook pour les notifications PayPal
    
    Endpoint: POST /api/webhooks/paypal/
    """
    try:
        # Parse JSON
        data = json.loads(request.body)
        event_type = data.get('event_type')
        
        logger.info(f"PayPal webhook received: {event_type}")
        
        if event_type == 'CHECKOUT.ORDER.COMPLETED':
            _process_payment_success(data)
        elif event_type == 'CHECKOUT.ORDER.PAYMENT_APPROVED':
            _process_payment_approved(data)
        
        return JsonResponse({'status': 'success'}, status=200)
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def _process_payment_success(data):
    """Traite le paiement réussi"""
    try:
        resource = data.get('resource', {})
        payment_id = resource.get('id')
        invoice_number = resource.get('custom_id')
        
        # Trouve la commande
        try:
            order = Order.objects.get(id=invoice_number)
        except Order.DoesNotExist:
            logger.error(f"Order not found: {invoice_number}")
            return
        
        # Crée ou met à jour le paiement
        payment, created = Payment.objects.update_or_create(
            order=order,
            defaults={
                'amount': Decimal(resource.get('amount', {}).get('value', 0)),
                'currency': resource.get('amount', {}).get('currency_code', 'USD'),
                'status': 'COMPLETED',
                'transaction_id': payment_id,
                'payment_method': 'paypal'
            }
        )
        
        # Met à jour le statut de la commande
        order.payment_status = 'COMPLETED'
        order.save()
        
        logger.info(f"Payment completed: Order={order.id}, PaymentID={payment_id}")
        
        # Envoie email de confirmation (à implémenter)
        # send_payment_confirmation_email(order)
        
    except Exception as e:
        logger.error(f"Payment success processing error: {str(e)}")


def _process_payment_approved(data):
    """Traite le paiement approuvé (mais pas encore complété)"""
    logger.info(f"Payment approved: {data.get('resource', {}).get('id')}")
```

---

## ⏱️ ÉTAPE 8: Exemple d'Utilisation (2 min)

Utilise dans une vue Django:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import redirect
from django.http import JsonResponse
from decimal import Decimal
from catalogue.models import Order
from catalogue.payment_paypal import initiate_paypal_payment

class InitiatePayPalPaymentView(LoginRequiredMixin, View):
    """Vue pour initier un paiement PayPal"""
    
    def post(self, request):
        book_id = request.POST.get('book_id')
        
        # Crée une commande
        order = Order.objects.create(
            user=request.user,
            book_id=book_id,
            amount=Decimal('50.00'),
            payment_status='PENDING'
        )
        
        # Initie le paiement PayPal
        success, approval_url, payment_id = initiate_paypal_payment(
            amount=Decimal('50.00'),
            currency='USD',
            description=f'Book purchase',
            return_url=request.build_absolute_uri('/paypal/success/'),
            cancel_url=request.build_absolute_uri('/paypal/cancel/'),
            order_id=order.id
        )
        
        if success:
            # Redirige vers PayPal
            return redirect(approval_url)
        else:
            return JsonResponse({'error': 'Payment initiation failed'}, status=500)


class PayPalSuccessView(LoginRequiredMixin, View):
    """Vue appelée après le succès du paiement"""
    
    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        
        # Exécute le paiement
        client = PayPalClient()
        success, tx_id = client.execute_payment(payment_id, payer_id)
        
        if success:
            return JsonResponse({'message': 'Payment successful'})
        else:
            return JsonResponse({'error': 'Payment failed'}, status=500)
```

---

## 🧪 TESTER AVEC COMPTES SANDBOX (5 min)

### Utilise les comptes de test de l'ÉTAPE 4:

1. **Account Personnel** (pour tester les paiements)
   ```
   Email: sb-xxx@personal.example.com
   Password: ~xxxxxx
   ```

2. Quand tu es sur la page de paiement PayPal, connecte-toi avec ce compte

3. Complète le paiement de test

4. Tu devrais voir le paiement dans ta page "Transactions" du Dashboard

---

## ✅ Checklist de Configuration

- [ ] Compte créé sur https://developer.paypal.com/
- [ ] App Sandbox créée
- [ ] Client ID copié
- [ ] Client Secret copié
- [ ] Accounts de test notés
- [ ] Variables ajoutées au .env
- [ ] `pip install paypalrestsdk` exécuté
- [ ] `payment_paypal.py` créé
- [ ] `payment_paypal_webhook.py` créé
- [ ] URLs configurées
- [ ] Paiement de test exécuté ✅

---

## 📝 Prochaines Étapes

1. **Intégrer dans Django**
   ```bash
   python manage.py runserver
   ```

2. **Tester un paiement** avec un compte de test

3. **Vérifier les logs** pour les détails du paiement

4. **Pour la Production (JAN 1)**
   - Changer `PAYPAL_MODE=live`
   - Utiliser les vrais Client ID et Secret
   - Ajouter les bonnes URLs de webhook

---

## 🆘 Dépannage

### "Client ID not configured"
```
Solution: Ajoute PAYPAL_CLIENT_ID au .env
```

### "Payment creation failed"
```
Solution: Vérife les URLs return_url et cancel_url sont valides
```

### "Webhook not received"
```
Solution: Ajoute l'URL webhook au dashboard PayPal:
  Settings → Webhook Endpoints → Add Endpoint
  URL: https://yourdomain.com/api/webhooks/paypal/
```

---

**Fin! Tu peux maintenant accepter des paiements PayPal! 🎉**
