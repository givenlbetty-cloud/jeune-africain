# 📖 BNC Modern eBook Reader - Guide d'Utilisation

## ✨ Améliorations Implémentées

### 1. **Barre de Progression Sensuelle**
- Barre de progression fluide avec animation `cubic-bezier(0.34, 1.56, 0.64, 1)`
- Curseur interactif qui apparaît au survol
- Affichage dynamique du pourcentage avec animation de nombre
- Feedback haptique lors des changements de page (10-15ms)
- Suivi continu du scroll en temps réel

### 2. **Interface Moderne et Fluide**
- Design minimaliste avec gradients doux
- Transitions ultra-fluides sur tous les éléments
- Animations d'entrée/sortie élégantes
- Support complet du mode sombre
- Responsive design pour tous les appareils

### 3. **Surlignage Amélioré**
Trois façons de surligner :

#### Option 1: Sélection de Texte
1. Sélectionnez le texte que vous voulez surligner
2. Un menu contextuel apparaît avec 2 boutons:
   - **✨ Surligner**: Marque le texte en jaune/orange
   - **📝 Note**: Ajoute une note à ce passage

#### Option 2: Raccourci Clavier
- `Ctrl+H` (ou `Cmd+H` sur Mac): Activer/désactiver le mode surlignage
- Le texte surligné brille avec une animation pulsante

#### Option 3: Menu Contextuel
- Clic droit → Marquer → Surligner

### 4. **Système de Notes Intégré**
- Cliquez sur `Ctrl+N` pour ajouter une note rapide
- Ou utilisez le menu contextuel après sélection de texte
- Les notes sont liées au passage surligné
- Sauvegarde automatique en base de données

### 5. **Navigation Intuitive**

#### Clavier
- `→` ou `Espace`: Page suivante
- `←`: Page précédente
- `Ctrl+B`: Afficher/masquer les marque-pages
- `Ctrl+H`: Mode surlignage
- `Ctrl+N`: Ajouter une note

#### Souris
- Cliquez sur les boutons Précédent/Suivant
- Saisissez un numéro de page et appuyez sur Entrée
- Utilisez le zoom (+/-)

### 6. **Suivi de la Progression**
- Barre de progression horizontale en haut
- Statistiques en temps réel:
  - Pages lues
  - Pourcentage complété
  - Temps de lecture écoulé
- Sauvegarde automatique chaque 1.5s
- Reprise depuis la dernière page lue au lancement

### 7. **Marque-pages Intelligents**
- Cliquez sur 📌 Marque-pages pour ouvrir le panneau
- Voir toutes vos annotations
- Accès rapide aux notes
- Surlignages avec prévisualisation

## 🎨 Expérience Sensuelle

### Feedback Tactile
- Vibrations légères lors de:
  - Changement de page (15ms)
  - Actions importantes (10-5-10ms)
  - Jalons de progression (5ms tous les 10%)

### Animations Fluides
- Easing personnalisé: `cubic-bezier(0.34, 1.56, 0.64, 1)`
- Transitions de 300-600ms selon l'action
- Animations de pulse pour les surlignages
- Fondu doux pour les toasts

### Couleurs et Gradients
- Primaire: #1a4d3e → #2d7a5f
- Secondaire: #c9534f
- Surlignage: Jaune/Orange avec transparence
- Mode sombre supporté

## 📊 Performance

- **Scroll optimisé**: `passive: true` listeners
- **Animations GPU**: `will-change`, `transform`
- **Debounce de sauvegarde**: Toutes les 1.5s max
- **Chargement lazy**: Ressources externes chargées au besoin
- **Optimisation mémoire**: Cleanup des anciens événements

## 🔧 Configuration

### Initialisation Manuelle
```javascript
const reader = new EBookReader({
    bookId: 123,
    totalPages: 250,
    lastPage: 45,
    isPdf: false
});
```

### Options
- `bookId`: ID du livre (requis pour sauvegarde)
- `totalPages`: Nombre total de pages
- `lastPage`: Dernière page lue
- `isPdf`: Format PDF ou texte

## 📝 API Backend Requise

Pour la sauvegarde complète, vous devez avoir ces endpoints:

### 1. Mise à jour de la progression
```
POST /catalogue/{bookId}/update-progress/
Body: {
    current_page: number,
    progress_percent: number,
    is_completed: boolean
}
```

### 2. Sauvegarde des surlignages
```
POST /catalogue/{bookId}/highlight/
Body: {
    highlight_id: string,
    text: string,
    page: number
}
```

### 3. Sauvegarde des notes
```
POST /catalogue/{bookId}/note/
Body: {
    selected_text: string,
    note_text: string,
    page: number
}
```

### 4. Chargement des annotations
```
GET /catalogue/{bookId}/annotations/
Response: {
    highlights: [],
    notes: []
}
```

## 🌙 Mode Sombre

- Styles automatiquement appliqués avec `[data-bs-theme="dark"]`
- Texte blanc sur fond foncé
- Surlignages conservent leur couleur dorée
- Gradients adaptés pour la lisibilité

## ♿ Accessibilité

- Support des lecteurs d'écran
- Navigation au clavier complète
- Contraste WCAG AA sur tout le site
- Respect des `prefers-reduced-motion`

## 🚀 Fonctionnalités Futures

- [ ] Marque-pages avec synchronisation cloud
- [ ] Dictionnaire intégré (clic pour définition)
- [ ] Traduction en ligne (multi-langue)
- [ ] Export de notes (PDF, Markdown)
- [ ] Partage de passages surlignés
- [ ] Synchronisation entre appareils
- [ ] Format Epub avancé (multi-colonnes)

## 🐛 Dépannage

### Les surlignages ne s'affichent pas
- Vérifier que le CSRF token est présent
- Vérifier les logs du navigateur (F12)
- Vérifier les endpoints backend

### Les animations sont saccadées
- Activer GPU acceleration dans le navigateur
- Réduire les effets visuels pour les appareils lents
- Les animations se désactivent si `prefers-reduced-motion` est activé

### Le scroll n'est pas fluide
- Vérifier que `scroll-behavior: smooth` est supporté
- Utiliser Firefox/Chrome pour une meilleure expérience

## 📞 Support

Pour toute question ou suggestion:
1. Vérifiez les erreurs dans la console (F12)
2. Testez dans un navigateur moderne (Chrome/Firefox/Safari)
3. Contactez le support de BNC
