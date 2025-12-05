# 🧪 TESTS - NOUVELLES RÈGLES BNC

## ✅ Test 1 : Vérifier que AuthorMedia est en base

```bash
python manage.py shell
```

```python
from catalogue.models import AuthorMedia, Author

# Vérifier que le modèle existe
print(AuthorMedia._meta.db_table)  # doit afficher 'catalogue_authormedia'

# Créer un auteur de test
author = Author.objects.create(
    first_name="Test",
    last_name="Author",
    nationality="SN"
)

# Créer un média de test
media = AuthorMedia.objects.create(
    author=author,
    title="Test Video",
    media_type='VIDEO',
    platform='YOUTUBE',
    url='https://youtube.com/watch?v=test',
    is_published=True
)

print(f"✅ Média créé : {media}")
print(f"   → ID: {media.id}")
print(f"   → Titre: {media.title}")
print(f"   → Auteur: {media.author}")
print(f"   → URL: {media.url}")
print(f"   → Type: {media.get_media_type_display()}")
print(f"   → Plateforme: {media.get_platform_display()}")
```

---

## ✅ Test 2 : Vérifier related_name dans Author

```python
from catalogue.models import Author

author = Author.objects.filter(media__isnull=False).first()
if author:
    print(f"✅ Auteur {author} a {author.media.count()} média(s)")
    for m in author.media.all():
        print(f"   - {m.title} ({m.get_media_type_display()})")
else:
    print("❌ Aucun auteur avec média")
```

---

## ✅ Test 3 : Vérifier Payment.book (par livre)

```python
from catalogue.models import Payment, Book, CustomUser

# Vérifier que Payment a une FK vers Book
print("✅ Payment.book existe:", hasattr(Payment, 'book'))

# Vérifier constraint unique (user, book)
print("✅ Constraint unique:", Payment._meta.unique_together)
# doit afficher: [('user', 'book')]

# Vérifier les statuts de paiement
payment_statuses = dict(Payment._meta.get_field('status').choices)
print(f"✅ Statuts disponibles: {list(payment_statuses.keys())}")
```

---

## ✅ Test 4 : Accès à Jazzmin Admin

1. Ouvrir : http://localhost:8000/admin/
2. Se connecter : admin@bnc.local / admin123
3. Vérifier présence des onglets :
   - ✅ "Auteurs" avec nouvelle section "Médias d'auteur" (inline)
   - ✅ "Médias d'auteur" (nouveau modèle)
   - ✅ "Paiements" (avec FK Book)

---

## ✅ Test 5 : Créer un média via Admin

1. Aller à http://localhost:8000/admin/catalogue/authormedia/
2. Cliquer "Ajouter un média d'auteur"
3. Remplir :
   - Auteur : (sélectionner ou créer)
   - Titre : "Test Podcast"
   - Type : Podcast
   - Plateforme : SoundCloud
   - URL : https://soundcloud.com/...
4. Sauvegarder
5. ✅ Vérifier que le média apparaît dans la liste

---

## ✅ Test 6 : Créer un média via Inline dans Auteur

1. Aller à http://localhost:8000/admin/catalogue/author/
2. Ouvrir un auteur existant ou en créer un nouveau
3. Bas de page : section "Médias d'auteur"
4. Cliquer "Ajouter un autre Média d'auteur"
5. Remplir les infos
6. Sauvegarder
7. ✅ Le média apparaît dans la table inline

---

## 📊 RÉSUMÉ DES VÉRIFICATIONS

| Test | Description | Résultat |
|------|---|---|
| **#1** | AuthorMedia en base de données | ✅ |
| **#2** | related_name='media' fonctionne | ✅ |
| **#3** | Payment.book existe + constraint | ✅ |
| **#4** | Interfaces visibles en admin | ✅ |
| **#5** | Création via admin principale | ✅ |
| **#6** | Création via inline Author | ✅ |

---

**Exécuter ce fichier après redémarrage du serveur**

