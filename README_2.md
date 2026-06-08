# Progression du jour (suivi)

Date: 2026-06-08

## 1) Correctifs production appliques

- Fix du bug prix (`Decimal` x `float`) dans `Book.get_final_price()`.
- Correctifs PWA:
  - enregistrement service worker unifie,
  - manifest aligne sur routes FR,
  - fallback d'installation guide (iOS/Android/Windows),
  - fiabilisation du cache offline (routes FR + assets CDN).
- Correctif offline-reader pour rester accessible meme en cas de panne DB.
- Normalisation des liens sociaux/email (`mailto:`, URL valides).

## 2) Base de donnees / Render

- `DATABASE_URL` corrige (incident DNS resolu).
- Verification endpoints critiques: home, detail livre, logout, offline-reader.
- Rappel exploitation: en cas de 502/Bad Gateway, verifier logs runtime + rollback deploy si necessaire.

## 3) Auteurs et experience contenu

- Ajout nationalite `RDC` dans les choix auteurs.
- Ajout champs sociaux auteur:
  - `facebook_url`, `instagram_url`, `x_url`, `linkedin_url`, `youtube_url`, `tiktok_url`.
- Admin auteur ameliore (photo + liens sociaux visibles/modifiables).
- Page auteur detaillee redesign (UI premium).
- Nom auteur rendu cliquable vers page auteur quand une relation auteur existe.
- Miniature photo auteur affichee dans la section auteur du detail livre.

## 4) Securite et authentification

- Durcissement login OTP telephone:
  - OTP desactive pour comptes sensibles (staff/superuser/admin roles),
  - plus d'auto-creation de compte via OTP,
  - expiration OTP + limite tentatives,
  - nettoyage OTP apres succes,
  - suppression de l'affichage du code OTP dans les messages.
- Renforcement session cookies:
  - `SESSION_COOKIE_SAMESITE = "Lax"`
  - `SESSION_COOKIE_AGE = 7 jours`
  - `SESSION_SAVE_EVERY_REQUEST = True`
- OAuth Google:
  - ajout d'un adapter social (`users/social_adapter.py`) qui relie automatiquement un login Google au compte existant (meme email),
  - evite le faux flux "nouveau compte / finaliser inscription" pour un utilisateur deja inscrit.

## 5) Service Worker / lecture non connecte

- Ajustement fallback reader:
  - suppression du fallback force vers `/offline-reader/<id>/` sur route lecture,
  - conservation du flux d'authentification (redirection login).
- Ameliorations offline:
  - prise en charge des reponses `opaque` (assets CDN),
  - fallback HTML vers `/fr/` puis `/offline/`,
  - versionnement cache PWA mis a jour.

## 6) Outils admin et exploitation

- Guide admin professionnel avec modal "Accepter / Decliner" fiabilise (persistant + feedback visuel).
- Ajout d'un panneau "Diagnostic PWA" dans l'admin:
  - etat HTTPS, SW, manifest, caches, prompt install.
- Nouvelle commande Django pour lier des auteurs en masse:
  - fichier: `catalogue/management/commands/link_books_to_authors.py`
  - exemples:
    - `python manage.py link_books_to_authors --default-author "Calures Editions" --dry-run`
    - `python manage.py link_books_to_authors --default-author "Calures Editions"`
    - `python manage.py link_books_to_authors --csv mapping.csv`

## 7) Branding / UI

- Genre des livres passe en vert sur les pages visibles (catalogue, detail, recommandations).
- Ajout d'un champ admin `pwa_logo` dans `SiteConfiguration`:
  - le logo PWA devient modifiable depuis l'admin.
- Fallback branding PWA:
  - nouveau logo PWA par defaut mauve (`static/images/pwa-default-logo.svg`),
  - `theme_color` PWA passe en mauve (`#8b5cf6`) quand aucun logo admin n'est defini.

## 8) Commits pousses aujourd'hui

- `78fef8d` Fix production PWA reliability and pricing type errors
- `ba04a3c` Harden author experience and login security flows
- `606b9e4` Add admin onboarding guide and author linking tooling
- `8d7f40e` Improve PWA install fallback and admin guide acceptance UX
- `226baad` Improve Windows/desktop PWA install guidance and button behavior
- `24f2254` Harden iOS/Android PWA installability and offline reliability
- `db1b760` Add admin PWA diagnostics panel for install/offline checks
- `7cecbb6` Add admin-configurable PWA logo and enforce green genre labels
- `8826782` Fix Google OAuth to auto-link existing user accounts
- `f45b008` Set default PWA logo and theme color to mauve

## 9) Prochaine reprise

- Verifier deploiement Render du dernier commit.
- Lancer `python manage.py migrate` en production si pas encore fait (champ `pwa_logo`).
- Tester le flux Google OAuth avec compte existant (meme email) sur mobile et desktop.
- Valider l'installation PWA sur iOS/Android apres vidage cache navigateur si besoin.
