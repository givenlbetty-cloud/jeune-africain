"""
PHASE 6 PART 2: ENHANCED PAYMENT SYSTEM WITH WEBHOOKS & NOTIFICATIONS
Improve payment flow with better error handling and user feedback
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
import json
import hmac
import hashlib
from decimal import Decimal

from catalogue.models import Payment, Book, UserPurchase
from catalogue.payment_gateways import get_payment_gateway


# ============================================================================
# ENHANCED PAYMENT VIEWS WITH NOTIFICATIONS
# ============================================================================

@login_required(login_url='users:login')
def initiate_payment_enhanced(request, book_id):
    """
    Enhanced payment initiation with validation and UI feedback
    """
    try:
        book = get_object_or_404(Book, id=book_id, is_published=True)
        
        # Validation 1: Check if user already purchased
        existing = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        
        if existing:
            return JsonResponse({
                'success': False,
                'error': 'Vous avez déjà acheté ce livre.',
                'message': 'Accédez à votre bibliothèque pour lire ce livre.'
            }, status=400)
        
        # Validation 2: Check pending payments
        pending = Payment.objects.filter(
            user=request.user,
            book=book,
            status__in=['PENDING', 'PROCESSING']
        ).exists()
        
        if pending:
            return JsonResponse({
                'success': False,
                'error': 'Un paiement est déjà en cours pour ce livre.',
                'message': 'Veuillez attendre la confirmation du paiement précédent.'
            }, status=400)
        
        # Get payment method
        payment_method = request.POST.get('payment_method', 'CREDIT_CARD').upper()
        
        # Validate payment method
        valid_methods = ['CREDIT_CARD', 'MOBILE_MONEY', 'MPESA', 'AIRTEL', 'ORANGE']
        if payment_method not in valid_methods:
            return JsonResponse({
                'success': False,
                'error': 'Méthode de paiement invalide.'
            }, status=400)
        
        # Create payment record
        import uuid
        transaction_id = f"BNC_{uuid.uuid4().hex[:16].upper()}"
        final_price = book.get_final_price() if hasattr(book, 'get_final_price') else Decimal(book.price)
        
        payment = Payment.objects.create(
            user=request.user,
            book=book,
            amount=final_price,
            currency='CDF',
            transaction_id=transaction_id,
            payment_method=payment_method,
            status='PENDING'
        )
        
        # Get appropriate gateway
        gateway = get_payment_gateway(payment)
        
        # Initiate payment
        result = gateway.initiate_payment()
        
        if result.get('success'):
            payment.status = 'PROCESSING'
            payment.provider_reference = result.get('reference_id', '')
            payment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Redirection vers la passerelle de paiement...',
                'redirect_url': result.get('redirect_url'),
                'payment_id': str(payment.id)
            })
        else:
            payment.status = 'FAILED'
            payment.error_message = result.get('error', 'Erreur inconnue')
            payment.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Impossible d\'initier le paiement.',
                'message': result.get('error', 'Veuillez réessayer plus tard.')
            }, status=500)
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment initiation error: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'error': 'Erreur système.',
            'message': 'Veuillez contacter le support.'
        }, status=500)


@login_required(login_url='users:login')
def payment_success_enhanced(request, payment_id):
    """
    Enhanced payment success page with verification
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Verify payment status before marking as complete
    gateway = get_payment_gateway(payment)
    
    if hasattr(gateway, 'verify_payment'):
        result = gateway.verify_payment()
        
        if result.get('verified'):
            if payment.status != 'COMPLETED':
                payment.status = 'COMPLETED'
                payment.save()
                
                # Create user purchase record
                UserPurchase.objects.get_or_create(
                    user=request.user,
                    book=payment.book,
                    defaults={'purchase_date': payment.created_at}
                )
                
                messages.success(
                    request,
                    f'✅ Votre achat de "{payment.book.title}" a été confirmé!'
                )
    
    context = {
        'payment': payment,
        'book': payment.book,
        'success': payment.status == 'COMPLETED'
    }
    
    return render(request, 'payment/success.html', context)


@login_required(login_url='users:login')
def payment_cancel(request, payment_id):
    """
    Handle payment cancellation
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status in ['PENDING', 'PROCESSING']:
        payment.status = 'CANCELLED'
        payment.error_message = 'Paiement annulé par l\'utilisateur'
        payment.save()
        
        messages.warning(
            request,
            'Votre paiement a été annulé. Vous pouvez réessayer quand vous le souhaitez.'
        )
    
    return redirect('catalogue:book_detail', book_id=payment.book.id)


# ============================================================================
# WEBHOOK HANDLERS - STRIPE
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    try:
        event_data = json.loads(request.body)
        event_type = event_data.get('type')
        
        # Verify webhook signature (optional but recommended)
        stripe_signature = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if event_type == 'payment_intent.succeeded':
            handle_stripe_payment_success(event_data)
        elif event_type == 'payment_intent.payment_failed':
            handle_stripe_payment_failed(event_data)
        elif event_type == 'charge.refunded':
            handle_stripe_refund(event_data)
        
        return JsonResponse({'status': 'received'}, status=200)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Stripe webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


def handle_stripe_payment_success(event_data):
    """Process successful Stripe payment"""
    payment_intent = event_data.get('data', {}).get('object', {})
    metadata = payment_intent.get('metadata', {})
    payment_id = metadata.get('payment_id')
    
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            if payment.status != 'COMPLETED':
                payment.status = 'COMPLETED'
                payment.provider_reference = payment_intent.get('id')
                payment.save()
                
                # Create purchase record
                UserPurchase.objects.get_or_create(
                    user=payment.user,
                    book=payment.book
                )
                
                # Log transaction
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Stripe payment completed: {payment_id}")
        except Payment.DoesNotExist:
            pass


def handle_stripe_payment_failed(event_data):
    """Process failed Stripe payment"""
    payment_intent = event_data.get('data', {}).get('object', {})
    metadata = payment_intent.get('metadata', {})
    payment_id = metadata.get('payment_id')
    
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'FAILED'
            payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Erreur de paiement')
            payment.save()
        except Payment.DoesNotExist:
            pass


def handle_stripe_refund(event_data):
    """Process Stripe refund"""
    charge = event_data.get('data', {}).get('object', {})
    # Handle refund logic here


# ============================================================================
# WEBHOOK HANDLERS - MOBILE MONEY (MPesa, Airtel, Orange)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def mobile_money_webhook(request, provider):
    """
    Handle Mobile Money webhook from different providers
    MPesa, Airtel, Orange, etc.
    """
    try:
        # Verify webhook signature based on provider
        if not verify_webhook_signature(request, provider):
            return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        body = json.loads(request.body)
        
        if provider.lower() == 'mpesa':
            return handle_mpesa_webhook(body)
        elif provider.lower() == 'airtel':
            return handle_airtel_webhook(body)
        elif provider.lower() == 'orange':
            return handle_orange_webhook(body)
        else:
            return JsonResponse({'error': 'Unknown provider'}, status=400)
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Mobile Money webhook error ({provider}): {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


def verify_webhook_signature(request, provider):
    """Verify webhook authenticity based on provider"""
    from django.conf import settings
    
    # Get provider secret from settings
    secret_key = getattr(settings, f'{provider.upper()}_WEBHOOK_SECRET', None)
    
    if not secret_key:
        return False
    
    # Get signature from header
    signature = request.META.get(f'HTTP_{provider.upper()}_SIGNATURE')
    
    if not signature:
        return False
    
    # Verify signature
    body_hash = hmac.new(
        secret_key.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return signature == body_hash


def handle_mpesa_webhook(body):
    """Handle M-Pesa payment notification"""
    # Extract payment details
    result_code = body.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    result_desc = body.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
    
    if result_code == 0:  # Success
        callback_metadata = body.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {})
        items = {item['Name']: item['Value'] for item in callback_metadata.get('Item', [])}
        
        amount = items.get('Amount')
        phone = items.get('PhoneNumber')
        transaction_id = items.get('MpesaReceiptNumber')
        
        # Find and update payment
        try:
            payment = Payment.objects.get(provider_reference=transaction_id)
            payment.status = 'COMPLETED'
            payment.save()
            
            # Create purchase
            UserPurchase.objects.get_or_create(
                user=payment.user,
                book=payment.book
            )
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'ResultCode': 0})


def handle_airtel_webhook(body):
    """Handle Airtel Money payment notification"""
    status = body.get('transaction', {}).get('status')
    
    if status == 'SUCCESS':
        airtel_ref = body.get('transaction', {}).get('airtel_money_id')
        amount = body.get('transaction', {}).get('amount')
        
        try:
            payment = Payment.objects.get(provider_reference=airtel_ref)
            payment.status = 'COMPLETED'
            payment.save()
            
            UserPurchase.objects.get_or_create(
                user=payment.user,
                book=payment.book
            )
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'OK'})


def handle_orange_webhook(body):
    """Handle Orange Money payment notification"""
    transaction_status = body.get('transactionStatus')
    
    if transaction_status == '00':  # Success
        transaction_id = body.get('transactionId')
        
        try:
            payment = Payment.objects.get(provider_reference=transaction_id)
            payment.status = 'COMPLETED'
            payment.save()
            
            UserPurchase.objects.get_or_create(
                user=payment.user,
                book=payment.book
            )
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'ok'})


# ============================================================================
# PAYMENT STATUS & HISTORY
# ============================================================================

@login_required(login_url='users:login')
def payment_status_api(request, payment_id):
    """
    API endpoint to check payment status
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return JsonResponse({
        'status': payment.status,
        'amount': str(payment.amount),
        'currency': payment.currency,
        'created_at': payment.created_at.isoformat(),
        'book': {
            'id': str(payment.book.id),
            'title': payment.book.title,
            'author': str(payment.book.authors.first()) if payment.book.authors.exists() else 'Unknown'
        },
        'error': payment.error_message if payment.status == 'FAILED' else None
    })


@login_required(login_url='users:login')
def payment_history_api(request):
    """
    API endpoint for payment history
    """
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    data = [
        {
            'id': str(p.id),
            'book': p.book.title,
            'amount': str(p.amount),
            'status': p.status,
            'date': p.created_at.isoformat(),
            'method': p.payment_method
        }
        for p in payments[:20]  # Last 20 transactions
    ]
    
    return JsonResponse({'payments': data})
