# ✅ CHECKLIST DÉPLOIEMENT PRODUCTION

**Date:** 23 Décembre 2025  
**Version:** 2.0.0  
**Status:** 🟢 Production-Ready

---

## 🔒 SÉCURITÉ

- [ ] `DEBUG = False` dans settings
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] `SECRET_KEY` changé et stocké en env
- [ ] HTTPS/SSL activé et forcé (`SECURE_SSL_REDIRECT = True`)
- [ ] Cookies sécurisés (`SESSION_COOKIE_SECURE = True`)
- [ ] CSRF Protection active
- [ ] CORS configuré correctement
- [ ] Headers de sécurité ajoutés (X-Frame-Options, etc)
- [ ] Rate limiting en place
- [ ] Input validation et sanitization
- [ ] SQL Injection prevention (ORM Django)
- [ ] XSS Protection (templates auto-escaped)
- [ ] CSRF tokens sur tous les formulaires

## 🗄️ DATABASE

- [ ] PostgreSQL en production (pas SQLite)
- [ ] Backups automatiques configurés
- [ ] Replication/Standby si possible
- [ ] Connection pooling (pgBouncer)
- [ ] Migrations appliquées: `python manage.py migrate`
- [ ] Indexes créés pour performance
- [ ] Vacuum/Analyze planifiés (cron)
- [ ] Logs de slow queries monitored

## 💳 PAIEMENTS

### Stripe
- [ ] `STRIPE_API_KEY` en mode LIVE (pas test)
- [ ] `STRIPE_PUBLISHABLE_KEY` correct
- [ ] `STRIPE_WEBHOOK_SECRET` configuré
- [ ] Webhook endpoint sécurisé (`/api/webhooks/stripe/`)
- [ ] HTTPS forcé sur webhook
- [ ] Signature verification implémentée
- [ ] Tests avec montants réels
- [ ] Monitoring transactions actif

### PayPal
- [ ] `PAYPAL_MODE = 'live'` (pas sandbox)
- [ ] `PAYPAL_CLIENT_ID` et `PAYPAL_CLIENT_SECRET`
- [ ] Webhook configuré dans Dashboard PayPal
- [ ] Return URLs correctes
- [ ] Tests transactions

### Airtel Money
- [ ] Credentials récupérés
- [ ] Endpoint production configuré
- [ ] Callback URL sécurisée
- [ ] Tests avec montants réels

### M-Pesa
- [ ] Consumer key/secret
- [ ] Shortcode correct
- [ ] Passkey configuré
- [ ] Endpoint production
- [ ] STK push configuré

### Orange Money
- [ ] API keys production
- [ ] Endpoint production
- [ ] Webhook configuré
- [ ] Tests

## 🌐 VARIABLES D'ENVIRONNEMENT

- [ ] `.env` NOT commité (dans `.gitignore`)
- [ ] Tous les `os.getenv()` ont des défauts sensés
- [ ] Variables testées en prod
- [ ] Rotation des secrets planifiée

**Required:**
```
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...
STRIPE_API_KEY=sk_live_...
SITE_URL=https://yourdomain.com
```

## ⚙️ INFRASTRUCTURE

- [ ] Server: Digital Ocean, AWS, Heroku, etc.
- [ ] Firewall configuré
- [ ] DDoS protection active
- [ ] SSL Certificate (Let's Encrypt)
- [ ] DNS records corrects
- [ ] Email SMTP configuré
- [ ] Backup service active
- [ ] CDN configuré (CloudFlare, etc)
- [ ] Load balancer si multi-instance

## 📦 STATIC FILES

- [ ] Collectés: `python manage.py collectstatic --noinput`
- [ ] Servus par CDN ou serveur web
- [ ] Cache headers optimisés
- [ ] Compression (gzip) active
- [ ] Minification CSS/JS
- [ ] Images optimisées

## 🌍 TRADUCTIONS

- [ ] Compilées: `./scripts/manage_translations.sh compile`
- [ ] Fichiers .mo présents en production
- [ ] Langues supportées testées
- [ ] Fallback language configuré

## 📱 OFFLINE/PWA

- [ ] Service Worker enregistré dans HTML
- [ ] `manifest.json` configuré
- [ ] Icons pour PWA (192x192, 512x512)
- [ ] Offline page créée
- [ ] IndexedDB schemas définis
- [ ] Service Worker testé hors-ligne

## 📊 MONITORING & LOGGING

- [ ] Logger configuré (Sentry/ELK)
- [ ] Error tracking actif
- [ ] Performance monitoring actif
- [ ] Application monitoring (APM)
- [ ] Log aggregation en place
- [ ] Alertes configurées
- [ ] Dashboard de santé en place

## 🚀 PERFORMANCE

- [ ] Database queries optimisées
- [ ] N+1 queries corrigées
- [ ] Caching Redis configuré
- [ ] Cache timeout approprié
- [ ] Static files cached navigateur
- [ ] Lazy loading des images
- [ ] CSS/JS bundled
- [ ] Time to First Byte < 1s
- [ ] Lighthouse score > 80

## 🧪 TESTS

- [ ] Tests unitaires passent: `python manage.py test`
- [ ] Tests d'intégration OK
- [ ] Tests de paiement (sandbox/test modes)
- [ ] Tests hors-ligne (Service Worker)
- [ ] Tests mobile (responsive)
- [ ] Tests de charge si nécessaire

## 📝 DOCUMENTATION

- [ ] README mis à jour
- [ ] API documentation complète
- [ ] Deployment guide écrit
- [ ] Runbook pour opérations
- [ ] Troubleshooting guide
- [ ] Architecture diagram
- [ ] Database schema documented

## 🔑 OAUTH (optionnel)

- [ ] Google OAuth `GOOGLE_OAUTH_CLIENT_ID` et `SECRET`
- [ ] Redirect URI configuré correctement
- [ ] Scope permissions minimal
- [ ] Tests login Google

## ✉️ EMAIL

- [ ] SMTP configuré
- [ ] From address correct
- [ ] HTML templates testées
- [ ] Transactional emails (confirmation, reset, etc)
- [ ] Unsubscribe links si marketing

## 📋 DOMAIN & DNS

- [ ] Domaine acheté et pointé
- [ ] DNS A record correct
- [ ] Mail records (MX) si email
- [ ] SPF record configuré
- [ ] DKIM record configuré
- [ ] DMARC record configuré

## 🎯 FINAL CHECKS

- [ ] Tester depuis mobile (iOS + Android)
- [ ] Tester PDF reader complètement
- [ ] Tester paiement end-to-end
- [ ] Tester offline mode (mode avion)
- [ ] Tester recherche
- [ ] Tester recommandations
- [ ] Tester traductions (changer langue)
- [ ] Vérifier SEO basique
- [ ] Tester contact/support form
- [ ] Vérifier analytics tracé

## 🚨 INCIDENT RESPONSE

- [ ] Procédure de rollback définie
- [ ] Contacts d'urgence en place
- [ ] Runbook d'incidents écrit
- [ ] Escalation path définie
- [ ] Communication plan en cas de panne

## 📅 POST-DEPLOYMENT

- [ ] Monitoring 24/7 les 48 premières heures
- [ ] Check alertes et logs quotidiennement
- [ ] User feedback monitoring
- [ ] Performance metrics tracking
- [ ] Incident log tenu à jour

---

## 📊 DÉPLOIEMENT AVEC DOCKER

```bash
# Build
docker build -t bnc:latest .

# Run
docker run -d \
  --name bnc \
  -p 80:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  bnc:latest

# Migrations
docker exec bnc python manage.py migrate

# Collectstatic
docker exec bnc python manage.py collectstatic --noinput
```

## 📊 DÉPLOIEMENT AVEC HEROKU

```bash
# Login
heroku login

# Create app
heroku create bnc-prod

# Configure environment
heroku config:set DEBUG=False SECRET_KEY=xxx DATABASE_URL=xxx

# Deploy
git push heroku main

# Migrations
heroku run python manage.py migrate

# Collectstatic
heroku run python manage.py collectstatic --noinput
```

## 📊 DÉPLOIEMENT MANUEL

```bash
# SSH to server
ssh user@server.com

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Collectstatic
python manage.py collectstatic --noinput

# Compile translations
./scripts/manage_translations.sh compile

# Restart service
sudo systemctl restart bnc

# Check status
sudo systemctl status bnc
```

## 🔍 VERIFICATION CHECKLIST

- [ ] Site accessible sur domaine
- [ ] HTTPS fonctionne (pas d'avertissements)
- [ ] Admin `/admin/` accessible
- [ ] API endpoints répondent
- [ ] PDFs lisibles
- [ ] Paiements processent
- [ ] Emails envoient
- [ ] Logs write correctement
- [ ] Backups run
- [ ] Monitoring actif

---

**À compléter avant chaque déploiement production**

**Checkpoints:**
- [ ] Pre-deployment (avant PR)
- [ ] Staging (branche staging)
- [ ] Production (main branch)

**Validé par:** _____________  
**Date:** _____________  
**Notes:** _____________

---

*Dernière mise à jour: 23 Décembre 2025*
