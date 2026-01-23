import os
import sys
from dotenv import load_dotenv

def check_config():
    print("🔍 Vérification de la configuration .env...\n")
    
    # Charger les variables
    load_dotenv()
    
    errors = []
    warnings = []
    
    # 1. Vérification Moneroo
    moneroo_key = os.getenv('MONEROO_API_KEY')
    
    if not moneroo_key or 'votre_cle_unique' in moneroo_key:
        errors.append("❌ MONEROO_API_KEY est manquant ou contient une valeur par défaut.")
    else:
        print(f"✅ Moneroo API Key: Configuré ({moneroo_key[:10]}...)")

    # 2. Vérification Google OAuth
    google_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    if not google_id or 'your-client-id' in google_id:
        warnings.append("⚠️  GOOGLE_OAUTH_CLIENT_ID semble être une valeur par défaut.")
    else:
        print(f"✅ Google Client ID: Configuré ({google_id[:15]}...)")

    # 3. Vérification Email
    email_user = os.getenv('EMAIL_HOST_USER')
    email_pass = os.getenv('EMAIL_HOST_PASSWORD')
    
    if not email_user or 'your-email' in email_user:
        warnings.append("⚠️  EMAIL_HOST_USER non configuré.")
    elif not email_pass:
        warnings.append("⚠️  EMAIL_HOST_PASSWORD non configuré.")
    else:
        print(f"✅ Email: Configuré ({email_user})")

    # Résumé
    print("\n" + "="*50)
    if errors:
        print(f"🔴 {len(errors)} ERREURS BLOQUANTES :")
        for err in errors:
            print(err)
        print("\nL'application ne pourra pas accepter de paiements.")
    else:
        print("🟢 Configuration Critique OK !")
        
    if warnings:
        print(f"\n🟡 {len(warnings)} AVERTISSEMENTS :")
        for warn in warnings:
            print(warn)
            
    if not errors and not warnings:
        print("\n✨ TOUT EST PARFAIT ! Vous êtes prêt pour la production.")

if __name__ == "__main__":
    check_config()
