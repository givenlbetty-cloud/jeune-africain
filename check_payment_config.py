#!/usr/bin/env python
"""
Vérification Configuration Paiements
Utilisation: python check_payment_config.py
"""

import os
import sys
from pathlib import Path

def check_env_variable(name, required=True):
    """Vérifier si une variable d'environnement est configurée"""
    value = os.getenv(name)
    
    if not value:
        status = "❌ MANQUANT" if required else "⚠️  OPTIONNEL"
        print(f"  {status}: {name}")
        return False
    
    # Masquer les vraies valeurs
    masked = value[:10] + "***" if len(value) > 10 else "***"
    print(f"  ✅ {name} = {masked}")
    return True

def main():
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION CONFIGURATION PAIEMENTS")
    print("="*60 + "\n")
    
    # Charger .env si existe
    env_file = Path('.env') if Path('.env').exists() else Path('.env.production')
    
    if env_file.exists():
        print(f"📂 Fichier trouvé: {env_file}\n")
        # Charger variables
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print("⚠️  Aucun fichier .env trouvé!\n")
    
    # Vérifications
    all_ok = True
    
    # STRIPE
    print("🟦 STRIPE (Cartes bancaires)")
    all_ok &= check_env_variable('STRIPE_API_KEY')
    all_ok &= check_env_variable('STRIPE_PUBLISHABLE_KEY')
    all_ok &= check_env_variable('STRIPE_WEBHOOK_SECRET')
    print()
    
    # PAYPAL
    print("🟦 PAYPAL (Comptes)")
    all_ok &= check_env_variable('PAYPAL_CLIENT_ID')
    all_ok &= check_env_variable('PAYPAL_CLIENT_SECRET')
    all_ok &= check_env_variable('PAYPAL_WEBHOOK_ID')
    print()
    
    # AIRTEL MONEY
    print("🟦 AIRTEL MONEY (Mobile Money)")
    all_ok &= check_env_variable('AIRTEL_API_KEY')
    all_ok &= check_env_variable('AIRTEL_API_SECRET')
    all_ok &= check_env_variable('AIRTEL_MERCHANT_ID', required=False)
    print()
    
    # M-PESA
    print("🟦 M-PESA (Mobile Kenya)")
    all_ok &= check_env_variable('MPESA_CONSUMER_KEY')
    all_ok &= check_env_variable('MPESA_CONSUMER_SECRET')
    all_ok &= check_env_variable('MPESA_SHORTCODE')
    all_ok &= check_env_variable('MPESA_PASSKEY')
    print()
    
    # ORANGE MONEY
    print("🟦 ORANGE MONEY (Mobile RDC)")
    all_ok &= check_env_variable('ORANGE_MONEY_API_KEY', required=False)
    all_ok &= check_env_variable('ORANGE_MONEY_API_SECRET', required=False)
    all_ok &= check_env_variable('ORANGE_MONEY_MERCHANT_ID', required=False)
    print()
    
    # GENERAL
    print("🟦 CONFIGURATION GÉNÉRALE")
    all_ok &= check_env_variable('DEBUG')
    all_ok &= check_env_variable('SECRET_KEY')
    all_ok &= check_env_variable('ALLOWED_HOSTS')
    all_ok &= check_env_variable('DATABASE_URL')
    print()
    
    # EMAIL
    print("🟦 EMAIL (Pour confirmations paiement)")
    all_ok &= check_env_variable('EMAIL_HOST')
    all_ok &= check_env_variable('EMAIL_HOST_USER')
    all_ok &= check_env_variable('EMAIL_HOST_PASSWORD')
    all_ok &= check_env_variable('DEFAULT_FROM_EMAIL', required=False)
    print()
    
    # Résumé
    print("="*60)
    if all_ok:
        print("✅ TOUS LES PAIEMENTS CONFIGURÉS!")
        print("="*60)
        print("\nProchaines étapes:")
        print("  1. Redémarrer l'application")
        print("  2. Tester les webhooks")
        print("  3. Tester un paiement en mode test")
        return 0
    else:
        print("❌ CONFIGURATION INCOMPLÈTE")
        print("="*60)
        print("\nVeuillez configurer les variables manquantes:")
        print("  1. Ouvrir .env")
        print("  2. Remplir les valeurs manquantes")
        print("  3. Relancer ce script")
        return 1

if __name__ == '__main__':
    sys.exit(main())
