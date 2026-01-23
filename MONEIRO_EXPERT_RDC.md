# 🔥 Moneiro Paiement - Expert RDC (Minimaliste & Prêt)

## ⚡ Setup (5 min)

### 1. Modèle Commande
```python
# models.py - ajoute ceci ou importe de models_commande.py

class Commande(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, default='USD')  # USD ou CDF
    est_payee = models.BooleanField(default=False)
    methode_paiement = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='PENDING')
```

### 2. .env
```env
MONEIRO_API_KEY=ton_api_key
MONEIRO_MERCHANT_ID=ton_merchant_id
MONEIRO_API_SECRET=ton_api_secret
MONEIRO_API_URL=https://api.moneiro.com/v1
```

### 3. URLs
```python
# Dans urls.py principal:
path('', include('catalogue.urls_moneiro')),
```

### 4. Migration
```bash
python manage.py migrate
```

---

## 💰 Utilisation - 3 Étapes

### ÉTAPE 1: Form HTML (Sélectionner méthode de paiement)
```html
<form method="POST" action="/process-payment/">
    {% csrf_token %}
    
    <!-- Montant -->
    <input type="number" name="montant" value="100.00" required>
    
    <!-- Devise -->
    <select name="devise" required>
        <option value="USD">Dollar</option>
        <option value="CDF">Franc Congolais</option>
    </select>
    
    <!-- Méthode paiement -->
    <select name="methode_paiement" required>
        <option value="mpesa">M-Pesa</option>
        <option value="orange_money">Orange Money</option>
        <option value="airtel_money">Airtel Money</option>
        <option value="visa">Visa</option>
        <option value="mastercard">Mastercard</option>
    </select>
    
    <!-- Références -->
    <input type="hidden" name="reference" value="COMMANDE-{{ timestamp }}">
    <input type="hidden" name="book_id" value="{% book.id %}">
    <input type="text" name="phone" placeholder="+243...">
    
    <button type="submit">Payer avec Moneiro</button>
</form>
```

### ÉTAPE 2: Vue process_payment (AUTOMATIQUE)
```
✅ POST /process-payment/
✅ Crée commande en BDD
✅ Appelle API Moneiro
✅ Redirige vers page paiement Moneiro
```

### ÉTAPE 3: Webhook (AUTOMATIQUE)
```
✅ POST /webhook-moneiro/
✅ Reçoit confirmation de Moneiro
✅ Met à jour: Commande.est_payee = True
✅ Accorde accès au livre
✅ Envoie email confirmation
```

---

## 🎯 Exemple Complet

### View (Django)
```python
from django.shortcuts import render
from catalogue.models_commande import Commande

def shop_book(request, book_id):
    book = Book.objects.get(id=book_id)
    
    context = {
        'book': book,
        'montant': book.prix,
        'devise': 'USD',  # ou déterminé dynamiquement
    }
    
    return render(request, 'shop/payment_form.html', context)
```

### Template
```html
{% extends "base.html" %}

{% block content %}
<div class="payment-container">
    <h2>Acheter: {{ book.title }}</h2>
    <p>Prix: {{ montant }} {{ devise }}</p>
    
    <form method="POST" action="/process-payment/">
        {% csrf_token %}
        <input type="hidden" name="montant" value="{{ montant }}">
        <input type="hidden" name="devise" value="{{ devise }}">
        <input type="hidden" name="book_id" value="{{ book.id }}">
        <input type="hidden" name="reference" value="BNC-{{ book.id }}-{{ request.user.id }}-{{ now|date:'YmdHis' }}">
        
        <select name="methode_paiement" required>
            <option value="">-- Choisir méthode --</option>
            <option value="mpesa">📱 M-Pesa</option>
            <option value="orange_money">🍊 Orange Money</option>
            <option value="airtel_money">🔴 Airtel Money</option>
            <option value="visa">💳 Visa</option>
            <option value="mastercard">💳 Mastercard</option>
        </select>
        
        <input type="tel" name="phone" placeholder="+243123456789">
        
        <button type="submit">Procéder au paiement</button>
    </form>
</div>
{% endblock %}
```

---

## 🔍 Vérifier le Statut d'une Commande

```python
# Vue pour checker si payée
def check_payment_status(request, reference):
    commande = Commande.objects.get(reference=reference)
    
    return JsonResponse({
        'reference': reference,
        'est_payee': commande.est_payee,
        'status': commande.status,
        'montant': commande.montant,
        'devise': commande.devise,
    })
```

---

## 🚨 Erreurs Courantes

### "MONEIRO_API_KEY not set"
✅ Ajoute à `.env`:
```
MONEIRO_API_KEY=xxx
MONEIRO_MERCHANT_ID=xxx
MONEIRO_API_SECRET=xxx
```

### "Méthode invalide"
✅ Utilise uniquement:
- `mpesa`
- `orange_money`
- `airtel_money`
- `visa`
- `mastercard`

### "Webhook pas reçu"
✅ Moneiro doit avoir:
```
URL: https://tondomaine.com/webhook-moneiro/
Événements: payment.success, payment.failed
```

---

## 📊 Flux Complet

```
1. Utilisateur choisit livre + méthode
   ↓
2. POST /process-payment/
   ↓
3. Django crée Commande (PENDING)
   ↓
4. Appelle Moneiro API
   ↓
5. Redirection vers Moneiro (paiement)
   ↓
6. Utilisateur complète paiement
   ↓
7. Moneiro POST /webhook-moneiro/
   ↓
8. Django update Commande (SUCCESS)
   ↓
9. Accès livre accordé + Email envoyé
   ↓
10. User redirigé vers /paiement-succes/
```

---

## 🔐 Sécurité

✅ Credentials stockées dans `.env`
✅ Validation montant/devise côté serveur
✅ Webhook @csrf_exempt (nécessaire pour externe)
✅ Try/except sur toutes les API calls
✅ Logging de toutes les transactions

---

## ✅ Checklist Avant Production

- [ ] MONEIRO_API_KEY configurée
- [ ] MONEIRO_MERCHANT_ID configurée
- [ ] MONEIRO_API_SECRET configurée
- [ ] URLs incluses dans urls.py
- [ ] Modèle Commande migré
- [ ] Webhook URL configurée dans Moneiro
- [ ] Email SMTP configuré (optionnel)
- [ ] Tests avec transactions de test

---

## 📞 Support

Voir `payment_moneiro.py` pour API client complet (si besoin)

Code scannable ✅
Minimaliste ✅
Prêt à l'emploi ✅
**RDC optimisé** ✅
