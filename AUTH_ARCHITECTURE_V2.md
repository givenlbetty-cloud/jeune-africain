# Architecture d'Authentification Hybride (Google + WhatsApp)

## 🎯 Objectif
Système d'authentification robuste, simple et adapté au marché RDC, éliminant les mots de passe traditionnels au profit d'une approche "Passwordless" via WhatsApp et Google.

---

## 1. Flux Utilisateur (User Flow)

### A. Connexion/Inscription via Google (Flux Principal)
1.  **Action** : L'utilisateur clique sur "Continuer avec Google".
2.  **Processus** : OAuth 2.0 standard.
3.  **Résultat** :
    -   *Si Nouveau Compte* : Compte créé avec Email + Nom + Avatar.
        -   **ÉTAPE CRITIQUE** : Redirection immédiate vers une page "Vérification WhatsApp". L'utilisateur **ne peut pas** accéder au site sans valider son numéro.
    -   *Si Compte Existant* :
        -   Vérification si `phone_verified == True`.
        -   Si Oui 👉 Dashboard.
        -   Si Non 👉 Redirection page "Vérification WhatsApp".

### B. Connexion/Inscription via WhatsApp (Flux Alternatif)
1.  **Action** : L'utilisateur clique sur "Se connecter avec WhatsApp".
2.  **Saisie** : Formulaire simple demandant uniquement le numéro de téléphone (préfixe +243 par défaut).
3.  **Validation** : Le système vérifie le format et l'existence du numéro.
4.  **Envoi OTP** : Un code à 6 chiffres est envoyé via l'API WhatsApp Business.
5.  **Vérification OTP** :
    -   *Si Nouveau Compte* : Création du compte (Phone = ID, Email = généré/placeholder ou demandé optionnellement). Demande Nom/Prénom. 👉 Dashboard.
    -   *Si Compte Existant* : Login immédiat. 👉 Dashboard.

---

## 2. Structure de Données (Modifications DB)

Le modèle `CustomUser` doit évoluer pour supporter cette logique.

```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Champs existants...
    email = models.EmailField(unique=True, null=True, blank=True) # Devient nullable pour les users 100% WhatsApp
    
    # Nouveaux Champs / Modifications
    phone = models.CharField(
        unique=True, # CRITIQUE : Le numéro devient un identifiant unique
        max_length=20,
        validators=[phone_regex]
    )
    is_phone_verified = models.BooleanField(default=False)
    
    # Sécurité OTP
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.IntegerField(default=0)
    
    # Username est souvent requis par Django, on peut utiliser le phone comme username par défaut
    username = models.CharField(max_length=150, unique=True)
```

## 3. Logique Technique & API

### A. Backend Authentication
Nous devons créer un `Backend` d'authentification personnalisé pour Django qui accepte (Phone + OTP) au lieu de (Email + Password).

### B. API WhatsApp (Intégration)
Pour la RDC, l'utilisation de **Meta Cloud API (WhatsApp Business API)** est recommandée pour la fiabilité.
Alternative moins chère/plus simple : **Twilio** ou **Verify API**.

**Algorithme d'envoi OTP :**
```python
def send_whatsapp_otp(phone_number):
    code = generate_random_code(6)
    user = User.objects.get(phone=phone_number)
    user.otp_code = code
    user.otp_created_at = now()
    user.save()
    
    # Appel API
    whatsapp_api.send_message(
        to=phone_number,
        template="your_auth_code",
        variables=[code]
    )
```

## 4. Plan de Migration

1.  **Phase 1 (Modèles)** : Mettre à jour `CustomUser` (rendre email nullable, phone unique).
2.  **Phase 2 (Backend)** : Implémenter le `ModelBackend` personnalisé pour authentifier sans mot de passe.
3.  **Phase 3 (Google Post-Auth)** : Créer la vue "Force Phone Verification" interceptant les logins sociaux incomplets.
4.  **Phase 4 (WhatsApp Flow)** : Créer les vues de saisie numéro et saisie OTP.

---

## ✅ Avantages Sécurité
-   **Anti-Bruteforce** : OTP expire après 5 minutes.
-   **Zéro mot de passe** : Élimine le risque de mots de passe faibles.
-   **Récupération** : Le compte est lié à la carte SIM, très difficile à pirater à distance sans accès physique ou SIM swap (qui est rare comparé au phishing).
