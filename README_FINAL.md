# 📚 BNC - Bibliothèque Numérique Africaine

[![Django 6.0](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-orange)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

**BNC** est une plateforme africaine de distribution de livres numériques avec paiement sécurisé, lecteur PDF intégré, recommandations personnalisées, et support offline complet.

## 🎯 Caractéristiques Principales

- 📖 **Lecteur PDF moderne** - Scroll continu, zoom fluide, auto-retour page
- 💳 **5 méthodes de paiement** - Stripe, PayPal, Airtel Money, M-Pesa, Orange Money
- 🤖 **Recommandations ML** - Basées sur historique & lecteurs similaires
- 🔍 **Recherche avancée** - Par titre, auteur, éditeur, pays, genre
- 📱 **Mode offline (PWA)** - Lire sans connexion internet
- ✏️ **Annotations complètes** - Notes, surlignages, avis, citations
- 🌍 **Multilingue** - Français, anglais, arabe, portugais, swahili
- 📊 **Analytics** - Statistiques de lecture, genres préférés

## 🚀 Démarrage Rapide

### Pré-requis
- Python 3.12+
- PostgreSQL 14+
- Redis (optionnel, pour cache)

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-repo/bnc.git
cd bnc

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos API keys

# Migrations
python manage.py migrate

# Créer un super-utilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Accédez à: http://localhost:8000

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [PAYMENT_SETUP_GUIDE.md](PAYMENT_SETUP_GUIDE.md) | Configuration des paiements |
| [I18N_SETUP_GUIDE.md](I18N_SETUP_GUIDE.md) | Traductions multilingues |
| [CAHIER_DES_CHARGES_CONFORMITE.md](CAHIER_DES_CHARGES_CONFORMITE.md) | Status d'implémentation |
| [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) | Résumé des complétions |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API REST endpoints |

## 🏗️ Architecture

```
bnc/
├── config/              # Configuration Django
├── catalogue/           # App: Livres, auteurs, paiements
├── users/              # App: Utilisateurs, profils
├── api/                # App: API REST
├── templates/          # Templates HTML
├── static/             # Assets (CSS, JS, images)
├── manage.py           # CLI Django
└── requirements.txt    # Dépendances Python
```

### Apps Django

| App | Responsabilité |
|-----|-----------------|
| `catalogue` | Livres, auteurs, lecteur PDF, paiements, recommandations |
| `users` | Authentification, profils, historique |
| `api` | Endpoints REST pour mobile/frontend |

## 🔐 Variables d'Environnement

Voir [`.env.example`](.env.example) pour la liste complète:

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@localhost/bnc

# Payment Gateways
STRIPE_API_KEY=sk_live_...
PAYPAL_CLIENT_ID=...
AIRTEL_CLIENT_ID=...
MPESA_CONSUMER_KEY=...
ORANGE_MONEY_API_KEY=...

# OAuth
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_SECRET=...
```

## 💳 Intégration Paiements

**5 passerelles supportées:**

1. **Stripe** - Cartes internationales
   - `STRIPE_API_KEY` et `STRIPE_PUBLISHABLE_KEY`
   - Coût: 2.9% + $0.30

2. **PayPal** - Global
   - `PAYPAL_CLIENT_ID` et `PAYPAL_CLIENT_SECRET`
   - Coût: 3.49% + $0.49

3. **Airtel Money** - Afrique Ouest
   - `AIRTEL_CLIENT_ID`, `AIRTEL_CLIENT_SECRET`, `AIRTEL_PIN`
   - Coût: 2.5-3%

4. **M-Pesa** - Kenya/Afrique Est
   - `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`
   - Coût: 0.79%

5. **Orange Money** - RDC/Afrique Centrale
   - `ORANGE_MONEY_API_KEY`, `ORANGE_MONEY_API_SECRET`
   - Coût: 2-3%

Voir [PAYMENT_SETUP_GUIDE.md](PAYMENT_SETUP_GUIDE.md) pour détails complets.

## 🌍 Traductions

Gérer les traductions avec le script:

```bash
# Extraire les strings
./scripts/manage_translations.sh extract

# Compiler (après édition des .po)
./scripts/manage_translations.sh compile

# Mettre à jour
./scripts/manage_translations.sh update

# Voir statut
./scripts/manage_translations.sh status

# Ajouter une langue
./scripts/manage_translations.sh add es
```

Voir [I18N_SETUP_GUIDE.md](I18N_SETUP_GUIDE.md) pour guide complet.

## 📱 Mode Offline (PWA)

La plateforme supporte une utilisation **complètement offline**:

- 📖 Lire les PDFs téléchargés
- 📝 Consulter notes et surlignages
- 🔄 Synchronisation auto quand connexion revient

**Technologie:** Service Worker v2.0 + IndexedDB

## 🤖 Recommandations

L'algorithme combine **5 stratégies:**

1. **Content-based** - Genres préférés
2. **Author-based** - Auteurs favoris
3. **Popularity-based** - Livres bien notés
4. **Collaborative** - Lecteurs similaires
5. **Trending** - Populaire récemment

Endpoint: `GET /api/books/recommendations/?limit=10`

## 🔍 Recherche Avancée

```bash
# Recherche simple
GET /api/search/?q=harry

# Filtrer par éditeur
GET /api/search/?publisher=Penguin

# Filtrer par pays
GET /api/search/?country=France

# Combiner les filtres
GET /api/search/?q=harry&author=Rowling&genre=fantasy&min_price=5&max_price=50
```

## 🧪 Tests

```bash
# Lancer les tests
python manage.py test

# Avec coverage
coverage run --source='.' manage.py test
coverage report

# Tests spécifiques
python manage.py test catalogue.tests
```

## 🚀 Déploiement

### Production Checklist

- [ ] `DEBUG=False` dans settings
- [ ] Variables d'environnement configurées
- [ ] HTTPS/SSL activé
- [ ] Database: PostgreSQL en production
- [ ] Cache: Redis configuré
- [ ] Migrations appliquées
- [ ] Traductions compilées
- [ ] Static files collectés
- [ ] Webhooks paiements testés
- [ ] Logs configurés
- [ ] Backups automatiques

### Avec Docker

```bash
docker-compose up -d
```

### Avec Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📊 Statistiques

| Métrique | Valeur |
|----------|--------|
| **Lignes de code** | 50,000+ |
| **Endpoints API** | 80+ |
| **Models** | 25+ |
| **Templates** | 40+ |
| **Tests** | 100+ |
| **Documentation** | 1,000+ lignes |

## 🤝 Contribution

Les contributions sont bienvenues! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - Voir [LICENSE](LICENSE)

## 📞 Support

- **Issues:** GitHub Issues
- **Email:** support@bnc-digital.com
- **Docs:** https://docs.bnc-digital.com

## 🎉 Merci

BNC est construit avec ❤️ en Afrique pour servir le continent.

---

**Version:** 2.0.0  
**Dernière mise à jour:** 23 Décembre 2025  
**Status:** 🟢 Production-Ready pour 80% du cahier des charges
