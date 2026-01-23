# Réorganisation de l'Administration Django

## Objectif
Ce document explique la restructuration du panneau d'administration pour séparer les fonctionnalités en sections logiques distinctes (Catalogue, Média, Finance, Événements) sans modifier la base de données.

## Architecture "Virtual Apps"

Nous avons utilisé le pattern **Proxy Models** couplé à des **Custom AppConfigs** pour créer des sections virtuelles.

### 1. Structure des "Apps"
Des modules virtuels ont été créés pour permettre à Django de séparer les modèles dans le menu :
- `catalogue.media_app` → Label: `media_management` ("Gestion Média")
- `catalogue.finance_app` → Label: `finance_management` ("Finance & Paiement")
- `catalogue.events_app` → Label: `event_management` ("Événements")

Ces modules sont définis dans `catalogue/apps.py` et enregistrés dans `settings.INSTALLED_APPS`.

### 2. Modèles Proxy (`catalogue/proxy_models.py`)
Au lieu de modifier les modèles existants (ce qui briserait les relations en base de données), nous avons créé des "Proxies".
Un Proxy pointe vers la même table SQL mais peut avoir une configuration Python différente (notamment `app_label`).

Exemple :
```python
class AudiobookProxy(AudiobookMetadata):
    class Meta:
        proxy = True
        app_label = 'media_management'  # C'est ici que la magie opère !
```

### 3. Configuration Admin (`catalogue/admin.py`)
1. **Désactivation** des modèles originaux (pour éviter les doublons).
2. **Enregistrement** des modèles Proxy.
3. **Optimisation** des interfaces (colonnes, filtres, inlines).

## Résultat dans l'Interface

| Section | Contenu |
|---------|---------|
| **📖 Catalogue** | Livres, Auteurs, Catégories |
| **📺 Gestion Média** | Audiobooks, Vidéos, Podcasts |
| **💳 Finance & Paiement** | Transactions, Comptes Marchands |
| **📅 Événements** | Agenda Événements |

## Maintenance

Pour ajouter un nouveau modèle dans une section :
1. Définir le modèle normalement dans `models.py`.
2. Créer un Proxy dans `proxy_models.py` avec le bon `app_label`.
3. Enregistrer ce Proxy dans `admin.py` au lieu du modèle original.
