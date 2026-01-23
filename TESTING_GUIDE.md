# 🧪 Guide de test - UI/UX Redesign

## 🏠 Accueil (/)

### ✅ À tester:
1. **Navbar**
   - [ ] Logo cliquable ramène à l'accueil
   - [ ] Liens de navigation visibles et cliquables
   - [ ] Dropdown utilisateur fonctionne
   - [ ] Toggle mode sombre/clair (bouton lune/soleil)
   - [ ] Responsive: hamburger menu sur mobile

2. **Hero Section**
   - [ ] Gradient visible
   - [ ] Texte centré
   - [ ] Boutons CTA visibles et cliquables

3. **Statistiques**
   - [ ] 4 cartes affichées (Livres, Auteurs, Partenaires, Lecteurs)
   - [ ] Hover effect sur cartes
   - [ ] Animation d'apparition

4. **Livres à la une**
   - [ ] Grille responsive affichée
   - [ ] Couvertures de livres chargées
   - [ ] Bouton "Découvrir" fonctionnel

5. **Footer**
   - [ ] 4 colonnes avec liens
   - [ ] Réseaux sociaux affichés
   - [ ] Copyright visible

### 🌓 Mode sombre:
- [ ] Cliquer lune → fond sombre, texte clair
- [ ] Cliquer soleil → fond clair, texte foncé
- [ ] Rafraîchir la page → thème persisté

---

## 📚 Catalogue (/books/)

### ✅ À tester:
1. **Hero section de recherche**
   - [ ] Barre de recherche visible
   - [ ] Bouton rechercher fonctionnel

2. **Filtres (Sidebar)**
   - [ ] Tri: Par défaut, Titre A-Z, Récents, Prix, Mieux notés
   - [ ] Genre: Checkboxes fonctionnelles
   - [ ] Type: Gratuit / Payant
   - [ ] Langue: Checkboxes fonctionnelles
   - [ ] Sticky position sur desktop

3. **Grille de livres**
   - [ ] Grille responsive:
     - [ ] 4 colonnes sur desktop (>1200px)
     - [ ] 3 colonnes sur tablet (768-1200px)
     - [ ] 2 colonnes sur mobile (576-768px)
   - [ ] Cartes avec couverture
   - [ ] Badge "Gratuit"/"Payant"
   - [ ] Hover effect: élévation + zoom image
   - [ ] Boutons "Voir" et "♥" 

4. **Pagination**
   - [ ] Numéros de page visibles
   - [ ] Boutons Précédent/Suivant/Premier/Dernier
   - [ ] Navigation fonctionnelle

---

## 📖 Lecteur de livre (/book/{id}/read/)

### ✅ À tester:
1. **Header du lecteur**
   - [ ] Titre du livre visible
   - [ ] Auteur visible
   - [ ] Temps de lecture compte
   - [ ] Bouton Fermer retourne à la fiche

2. **Toolbar**
   - [ ] Boutons Zoom - / + fonctionnels
   - [ ] Bouton Marque-pages ouvre sidebar
   - [ ] Boutons Précédent/Suivant pour pages
   - [ ] Input numéro page changeable
   - [ ] Pourcentage mis à jour

3. **Lecteur**
   - [ ] PDF affiché correctement (si fichier)
   - [ ] Ou texte formaté (si texte)
   - [ ] Scrolling fluide
   - [ ] Page change au clic Suivant

4. **Barre de progression**
   - [ ] Remplie proportionnellement aux pages
   - [ ] Couleur dégradée

5. **Sidebar marque-pages**
   - [ ] Glisse depuis la droite en douceur
   - [ ] Affiche statistiques:
     - [ ] Pages lues: nombre correct
     - [ ] Progression: en pourcentage
     - [ ] Temps écoulé: compté correctement
   - [ ] Section ajouter note avec textarea
   - [ ] Bouton ajouter note

---

## 👥 Authentification

### ✅ Connexion:
1. [ ] Page login accessible
2. [ ] Formulaire accepte identifiants
3. [ ] Erreur sur mauvaise connexion
4. [ ] Redirection vers page de destination

### ✅ Inscription:
1. [ ] Page signup visible
2. [ ] Formulaire complet
3. [ ] Validation des champs
4. [ ] Création compte fonctionne

### ✅ Profil:
1. [ ] Avatar affiché dans navbar
2. [ ] Dropdown menu utilisateur accessible
3. [ ] Lien vers profil fonctionne
4. [ ] Déconnexion fonctionne

---

## 🎨 Design et UX

### Palettes de couleurs:
- [ ] Mode clair: Vert foncé primaire, doré accent
- [ ] Mode sombre: Texte clair sur fond foncé
- [ ] Contraste suffisant pour lisibilité
- [ ] Cohérence couleurs entre pages

### Animations:
- [ ] Cartes: Hover avec translateY(-8px)
- [ ] Sidebar: Glisse depuis droite
- [ ] Progression: Barre remplit doucement
- [ ] Pas d'animations saccadées

### Responsive:
- [ ] **Mobile (< 576px)**
  - [ ] Menu hamburger
  - [ ] Navigation empilée
  - [ ] Grille 1-2 colonnes

- [ ] **Tablet (576-768px)**
  - [ ] 2 colonnes grille
  - [ ] Sidebar filtres visible
  - [ ] Navigation lisible

- [ ] **Desktop (> 768px)**
  - [ ] Full layout optimal
  - [ ] Sidebar fixe
  - [ ] 3-4 colonnes grille

---

## ⚡ Performance

### ✅ À vérifier:
1. [ ] Temps de chargement < 3s
2. [ ] Images optimisées
3. [ ] CSS non-bloquant
4. [ ] Pas de CLS (Cumulative Layout Shift)
5. [ ] Animations fluides 60fps

### Devtools:
```bash
# Performance
- Lighthouse > 80
- FCP < 1.5s
- LCP < 2.5s
```

---

## 🔒 Sécurité

### ✅ À vérifier:
1. [ ] CSRF token sur formulaires
2. [ ] Connexion sécurisée (HTTPS ready)
3. [ ] Pas de données sensibles en clair
4. [ ] Validation côté serveur

---

## ♿ Accessibilité

### ✅ À tester:
1. [ ] Tous les liens avec texte clair
2. [ ] Boutons avec aria-label
3. [ ] Contraste couleur > 4.5:1 pour texte
4. [ ] Navigation au clavier (Tab, Enter)
5. [ ] Focus visible sur tous les éléments
6. [ ] Support lecteur d'écran

---

## 🌐 Navigateurs

### ✅ Tester sur:
- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari
- [ ] Edge

### ✅ Appareils:
- [ ] iPhone (small)
- [ ] iPad (medium)
- [ ] Desktop 1920x1080 (large)
- [ ] Ultra-wide 3440x1440

---

## 📋 Checklist finale

### Frontend:
- [ ] Accueil responsive et beau
- [ ] Catalogue avec filtres
- [ ] Lecteur fonctionnel
- [ ] Mode sombre persistant
- [ ] Animations fluides
- [ ] Pas d'erreurs console

### Backend:
- [ ] Migrations appliquées
- [ ] Pas d'erreurs 500
- [ ] API répondante
- [ ] Base de données synchrone

### Déploiement:
- [ ] Code versionné (git)
- [ ] README à jour
- [ ] Documentation complète
- [ ] Prêt production

---

## 🐛 Bugs connus & fixes

| Bug | Statut | Fix |
|-----|--------|-----|
| Bloc extra_css dupliqué | ✅ FIXÉ | Supprimé second bloc |
| Template base_new.html | ✅ FIXÉ | Renommé en base.html |
| URLs templates | ✅ FIXÉ | Mises à jour |

---

## 📞 Support

Pour signaler un problème:
1. Ouvrir issue sur GitHub
2. Décrire le problème
3. Fournir capture d'écran
4. Indiquer navigateur/appareil

---

**Testez et amusez-vous! 🎉**

Date: 18 Décembre 2025
