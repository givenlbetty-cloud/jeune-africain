# 🚀 QUICK START - Redémarrage du Serveur

## ⚡ COMMANDE UNIQUE (Copier-Coller)

```bash
cd /workspaces/bnc && source venv/bin/activate && python manage.py check && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000
```

---

## 📍 ACCÈS À L'ADMIN

- **URL**: http://localhost:8000/admin/
- **Email**: admin@bnc.local
- **Password**: admin123

---

## ✅ VÉRIFICATIONS EFFECTUÉES

✅ django.contrib.admin présent dans INSTALLED_APPS  
✅ jazzmin EN PREMIER dans INSTALLED_APPS  
✅ AUTH_USER_MODEL = "users.CustomUser"  
✅ URLs admin correctement routées  
✅ JAZZMIN_SETTINGS configurés  
✅ Migrations appliquées  
✅ Fichiers statiques Jazzmin: 13 fichiers  
✅ Superuser admin@bnc.local créé  

---

## 🎯 RÉSULTAT

✨ **Jazzmin s'affichera avec l'interface moderne!**

