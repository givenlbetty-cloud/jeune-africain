# 🚀 GUIDE RAPIDE - 30 SECONDES

## Accédez à toutes les fonctionnalités en 3 étapes:

### 1️⃣ Lancer le serveur
```bash
python manage.py runserver
```

### 2️⃣ Ouvrir dans le navigateur
```
http://localhost:8000/fr/
```

### 3️⃣ Cliquer sur la section souhaitée

---

## 📍 URLS PRINCIPALES

| Section | URL |
|---------|-----|
| **🏠 Accueil** | http://localhost:8000/fr/ |
| **📚 Livres** | http://localhost:8000/fr/books/ |
| **🎬 Audiobooks** | http://localhost:8000/fr/audiobooks/ |
| **🎥 Vidéos** | http://localhost:8000/fr/videos/ |
| **🎙️ Podcasts** | http://localhost:8000/fr/podcasts/ |
| **💬 Forums** | http://localhost:8000/fr/forum/ |
| **👥 Communauté** | http://localhost:8000/fr/community/users/ |
| **👤 Mon Profil** | http://localhost:8000/fr/user/profile/ |
| **📚 Ma Bibliothèque** | http://localhost:8000/fr/user/library/ |
| **⭐ Favoris** | http://localhost:8000/fr/user/favorites/ |
| **💡 Recommandations** | http://localhost:8000/fr/books/recommendations/ |
| **🎪 Événements** | http://localhost:8000/fr/books/events/ |
| **📊 Statistiques** | http://localhost:8000/fr/user/analytics/ |
| **💳 Panier** | http://localhost:8000/fr/cart/ |
| **⚙️ Admin** | http://localhost:8000/admin/ |
| **🔌 API** | http://localhost:8000/api/ |

---

## 🎬 MÉDIAS - Détails

### Audiobooks
```
http://localhost:8000/fr/audiobooks/
```
✅ Lecteur audio intégré  
✅ Suivi de progression  
✅ Synchronisation  

### Vidéos
```
http://localhost:8000/fr/videos/
```
✅ Lecteur vidéo  
✅ Support YouTube/Vimeo  

### Podcasts
```
http://localhost:8000/fr/podcasts/
```
✅ Lecteur podcast  
✅ Sync Spotify/Apple  

---

## 💬 FORUMS - Détails

### Consulter Forums
```
http://localhost:8000/fr/forum/
```

### Catégories
```
http://localhost:8000/fr/forum/categories/
```

### Créer Discussion
```
http://localhost:8000/fr/forum/create/
```

✅ Discussions par catégorie  
✅ Votes (upvote/downvote)  
✅ Réponses imbriquées  
✅ Modération  

---

## 👥 COMMUNAUTÉ - Détails

### Mon Profil
```
http://localhost:8000/fr/user/profile/
```

### Répertoire Utilisateurs
```
http://localhost:8000/fr/community/users/
```

### Mes Suivis
```
http://localhost:8000/fr/user/following/
```

### Mes Followers
```
http://localhost:8000/fr/user/followers/
```

✅ Profils publics  
✅ Suivre utilisateurs  
✅ Partager livres  
✅ Découvrir lecteurs  

---

## 📖 LIRE UN LIVRE

1. Aller aux livres: http://localhost:8000/fr/books/
2. Chercher un livre
3. Cliquer dessus
4. Cliquer "Lire"
5. Utiliser le lecteur:
   - Scroll continu
   - Zoom +/-
   - Auto-sauvegarde
   - Surligner texte

---

## ⚠️ NOTES

- **Authentification requise** pour: Profil, Bibliothèque, Forums (création), Recommandations
- **Accès public** pour: Livres, Forums (lecture), Événements, Accueil
- **Erreur 404?** Vérifiez que le serveur fonctionne: `python manage.py runserver`

---

**Consulter:** [GUIDE_ACCES_PAGES.md](GUIDE_ACCES_PAGES.md) pour le guide complet avec tous les détails!

