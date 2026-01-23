# 🚀 Guide de Déploiement Mobile Money en Production

## Vue d'ensemble
Ce guide explique comment déployer le système de paiement Mobile Money Flutterwave en production avec les 4 réseaux RDC (Airtel, Orange, Vodacom, Moov Money).

---

## ✅ Étapes complétées
- ✅ **Étape 1** - Tester le flux (mode démo)
- ✅ **Étape 2** - Obtenir les clés Flutterwave
- ✅ **Étape 3** - Ajouter le bouton "Acheter" dans le catalogue
- ✅ **Étape 4** - Tester avec vrais numéros RDC (tous les 4 réseaux)
- 🔄 **Étape 5** - Déployer en production (EN COURS)

---

## 📋 Étape 5: Déploiement en Production

### 5.1 Configuration des clés API Flutterwave

Obtenez vos clés depuis https://dashboard.flutterwave.com :

```bash
# Option A: Via fichier .env
FLUTTERWAVE_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxx
FLUTTERWAVE_SECRET_KEY=sk_live_xxxxxxxxxxxxxx
FLUTTERWAVE_ENVIRONMENT=production
```

ou

```bash
# Option B: Directement dans config/settings.py
FLUTTERWAVE_PUBLIC_KEY = 'pk_live_xxxxxxxxxxxxxx'
FLUTTERWAVE_SECRET_KEY = 'sk_live_xxxxxxxxxxxxxx'
FLUTTERWAVE_ENVIRONMENT = 'production'
```

### 5.2 Vérifier la configuration

```bash
python manage.py shell
>>> from catalogue.payment_mobilemoney import flutterwave
>>> flutterwave.check_configuration()
# Devrait afficher: ✅ Flutterwave configured for production
```

### 5.3 Activer les webhooks Flutterwave

Dans le tableau de bord Flutterwave:
1. Aller à **Settings → Webhooks**
2. Ajouter l'URL: `https://votre-domaine.com/mobilemoney/webhook/`
3. Sélectionner les événements:
   - `charge.completed`
   - `charge.failed`
   - `transaction.completed`

### 5.4 Exécuter les migrations

```bash
python manage.py migrate catalogue
```

### 5.5 Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 5.6 Redémarrer le serveur

```bash
# Via systemd
sudo systemctl restart bnc

# Ou via gunicorn
gunicorn config.wsgi:application --reload
```

### 5.7 Tester en production

Accéder à: `https://votre-domaine.com/catalogue/`

1. ✅ Voir le bouton "Acheter" sur les livres
2. ✅ Cliquer sur "Acheter"
3. ✅ Sélectionner un réseau (Airtel, Orange, Vodacom, Moov)
4. ✅ Entrer un numéro RDC valide
5. ✅ Confirmer le paiement sur le téléphone
6. ✅ Voir la page de succès

---

## 🔒 Points de sécurité

### 1. HTTPS obligatoire
```bash
# config/settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Clés secrètes en variables d'environnement
```bash
# Ne JAMAIS commiter les clés secrètes!
export FLUTTERWAVE_SECRET_KEY='sk_live_xxxxxx'
```

### 3. Validation des webhooks
```python
# catalogue/mobilemoney_views.py ligne 295
# Vérifier la signature du webhook
import hashlib

def verify_webhook_signature(payload, signature):
    secret = settings.FLUTTERWAVE_SECRET_KEY
    computed = hashlib.sha256(
        (payload + secret).encode()
    ).hexdigest()
    return computed == signature
```

### 4. CSRF Protection
```html
<!-- Tous les formulaires incluent {% csrf_token %} -->
<form method="POST">
    {% csrf_token %}
    <!-- ... -->
</form>
```

---

## 📊 Monitoring en Production

### 1. Logs des paiements
```bash
# Voir les paiements échoués
python manage.py shell
>>> from catalogue.models import Payment
>>> Payment.objects.filter(status='failed').count()
```

### 2. Alertes
```python
# Envoyer une alerte si trop d'échecsdictates
from django.core.mail import send_mail

failed_count = Payment.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timedelta(hours=1)
).count()

if failed_count > 10:
    send_mail(
        '⚠️ Paiements: Taux d\'échec anormal',
        f'{failed_count} paiements ont échoué dans la dernière heure',
        'admin@example.com',
        ['support@example.com']
    )
```

### 3. Métriques de succès
```python
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

# Taux de succès des 24 dernières heures
last_24h = timezone.now() - timedelta(hours=24)
total = Payment.objects.filter(created_at__gte=last_24h).count()
successful = Payment.objects.filter(
    created_at__gte=last_24h,
    status='completed'
).count()
success_rate = (successful / total * 100) if total > 0 else 0
print(f"✅ Taux de succès: {success_rate:.1f}%")
```

---

## 🧪 Checklist de déploiement

### Avant le lancement
- [ ] Clés Flutterwave obtenues et testées
- [ ] HTTPS configuré
- [ ] Webhooks Flutterwave configurés
- [ ] Migrations exécutées
- [ ] Fichiers statiques collectés
- [ ] Tests de bout en bout passés
- [ ] Configuration de monitoring mise en place

### Après le lancement
- [ ] Surveiller les paiements pendant 24h
- [ ] Vérifier les taux de succès
- [ ] Tester avec de vrais montants
- [ ] Documenter les logs d'erreur

---

## 🆘 Dépannage

### Problème: "Flutterwave keys not configured"
**Solution**: Vérifier que `FLUTTERWAVE_SECRET_KEY` est défini dans `.env` ou `settings.py`

### Problème: "Numéro de téléphone invalide"
**Solution**: Utiliser le format RDC: `+243XXXXXXXXXX` (10 chiffres après +243)

### Problème: Webhook non reçu
**Solution**: 
1. Vérifier l'URL du webhook dans Flutterwave
2. Vérifier les logs du serveur: `tail -f /var/log/bnc/error.log`
3. Tester manuellement: `curl -X POST https://votre-domaine.com/mobilemoney/webhook/`

### Problème: Paiement bloqué pour dépassement de montant
**Solution**: Vérifier les limites par réseau:
- **Airtel**: $100 - $500,000
- **Orange**: $100 - $500,000
- **Vodacom**: $100 - $500,000
- **Moov**: $50 - $300,000

---

## 📱 Réseaux supportés

| Réseau | Format | Min | Max | Confirmé ✅ |
|--------|--------|-----|-----|-----------|
| Airtel Money | +243 812-999-XXXX | $100 | $500,000 | ✅ |
| Orange Money | +243 898-899-XXXX | $100 | $500,000 | ✅ |
| Vodacom M-Pesa | +243 811-818-XXXX | $100 | $500,000 | ✅ |
| Moov Money | +243 899-XXXXXX | $50 | $300,000 | ✅ |

---

## 📞 Support Flutterwave

- **Documentation**: https://developer.flutterwave.com/
- **Support**: support@flutterwave.com
- **Statut**: https://status.flutterwave.com/

---

## 📝 Fichiers modifiés pour cette intégration

1. **catalogue/payment_mobilemoney.py** - Gateway Flutterwave
2. **catalogue/mobilemoney_views.py** - Vues de paiement
3. **catalogue/mobilemoney_urls.py** - URLs du flux
4. **templates/payment/mobilemoney_flow.html** - Formulaire de paiement
5. **templates/payment/mobilemoney_confirmation.html** - Page de confirmation
6. **templates/payment/mobilemoney_success.html** - Page de succès
7. **templates/payment/pure_payment_modal.html** - Modal intégration
8. **config/urls.py** - Intégration des URLs

---

## 🎯 Prochaines étapes

Après déploiement:
1. Monitorer les paiements en production
2. Analyser les logs d'erreur
3. Optimiser les taux de conversion
4. Ajouter d'autres méthodes de paiement si needed

---

**Déploiement réalisé le**: {{ deployment_date }}
**État**: 🚀 Production-Ready (mode démo activé)

