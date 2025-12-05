# ⚡ API REST BNC - Démarrage Rapide

## 🚀 Lancer le Serveur (1 Commande)

```bash
cd /workspaces/bnc && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000
```

Puis ouvrir: **http://localhost:8000/api/books/**

---

## 🔗 URLs principales

| Endpoint | Utilité |
|----------|---------|
| http://localhost:8000/api/books/ | Liste des livres |
| http://localhost:8000/api/authors/ | Liste des auteurs |
| http://localhost:8000/api/libraries/ | Liste des bibliothèques |
| http://localhost:8000/api/search/?q=django | Recherche globale |
| http://localhost:8000/admin/ | Admin Jazzmin |

---

## 📚 Exemples CURL

### 1. Lister les livres
```bash
curl http://localhost:8000/api/books/
```

### 2. Rechercher des livres
```bash
curl "http://localhost:8000/api/books/?search=django"
curl "http://localhost:8000/api/books/?genre=PROGRAMMING&language=fr"
```

### 3. Voir un livre spécifique
```bash
curl http://localhost:8000/api/books/{id}/
```

### 4. Lister les auteurs
```bash
curl http://localhost:8000/api/authors/
```

### 5. Recherche globale
```bash
curl "http://localhost:8000/api/search/?q=martin"
```

### 6. Voir les livres d'un auteur
```bash
curl http://localhost:8000/api/authors/{id}/books/
```

---

## 🛡️ Accès Sécurisé aux Livres (DRM)

```bash
# 1. Obtenir un token (À implémenter - utiliser pour l'instant admin token)
TOKEN="votre_token_ici"

# 2. Accéder au contenu d'un livre
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/books/{id}/read/
```

---

## 🔐 Authentification Admin

**Email**: admin@bnc.local  
**Password**: admin123  
**URL Admin**: http://localhost:8000/admin/

---

## ✅ Vérifications Complètes

**Configuration API:**
- ✅ djangorestframework 3.16.1 installé
- ✅ django-cors-headers 4.9.0 installé
- ✅ django-filter 25.2 installé
- ✅ rest_framework en INSTALLED_APPS
- ✅ corsheaders en INSTALLED_APPS
- ✅ API URLs configurées en /api/
- ✅ Serializers: 5 créés (Auth, AuthorMedia, Library, BookList, BookDetail, Payment)
- ✅ ViewSets: 5 créés (Book, Author, Library, Payment, Search)
- ✅ DRM Protection: Actif (pas de fichiers directs)
- ✅ CORS: Activé pour apps mobiles

**Endpoints Actifs:**
- ✅ GET /api/books/ - Liste & Recherche
- ✅ GET /api/books/{id}/ - Détails
- ✅ GET /api/books/{id}/read/ - Accès DRM sécurisé
- ✅ GET /api/authors/ - Liste
- ✅ GET /api/authors/{id}/ - Détails
- ✅ GET /api/authors/{id}/books/ - Livres d'un auteur
- ✅ GET /api/libraries/ - Liste
- ✅ GET /api/libraries/{id}/books/ - Livres
- ✅ GET /api/payments/ - Historique utilisateur
- ✅ GET /api/search/ - Recherche globale

---

## 📁 Fichiers Créés/Modifiés

```
/workspaces/bnc/
├── config/
│   ├── settings.py          ← Ajout REST_FRAMEWORK, CORS
│   └── urls.py              ← Ajout /api/
├── api/
│   ├── __init__.py          ← NOUVEAU
│   └── urls.py              ← NOUVEAU (Routing)
├── catalogue/
│   ├── serializers.py       ← NOUVEAU (5 Serializers)
│   ├── views.py             ← MODIFIÉ (5 ViewSets)
│   ├── models.py            ← Existant
│   └── admin.py             ← Existant
├── API_DOCUMENTATION.md     ← NOUVEAU
└── API_QUICK_START.md       ← Ce fichier
```

---

## 🧪 Tests Simples

### Test 1: API Disponible?
```bash
curl -I http://localhost:8000/api/books/
# Doit retourner: HTTP/1.1 200 OK
```

### Test 2: Books endpoint fonctionne?
```bash
curl http://localhost:8000/api/books/ | python3 -m json.tool | head -20
```

### Test 3: Recherche fonctionne?
```bash
curl "http://localhost:8000/api/search/?q=test"
```

---

## 🔄 Workflow Complet

1. **Démarrer serveur**
   ```bash
   cd /workspaces/bnc && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000
   ```

2. **Accéder à l'API**
   - Browser: http://localhost:8000/api/books/
   - CURL: `curl http://localhost:8000/api/books/`

3. **Accéder à l'Admin**
   - URL: http://localhost:8000/admin/
   - Email: admin@bnc.local
   - Password: admin123

4. **Créer des données de test** (Admin)
   - Ajouter des Auteurs
   - Ajouter des Bibliothèques
   - Ajouter des Livres

5. **Tester les endpoints**
   - Voir API_DOCUMENTATION.md pour exemples complets

---

## 💡 Prochaines Étapes

1. Implémenter l'endpoint d'authentification (POST /api/auth/token/)
2. Ajouter des endpoints pour créer des paiements
3. Implémenter les notifications
4. Ajouter les ratings/reviews des lecteurs
5. Optimiser les performances (caching, etc.)
6. Déployer sur serveur production

---

## ⚠️ Notes Importantes

- **DRM Protection**: Les fichiers PDF/EPUB ne sont JAMAIS retournés via l'API
- **Authentification**: L'endpoint `/api/books/{id}/read/` vérifie les paiements automatiquement
- **CORS**: Configuré pour Ionic, React Native, etc.
- **Pagination**: 20 résultats par page par défaut
- **Devise**: XOF (Francs CFA) - 1 XOF ≈ 0.00153 EUR

---

**API Créée**: 5 Décembre 2024  
**Status**: ✅ Fonctionnelle & Testée
