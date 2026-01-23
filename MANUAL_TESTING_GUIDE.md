# 🧪 GUIDE DE TEST MANUEL - Étape 1 (23 Décembre 2025)

## 📋 Informations de Connexion

```
Email:    test@example.com
Password: test123456
```

---

## 🎯 TEST 1: Free Preview (30 min)

### Étapes:

1. **Aller à la page de connexion**
   - URL: http://localhost:8000/auth/login/
   - Cliquez sur "Se connecter"

2. **Entrer les identifiants**
   - Email: `test@example.com`
   - Mot de passe: `test123456`
   - Cliquez "Login"

3. **Accéder au livre de test**
   - Après connexion, allez à:
   - http://localhost:8000/catalogue/book/39eaa1e8-949a-40d9-88f1-fffc390e5a52/
   - Ou cherchez "la discipline" dans le catalogue

4. **Ouvrir le lecteur**
   - Cliquez sur "Lire" ou le bouton d'accès lecture
   - URL directe: http://localhost:8000/catalogue/book/39eaa1e8-949a-40d9-88f1-fffc390e5a52/read/

### À Vérifier:

- [ ] **Pages affichées:** Devrait voir seulement pages 1-5
  - Indicateur en bas: "Page 1 of 5" (free pages) vs "Page 1 of 103" (total)
  - Impossible de scroller au-delà de page 5

- [ ] **Banner "Acheter":** Après page 5
  - Message: "Fin de l'aperçu gratuit"
  - Bouton: "Acheter ce livre" ou "Débloquer accès complet"
  - Couleur: Rouge/Orange pour attirer attention

- [ ] **Zoom +/-:** Boutons en haut du lecteur
  - Cliquez + : Texte agrandit
  - Cliquez - : Texte réduit
  - Affichage: "Zoom: 100%" → "150%" → "80%"
  - Limite: 50% - 250%

- [ ] **Navigation par page:**
  - Scroll vertical: Fonctionne (pages empilées)
  - Input page: Entrez numéro, va à la page
  - Flèches: Haut/Bas pour page précédente/suivante

- [ ] **Barre progression:**
  - Visible en bas de l'écran
  - Pourcentage en temps réel
  - Avance avec scroll

- [ ] **Toast notifications:**
  - Message "Progression sauvegardée" après scroll
  - Message zoom "Zoom: X%"

---

## 🎯 TEST 2: Sauvegarde Progression (20 min)

### Étapes:

1. **Ouvrir le lecteur** (du test 1)
   - http://localhost:8000/catalogue/book/39eaa1e8-949a-40d9-88f1-fffc390e5a52/read/

2. **Lire quelques pages**
   - Scroll jusqu'à page 3-4
   - Attendez 6 secondes (sauvegarde auto)
   - Observez toast "Progression sauvegardée"

3. **Fermer le navigateur**
   - Fermez la page ou la fenêtre
   - Attendez 2-3 secondes

4. **Rouvrir et vérifier**
   - Reconnecter si nécessaire
   - Retourner au même livre
   - **VÉRIFICATION:** 
     - [ ] Page restituée à celle lue (ex: page 4)
     - [ ] Toast: "📖 Reprise page 4/5"
     - [ ] Scroll automatique vers la page lue
     - [ ] Pas besoin de relire depuis page 1

---

## 🎯 TEST 3: Événements (20 min)

### Étapes:

1. **Aller à la page des événements**
   - URL: http://localhost:8000/catalogue/events/

2. **Vérifier affichage grille**
   - [ ] 5 événements créés visibles
   - [ ] Grille responsive (3 colonnes desktop, 1 mobile)
   - [ ] Images placeholders si images manquantes
   - [ ] Titre, description, date visible

3. **Vérifier badges statut**
   - [ ] Événements "EN COURS" → Badge rouge 🔴
   - [ ] Événements "À VENIR" → Badge bleu ✅
   - [ ] Événements "PASSÉS" → Badge gris ⏱️

4. **Cliquer sur un événement**
   - Cliquez sur "Atelier: Écriture Créative"
   - Vérifier page détails:
     - [ ] Titre complet
     - [ ] Description longue
     - [ ] Date/Heure
     - [ ] Lieu
     - [ ] Lien externe (si présent)

5. **Vérifier filtres**
   - Cherchez filters/select en haut
   - [ ] Filtre par type (Annonces, Ateliers, Conférences, etc.)
   - [ ] Recherche par titre
   - [ ] Pagination si > 12 événements

6. **Test responsive**
   - Ouvrez DevTools (F12)
   - Redimensionnez à mobile (375px)
   - [ ] Grille passe à 1 colonne
   - [ ] Texte reste lisible
   - [ ] Boutons cliquables

---

## ✅ Checklist Finale

### Free Preview
- [ ] 5 pages affichées correctement
- [ ] Banner "Acheter" visible après page 5
- [ ] Zoom +/- fonctionne
- [ ] Navigation par page OK
- [ ] Barre progression visible

### Sauvegarde Progression
- [ ] Toast "Progression sauvegardée" après scroll
- [ ] Auto-retour à la dernière page après refresh
- [ ] Toast "Reprise page X/Y" au retour

### Événements
- [ ] 5 événements visibles
- [ ] Badges statut corrects
- [ ] Page détails fonctionnelle
- [ ] Filtres présents (si implémentés)
- [ ] Responsive OK

---

## 📊 Résultats Attendus

### Succès Complet: 
**Tous les checkboxes cochés ✅**
→ Système 100% fonctionnel
→ Prêt pour OAuth + Deploy

### Avec Problèmes Minor:
**1-2 checkboxes non cochés**
→ Demander aide pour corriger
→ Impact faible sur deployment

### Problème Major:
**Free Preview ne fonctionne pas**
→ Arrêter, debug code
→ Vérifier ReadingSession logic

---

## 🔍 Debug Tips

### Si Free Preview n'affiche pas le bon nombre de pages:
```bash
# Vérifier la configuration
python manage.py shell
>>> from catalogue.models import Book
>>> book = Book.objects.get(id='39eaa1e8-949a-40d9-88f1-fffc390e5a52')
>>> print(f"Pages libres: {book.free_pages_count}")
>>> print(f"Pages totales: {book.pages_count}")
```

### Si progression ne se sauvegarde pas:
- Ouvrir DevTools (F12) → Network
- Scroller et observer requêtes
- Chercher `PUT /api/reading-session/` ou similar
- Vérifier status 200/201

### Si événements ne s'affichent pas:
- Ouvrir http://localhost:8000/api/events/
- Vérifier JSON retourné
- Chercher `is_published: true` dans la réponse

---

## 💡 Notes

- Le serveur continue de tourner en arrière-plan
- Tests peuvent prendre 30-45 min total
- À faire dans l'ordre (Free Preview → Progression → Événements)
- Reporter tout problème avec détails + screenshot

