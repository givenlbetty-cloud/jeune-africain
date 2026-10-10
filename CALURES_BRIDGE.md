# Relier BNC à CALURES

Le menu **Articles** de l'administration BNC propose l'action **Envoyer sur CALURES comme brouillon**. Les articles reçus doivent être relus puis publiés dans https://calures-editions.vercel.app/admin/.

## Activation sur Render

Dans le service `bnc-web`, rubrique **Environment**, renseigner :

```dotenv
CALURES_BRIDGE_URL=https://calures-editions.vercel.app/integrations/bnc/articles/
CALURES_BRIDGE_TOKEN=<valeur de CALURES_BNC_SYNC_TOKEN sur Vercel>
```

Le jeton doit être identique des deux côtés. Ne jamais le placer dans Git, un ticket ou une capture publique. L'adresse est également définie par défaut dans Django et dans `render.yaml`. `sync: false` déclare le secret sans sa valeur ; un service Render déjà existant nécessite de renseigner ce secret dans son tableau de bord.

Déployer le commit contenant le pont et enregistrer les variables, puis vérifier depuis le Shell Render :

```sh
python manage.py check_calures_bridge
```

Cette commande contrôle le jeton sans créer d'article ni publier de contenu.

## Utilisation

1. Dans BNC, ouvrir **Articles** et sélectionner un article.
2. Choisir **Envoyer sur CALURES comme brouillon**, puis exécuter l'action.
3. Dans CALURES, ouvrir **Articles**, relire le brouillon puis publier.

Le nouvel envoi d'un même article met à jour son brouillon sans doublon. Une version déjà publiée sur CALURES reste visible jusqu'à validation de la nouvelle révision. L'image doit faire au maximum 4 Mo et l'ensemble de la requête rester sous la limite Vercel ; compresser l'image si nécessaire.

Cette liaison concerne les articles. La sélection des livres reste gérée dans **CALURES → Fragments → Livres mis en avant**, avec un lien vers la fiche BNC. Elle n'est pas synchronisée automatiquement.

Après la bascule du domaine, modifier `CALURES_BRIDGE_URL` vers `https://calures.org/integrations/bnc/articles/` et relancer la vérification.
