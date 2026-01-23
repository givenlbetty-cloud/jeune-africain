"""
Views Moneiro - Intégration Paiement Minimaliste pour BNC RDC
Gère M-Pesa, Orange Money, Airtel Money, Visa, Mastercard
"""

import json
import os
import logging
from decimal import Decimal
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════
# CONFIG MONEIRO
# ════════════════════════════════════════════════════════════════════════

MONEIRO_API_KEY = os.getenv('MONEIRO_API_KEY')
MONEIRO_MERCHANT_ID = os.getenv('MONEIRO_MERCHANT_ID')
MONEIRO_API_SECRET = os.getenv('MONEIRO_API_SECRET')
MONEIRO_API_URL = os.getenv('MONEIRO_API_URL', 'https://api.moneiro.com/v1')

# Valider config
if not all([MONEIRO_API_KEY, MONEIRO_MERCHANT_ID, MONEIRO_API_SECRET]):
    logger.warning("⚠️ MONEIRO not configured - check your .env file")


# ════════════════════════════════════════════════════════════════════════
# 1️⃣ PROCESS PAYMENT - Initier un paiement
# ════════════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(['POST'])
def process_payment(request):
    """
    Initie un paiement Moneiro
    
    POST /process-payment/
    
    Données requises (form ou JSON):
    - montant: decimal (ex: 100.00)
    - devise: str ('USD' ou 'CDF')
    - methode_paiement: str ('mpesa', 'orange_money', 'airtel_money', 'visa', 'mastercard')
    - reference: str (ID unique de la commande)
    - book_id: int (optionnel, ID du livre à acheter)
    
    Retourne:
    - Redirect vers page paiement Moneiro
    - Ou JSON avec erreur
    """
    try:
        # Récupérer données
        montant = request.POST.get('montant') or request.GET.get('montant')
        devise = request.POST.get('devise', 'USD')
        methode_paiement = request.POST.get('methode_paiement')
        reference = request.POST.get('reference') or request.POST.get('order_id')
        book_id = request.POST.get('book_id')
        
        # Valider
        if not all([montant, methode_paiement, reference]):
            return JsonResponse(
                {'error': 'Données manquantes: montant, methode_paiement, reference'},
                status=400
            )
        
        montant = Decimal(montant)
        
        # Valider devise
        if devise not in ['USD', 'CDF']:
            return JsonResponse({'error': 'Devise invalide (USD ou CDF)'}, status=400)
        
        # Valider méthode
        methodes_valides = ['mpesa', 'orange_money', 'airtel_money', 'visa', 'mastercard']
        if methode_paiement not in methodes_valides:
            return JsonResponse(
                {'error': f'Méthode invalide. Utilisez: {", ".join(methodes_valides)}'},
                status=400
            )
        
        # Créer la commande en base (optionnel - vous pouvez le faire avant)
        from catalogue.models_commande import Commande
        try:
            commande = Commande.objects.create(
                user=request.user,
                reference=reference,
                montant=montant,
                devise=devise,
                methode_paiement=methode_paiement,
                book_id=book_id,
                status='PENDING'
            )
            logger.info(f"✅ Commande créée: {reference}")
        except Exception as e:
            logger.error(f"❌ Erreur création commande: {str(e)}")
            return JsonResponse({'error': f'Erreur création commande: {str(e)}'}, status=500)
        
        # Préparer payload Moneiro
        headers = {
            'Authorization': f'Bearer {MONEIRO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'merchant_id': MONEIRO_MERCHANT_ID,
            'amount': str(montant),
            'currency': devise,
            'payment_method': methode_paiement,
            'customer_email': request.user.email,
            'customer_phone': request.POST.get('phone', ''),
            'order_id': reference,
            'description': f'Achat BNC - Commande {reference}',
            'success_url': request.build_absolute_uri('/paiement-succes/'),
            'cancel_url': request.build_absolute_uri('/paiement-annule/'),
            'notify_url': request.build_absolute_uri('/webhook-moneiro/'),
        }
        
        # Appel API Moneiro
        try:
            response = requests.post(
                f'{MONEIRO_API_URL}/payments',
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            payment_url = data.get('payment_url') or data.get('redirect_url')
            
            if not payment_url:
                logger.error(f"❌ Pas d'URL de paiement reçue: {data}")
                return JsonResponse(
                    {'error': 'Erreur API Moneiro - pas d\'URL'},
                    status=500
                )
            
            logger.info(f"✅ Paiement initié: {reference} -> {payment_url}")
            
            # Rediriger vers paiement
            return redirect(payment_url)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API Moneiro: {str(e)}")
            return JsonResponse(
                {'error': f'Erreur connexion Moneiro: {str(e)}'},
                status=500
            )
    
    except ValueError as e:
        logger.error(f"❌ Erreur validation: {str(e)}")
        return JsonResponse({'error': f'Montant invalide: {str(e)}'}, status=400)
    
    except Exception as e:
        logger.error(f"❌ Erreur process_payment: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erreur serveur: {str(e)}'}, status=500)


# ════════════════════════════════════════════════════════════════════════
# 2️⃣ WEBHOOK MONEIRO - Confirmation paiement
# ════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(['POST'])
def moneiro_webhook(request):
    """
    Webhook pour recevoir les confirmations de paiement Moneiro
    
    POST /webhook-moneiro/
    
    Moneiro envoie:
    {
        "event": "payment.success" | "payment.failed",
        "data": {
            "order_id": "COMMANDE-123",
            "amount": "100.00",
            "currency": "USD",
            "status": "SUCCESS" | "FAILED",
            "transaction_id": "TXN-123456",
            "payment_method": "mpesa"
        }
    }
    """
    try:
        # Parser JSON
        data = json.loads(request.body)
        logger.info(f"📩 Webhook reçu: {data}")
        
        event = data.get('event', '')
        payload = data.get('data', {})
        
        order_id = payload.get('order_id')
        status = payload.get('status', '').upper()
        transaction_id = payload.get('transaction_id')
        
        # Valider
        if not order_id:
            logger.error("❌ Pas d'order_id dans webhook")
            return JsonResponse({'error': 'Missing order_id'}, status=400)
        
        # Importer modèle
        from catalogue.models_commande import Commande
        
        try:
            commande = Commande.objects.get(reference=order_id)
        except Commande.DoesNotExist:
            logger.error(f"❌ Commande introuvable: {order_id}")
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        # Traiter selon le statut
        if status == 'SUCCESS':
            logger.info(f"✅ Paiement réussi: {order_id}")
            
            # Mettre à jour la commande
            commande.marquer_comme_payee(transaction_id)
            
            # Accorder l'accès au livre (optionnel)
            if commande.book:
                try:
                    commande.user.access_books.add(commande.book)
                    logger.info(f"✅ Accès livre accordé: {commande.user.id} -> {commande.book.id}")
                except Exception as e:
                    logger.error(f"❌ Erreur accès livre: {str(e)}")
            
            # Email de confirmation (optionnel)
            try:
                from django.core.mail import send_mail
                send_mail(
                    f'Paiement confirmé - Commande {order_id}',
                    f'Votre paiement de {commande.montant} {commande.devise} a été reçu.\n'
                    f'Transaction: {transaction_id}',
                    'noreply@bnc-library.com',
                    [commande.user.email],
                    fail_silently=True
                )
                logger.info(f"📧 Email confirmation envoyé: {commande.user.email}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur envoi email: {str(e)}")
            
            return JsonResponse({'status': 'success'}, status=200)
        
        elif status == 'FAILED':
            logger.warning(f"❌ Paiement échoué: {order_id}")
            commande.status = 'FAILED'
            commande.save()
            
            return JsonResponse({'status': 'failed'}, status=200)
        
        elif status == 'PENDING':
            logger.info(f"⏳ Paiement en attente: {order_id}")
            commande.status = 'PENDING'
            commande.save()
            
            return JsonResponse({'status': 'pending'}, status=200)
        
        else:
            logger.warning(f"⚠️ Statut inconnu: {status}")
            return JsonResponse({'status': 'unknown'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("❌ JSON invalide dans webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        logger.error(f"❌ Erreur webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


# ════════════════════════════════════════════════════════════════════════
# 3️⃣ PAGES RETOUR (après succès ou annulation)
# ════════════════════════════════════════════════════════════════════════

@login_required
def paiement_succes(request):
    """
    Page affichée après succès du paiement
    GET /paiement-succes/
    """
    reference = request.GET.get('order_id') or request.GET.get('reference')
    
    context = {
        'titre': 'Paiement Réussi ✅',
        'message': 'Votre paiement a été reçu avec succès!',
        'reference': reference,
    }
    
    return JsonResponse(context)


@login_required
def paiement_annule(request):
    """
    Page affichée si l'utilisateur annule le paiement
    GET /paiement-annule/
    """
    reference = request.GET.get('order_id') or request.GET.get('reference')
    
    context = {
        'titre': 'Paiement Annulé',
        'message': 'Vous avez annulé le paiement.',
        'reference': reference,
    }
    
    return JsonResponse(context)
