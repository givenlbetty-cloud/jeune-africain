"""
Vues pour le flux de paiement Mobile Money
Gère: Sélection réseau → Confirmation → Vérification OTP → Succès
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction
from decimal import Decimal
import uuid
import logging

from catalogue.models import Book
from catalogue.payment_gateways import Payment, MonerooPaymentGateway
from catalogue.payment_mobilemoney import flutterwave
from users.models import CustomUser

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def mobilemoney_payment_flow(request, book_id):
    """
    Flux complet de paiement Mobile Money
    GET: Afficher le formulaire
    POST: Traiter la commande
    
    Query parameters:
    - network: Réseau prédéfini (airtel, orange, vodacom, moov)
    - phone: Numéro de téléphone prédéfini
    """
    book = get_object_or_404(Book, id=book_id)
    user = request.user
    
    # Récupérer paramètres query pour pré-remplissage
    pre_selected_network = request.GET.get('network', '')
    pre_selected_phone = request.GET.get('phone', '')
    
    if request.method == 'GET':
        # Afficher le formulaire de saisie
        context = {
            'book': book,
            'amount': book.price or Decimal('5.00'),
            'user_email': user.email,
            'user_phone': pre_selected_phone or getattr(user, 'phone_number', ''),
            'user_name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'networks': flutterwave.get_networks(),
            'pre_selected_network': pre_selected_network,
        }
        return render(request, 'payment/mobilemoney_flow.html', context)
    
    elif request.method == 'POST':
        # REDIRECT TO MONEROO IF CONFIGURED
        import os
        if os.getenv('USE_MONEROO_FOR_ALL', 'False') == 'True':
             # Create a temporary payment object to use the gateway
            amount_str = request.POST.get('amount', '').strip()
            try:
                amount = Decimal(amount_str) if amount_str else (book.price or Decimal('5.00'))
            except:
                amount = book.price or Decimal('5.00')
            
            # Assuming book prices are in CDF
            EXCHANGE_RATE = Decimal('1.00')
            amount_cdf = amount * EXCHANGE_RATE
                
            phone = request.POST.get('phone_number', '').strip()
            network = request.POST.get('network', '').strip()
            
            transaction_ref = f"BNC_{uuid.uuid4().hex[:12].upper()}"
            
            payment = Payment.objects.create(
                user=user,
                book=book,
                amount=amount_cdf,
                currency='CDF', # Moneroo handles conversion if needed
                transaction_id=transaction_ref,
                payment_method='mobile_money',
                status='pending',
                phone_number=phone
            )
            
            # Map network to Moneroo provider
            moneroo_network = network.lower()
            provider = 'mobile_money' # Default
            
            if 'vodacom' in moneroo_network or 'mpesa' in moneroo_network:
                provider = 'mpesa'
            elif 'orange' in moneroo_network:
                provider = 'orange_money'
            elif 'airtel' in moneroo_network:
                provider = 'airtel_money'
                
            payment.mobile_money_provider = provider
            payment.save()
            
            gateway = MonerooPaymentGateway(payment)
            result = gateway.initiate_payment()
            
            if result.get('success') and result.get('url'):
                 return JsonResponse({
                    'success': True,
                    'redirect_url': result['url'], # Frontend should redirect here
                    'moneroo': True
                })
            else:
                 return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Erreur Moneroo'),
                }, status=400)

        # Traiter la commande (Legacy Flutterwave)
        return _process_mobilemoney_payment(request, book, user)


def _process_mobilemoney_payment(request, book, user):
    """Traiter la requête de paiement"""
    
    # Récupérer les données du formulaire
    phone = request.POST.get('phone_number', '').strip()
    email = request.POST.get('email', '').strip()
    name = request.POST.get('full_name', '').strip()
    network = request.POST.get('network', '').strip()
    
    # Convertir le montant avec gestion d'erreur
    try:
        amount_str = request.POST.get('amount', '').strip()
        if amount_str:
            amount = Decimal(amount_str)
        else:
            amount = book.price or Decimal('5.00')
    except:
        amount = book.price or Decimal('5.00')
    
    # Valider les données
    if not all([phone, email, name, network]):
        return JsonResponse({
            'success': False,
            'error': 'Tous les champs sont requis',
        }, status=400)
    
    # Valider le réseau
    if network not in flutterwave.MOBILE_NETWORKS:
        return JsonResponse({
            'success': False,
            'error': 'Réseau invalide',
        }, status=400)
    
    # Valider le numéro de téléphone
    valid, result = flutterwave.validate_phone_number(phone)
    if not valid:
        return JsonResponse({
            'success': False,
            'error': result,
        }, status=400)
    
    phone = result  # Utiliser le numéro formaté
    
    # Valider le montant
    valid, error_msg = flutterwave.validate_amount(amount, network)
    if not valid:
        return JsonResponse({
            'success': False,
            'error': error_msg,
        }, status=400)
    
    try:
        with db_transaction.atomic():
            # Créer une référence unique pour la transaction
            transaction_ref = f"BNC_{uuid.uuid4().hex[:12].upper()}"
            
            # Créer la requête de paiement
            payment_response = flutterwave.create_payment_request(
                user_email=email,
                user_phone=phone,
                user_name=name,
                amount=amount,
                network=network,
                book_id=str(book.id),
                transaction_ref=transaction_ref,
            )
            
            if not payment_response.get('success'):
                return JsonResponse({
                    'success': False,
                    'error': payment_response.get('error', 'Erreur de paiement'),
                }, status=400)
            
            # Créer l'enregistrement de paiement en base
            # Mapper réseau à provider
            network_to_provider = {
                'airtel': 'airtel',
                'orange': 'orange',
                'vodacom': 'mpesa',
                'moov': 'other'
            }
            
            payment = Payment.objects.create(
                user=user,
                book=book,
                amount=amount,
                currency='CDF',
                transaction_id=transaction_ref,
                external_transaction_id=payment_response.get('transaction_id', ''),
                payment_method='mobile_money',
                status='pending',
                mobile_money_provider=network_to_provider.get(network, 'other'),
                phone_number=phone,
                webhook_data={
                    'network': network,
                    'email': email,
                    'name': name,
                    'demo_mode': payment_response.get('demo_mode', False),
                    'flutterwave_response': payment_response,
                }
            )
            
            logger.info(f"Payment created: {payment.id} for book {book.id}")
            
            # Retourner la réponse avec confirmation
            return JsonResponse({
                'success': True,
                'payment_id': str(payment.id),
                'transaction_ref': transaction_ref,
                'amount': str(amount),
                'network': network,
                'phone': phone,
                'message': payment_response.get('message', 'En attente de confirmation'),
                'demo_mode': payment_response.get('demo_mode', False),
            })
    
    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors du traitement du paiement',
        }, status=500)


@login_required
@require_http_methods(["GET"])
def mobilemoney_confirmation(request, payment_id):
    """
    Page de confirmation - Attendre la réponse du téléphone
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        messages.error(request, 'Paiement non trouvé')
        return redirect('home')
    
    context = {
        'payment': payment,
        'book': payment.book,
        'amount': payment.amount,
        'network': payment.mobile_money_provider or 'Unknown',
        'phone': payment.phone_number or 'Unknown',
        'transaction_ref': payment.transaction_id,
    }
    
    return render(request, 'payment/mobilemoney_confirmation.html', context)


@login_required
@require_http_methods(["POST"])
def mobilemoney_verify_otp(request, payment_id):
    """
    Vérifier le code OTP entré par l'utilisateur
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Paiement non trouvé',
        }, status=404)
    
    otp = request.POST.get('otp', '').strip()
    
    if not otp:
        return JsonResponse({
            'success': False,
            'error': 'Veuillez entrer le code OTP',
        }, status=400)
    
    try:
        # Appeler Flutterwave pour confirmer la charge
        result = flutterwave.initiate_charge(
            transaction_id=payment.external_transaction_id,
            otp=otp,
        )
        
        if result.get('success'):
            # Mettre à jour le paiement
            payment.status = 'completed'
            payment.save()
            
            # Donner accès au livre
            # request.user.library.add(payment.book) # FIX: CustomUser has no library field
            # Access is checked via Payment model directly
            pass
            
            logger.info(f"Payment successful: {payment.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Paiement confirmé! Le livre est maintenant accessible.',
                'redirect_url': f'/fr/books/{payment.book.id}/',
            })
        else:
            payment.status = 'failed'
            payment.save()
            
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erreur de vérification OTP'),
            }, status=400)
    
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors de la vérification',
        }, status=500)


@login_required
@require_http_methods(["GET"])
def mobilemoney_check_status(request, payment_id):
    """
    Vérifier le statut d'un paiement (via AJAX)
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Paiement non trouvé',
        }, status=404)
    
    # Vérifier avec Flutterwave si statut encore pending
    if payment.status == 'pending':
        result = flutterwave.verify_transaction(payment.external_transaction_id)
        
        if result.get('success'):
            if result.get('status') == 'successful':
                payment.status = 'completed'
                payment.save()
                
                # Donner accès au livre
                # request.user.library.add(payment.book) # FIX: CustomUser has no library field
                # Access is checked via Payment model directly
                pass
    
    return JsonResponse({
        'success': True,
        'payment_id': str(payment.id),
        'status': payment.status,
        'message': f'Statut: {payment.get_status_display()}',
    })


@login_required
@require_http_methods(["GET"])
def mobilemoney_success(request, payment_id):
    """
    Page de succès du paiement
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user, status='completed')
    except Payment.DoesNotExist:
        messages.error(request, 'Paiement non validé')
        return redirect('home')
    
    context = {
        'payment': payment,
        'book': payment.book,
        'amount': payment.amount,
        'network': payment.mobile_money_provider or 'Unknown',
    }
    
    return render(request, 'payment/mobilemoney_success.html', context)


@login_required
@require_http_methods(["GET"])
def mobilemoney_failed(request, payment_id):
    """
    Page d'erreur de paiement
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user, status='failed')
    except Payment.DoesNotExist:
        messages.error(request, 'Paiement non trouvé')
        return redirect('home')
    
    context = {
        'payment': payment,
        'book': payment.book,
        'error': 'Paiement refusé ou échoué',
    }
    
    return render(request, 'payment/mobilemoney_failed.html', context)
