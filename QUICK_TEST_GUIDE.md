# 🚀 GUIDE RAPIDE DE TEST - BNC Application

**Date:** 17 Décembre 2025  
**Version:** 1.0  

---

## 🎯 DÉMARRAGE RAPIDE

### 1. Activation Environnement
```bash
cd /workspaces/bnc
source venv/bin/activate
```

### 2. Lancer le Serveur
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Accès aux Interfaces
```
🏠 Frontend:        http://localhost:8000/
🔐 Admin Jazzmin:   http://localhost:8000/admin/
📡 API REST:        http://localhost:8000/api/
```

---

## 👤 COMPTES DE TEST

### Admin (Complet)
- **Email:** `admin@bnc.local`
- **Password:** `admin123`
- **Rôle:** SUPER_ADMIN
- **Accès:** Tout (Admin, API, Frontend)

### Lecteur Exemple
- **Email:** `reader@bnc.local`
- **Password:** `reader123` (à créer via signup)
- **Rôle:** READER
- **Accès:** Frontend uniquement, pas d'admin

---

## 🧪 TESTS À EFFECTUER

### A. **Authentification**
```
1. Aller à http://localhost:8000
2. Cliquer "Inscription"
3. Remplir formulaire
4. Confirmer création de compte
5. Se connecter avec les identifiants
```

### B. **Catalogue**
```
1. Accueil → Voir livres en vedette
2. Cliquer "Catalogue"
3. Filtrer par genre/langue
4. Rechercher un livre
5. Cliquer sur un livre pour détails
```

### C. **Lecteur Livre**
```
IMPORTANT: Ajouter d'abord un livre gratuit via Admin

1. Admin → Catalogue → Books
2. Créer/éditer un livre: is_paid=False
3. Upload PDF ou EPUB
4. Publier (is_published=True)
5. Retour Frontend → Catalogue
6. Cliquer livre → "Lire en ligne"
7. Tester: navigation, zoom, sidebar notes
```

### D. **Achat Livre**
```
1. Admin → Book: Créer livre payant (is_paid=True, price=5000)
2. Frontend → Catalogue → Livre payant
3. Cliquer "Acheter"
4. Vérifier paiement créé
5. Admin → Payments: Voir paiement PENDING
6. Modifier statut → COMPLETED
7. Retour Frontend: Livre maintenant lisible
```

### E. **Profil Utilisateur**
```
1. Connecté → Menu profil
2. Cliquer "Mon Profil"
3. Éditer avatar, téléphone, etc.
4. Sauvegarder
5. Vérifier changements
```

### F. **Historique Lecture**
```
1. Connecté → "Historique"
2. Voir livres lus
3. Voir pages lues
4. Voir durée de lecture
```

### G. **API (avec cURL)**
```bash
# 1. Obtenir token (optionnel)
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@bnc.local","password":"admin123"}'

# 2. Lister livres publics
curl http://localhost:8000/api/books/

# 3. Lister critiques (auth optionnel)
curl http://localhost:8000/api/reviews/

# 4. Créer critique (auth REQUISE)
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book": "uuid-du-livre",
    "rating": 5,
    "title": "Excellent!",
    "content": "Really enjoyed this book"
  }'

# 5. Créer surlignage
curl -X POST http://localhost:8000/api/highlights/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book": "uuid-du-livre",
    "page_number": 42,
    "text": "Texte à surligner",
    "color": "#FFFF00"
  }'

# 6. Lister mes notes
curl http://localhost:8000/api/notes/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 🐛 DÉPANNAGE

### Erreur: "ModuleNotFoundError: No module named 'django'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Erreur: "Migrations pending"
```bash
python manage.py migrate
python manage.py makemigrations
```

### Port 8000 déjà utilisé
```bash
python manage.py runserver 8001
# Ou tuer le processus:
lsof -i :8000
kill -9 PID
```

### Problème staticfiles
```bash
python manage.py collectstatic --noinput
```

### Réinitialiser BD (ATTENTION: Supprime données)
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 POINTS DE CONTRÔLE

### Backend
- [ ] `python manage.py check` → 0 errors
- [ ] Serveur démarre sans erreurs
- [ ] Admin Jazzmin accessible
- [ ] API endpoints accessibles

### Frontend
- [ ] Homepage charge
- [ ] Formulaire login fonctionne
- [ ] Inscription possible
- [ ] Catalogue affiche livres
- [ ] Recherche/filtres fonctionnent
- [ ] Lecteur charge PDF/EPUB

### API
- [ ] GET /api/books/ → 200 OK
- [ ] GET /api/reviews/ → 200 OK
- [ ] POST /api/reviews/ (auth) → 201 Created
- [ ] PUT /api/notes/{id}/ (perso) → 200 OK
- [ ] DELETE /api/highlights/{id}/ (perso) → 204 No Content

---

## 📈 MÉTRIQUES DE TEST

```
✅ Modèles: 15 modèles Django
✅ Serializers: 11 serializers
✅ ViewSets: 8 ViewSets API
✅ Views: 10+ vues frontend
✅ URLs: 20+ routes
✅ Templates: 12+ templates
✅ Migrations: 5 migrations appliquées
✅ Code: 2000+ lignes
```

---

## 🎯 CHECKLIST FINAL

Avant déploiement, vérifier:

- [ ] Tous les tests passent
- [ ] Admin fonctionne
- [ ] Frontend responsive
- [ ] API documentée
- [ ] Pas d'erreurs console
- [ ] Pas de warnings de sécurité
- [ ] Performance acceptable
- [ ] Code formaté et documenté

---

## 📞 SUPPORT

Si problème:
1. Vérifier les logs Django
2. Vérifier la console navigateur (F12)
3. Vérifier les tables en Admin
4. Vérifier les migrations appliquées

---

**Bon testing! 🚀**
