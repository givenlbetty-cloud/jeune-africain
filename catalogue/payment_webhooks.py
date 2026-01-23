"""
Webhook handlers pour la réconciliation des paiements.
Gère les callbacks de Stripe, PayPal, Mobile Money, etc.
"""

import json
import logging
import hashlib
import hmac
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.mail import send_mail
from catalogue.models import Payment, Book
from django.utils import timezone

logger = logging.getLogger(__name__)


# ==================== STRIPE WEBHOOKS ====================

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Webhook pour les événements Stripe.
    Réconcilie les paiements et met à jour les statuts.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return JsonResponse({'error': 'Webhook not configured'}, status=400)
    
    try:
        import stripe
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"Stripe webhook invalid payload: {e}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except Exception as e:
        logger.error(f"Stripe webhook signature error: {e}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        handle_stripe_payment_succeeded(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        handle_stripe_payment_failed(event['data']['object'])
    elif event['type'] == 'charge.refunded':
        handle_stripe_refund(event['data']['object'])
    
    return JsonResponse({'status': 'success'})


def handle_stripe_payment_succeeded(payment_intent):
    """Traiter un paiement Stripe réussi"""
    try:
        transaction_id = payment_intent['id']
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            payment_method='STRIPE'
        )
        
        # Mettre à jour le statut
        payment.status = 'COMPLETED'
        payment.external_transaction_id = payment_intent['id']
        payment.processed_at = timezone.now()
        payment.save()
        
        # Marquer le livre comme acheté
        book = payment.book
        user = payment.user
        user.purchased_books.add(book)
        
        # Envoyer confirmation
        send_payment_confirmation_email(payment)
        
        logger.info(f"Payment {transaction_id} completed successfully")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for transaction {transaction_id}")
    except Exception as e:
        logger.error(f"Error handling Stripe payment: {e}")


def handle_stripe_payment_failed(payment_intent):
    """Traiter un paiement Stripe échoué"""
    try:
        transaction_id = payment_intent['id']
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            payment_method='STRIPE'
        )
        
        payment.status = 'FAILED'
        payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
        payment.save()
        
        logger.warning(f"Payment {transaction_id} failed: {payment.error_message}")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for transaction {transaction_id}")


def handle_stripe_refund(charge):
    """Traiter un remboursement Stripe"""
    try:
        transaction_id = charge['id']
        payment = Payment.objects.get(external_transaction_id=transaction_id)
        
        payment.status = 'REFUNDED'
        payment.refunded_at = timezone.now()
        payment.save()
        
        # Retirer l'accès au livre
        book = payment.book
        user = payment.user
        user.purchased_books.remove(book)
        
        logger.info(f"Payment {transaction_id} refunded")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for transaction {transaction_id}")


# ==================== PAYPAL WEBHOOKS ====================

@csrf_exempt
@require_http_methods(["POST"])
def paypal_webhook(request):
    """
    Webhook pour les événements PayPal.
    """
    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Vérifier la signature PayPal
    if not verify_paypal_webhook_signature(request):
        logger.error("PayPal webhook signature invalid")
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    # Traiter les événements
    if event['event_type'] == 'PAYMENT.SALE.COMPLETED':
        handle_paypal_payment_completed(event['resource'])
    elif event['event_type'] == 'PAYMENT.SALE.DENIED':
        handle_paypal_payment_denied(event['resource'])
    elif event['event_type'] == 'PAYMENT.SALE.REFUNDED':
        handle_paypal_payment_refunded(event['resource'])
    
    return JsonResponse({'status': 'success'})


def verify_paypal_webhook_signature(request):
    """Vérifier la signature du webhook PayPal"""
    try:
        import requests
        
        webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', None)
        if not webhook_id:
            return False
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        body = {
            'transmission_id': request.META.get('HTTP_PAYPAL_TRANSMISSION_ID'),
            'transmission_time': request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME'),
            'cert_url': request.META.get('HTTP_PAYPAL_CERT_URL'),
            'auth_algo': request.META.get('HTTP_PAYPAL_AUTH_ALGO'),
            'transmission_sig': request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG'),
            'webhook_id': webhook_id,
            'webhook_event': request.body.decode('utf-8'),
        }
        
        # Appel à PayPal pour vérifier
        response = requests.post(
            'https://api.paypal.com/v1/notifications/verify-webhook-signature',
            json=body,
            headers=headers
        )
        
        result = response.json()
        return result.get('verification_status') == 'SUCCESS'
        
    except Exception as e:
        logger.error(f"PayPal signature verification error: {e}")
        return False


def handle_paypal_payment_completed(resource):
    """Traiter un paiement PayPal complété"""
    try:
        transaction_id = resource['id']
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            payment_method='PAYPAL'
        )
        
        payment.status = 'COMPLETED'
        payment.external_transaction_id = transaction_id
        payment.processed_at = timezone.now()
        payment.save()
        
        # Marquer le livre comme acheté
        user = payment.user
        book = payment.book
        user.purchased_books.add(book)
        
        send_payment_confirmation_email(payment)
        logger.info(f"PayPal payment {transaction_id} completed")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for PayPal transaction {transaction_id}")


def handle_paypal_payment_denied(resource):
    """Traiter un paiement PayPal refusé"""
    try:
        transaction_id = resource['id']
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            payment_method='PAYPAL'
        )
        
        payment.status = 'FAILED'
        payment.error_message = 'Payment denied by PayPal'
        payment.save()
        
        logger.warning(f"PayPal payment {transaction_id} denied")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for PayPal transaction {transaction_id}")


def handle_paypal_payment_refunded(resource):
    """Traiter un remboursement PayPal"""
    try:
        transaction_id = resource['id']
        payment = Payment.objects.get(external_transaction_id=transaction_id)
        
        payment.status = 'REFUNDED'
        payment.refunded_at = timezone.now()
        payment.save()
        
        # Retirer l'accès
        user = payment.user
        book = payment.book
        user.purchased_books.remove(book)
        
        logger.info(f"PayPal payment {transaction_id} refunded")
        
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for PayPal transaction {transaction_id}")


# ==================== MOBILE MONEY WEBHOOKS ====================

@csrf_exempt
@require_http_methods(["POST"])
def airtel_money_webhook(request):
    """Webhook pour les paiements Airtel Money"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Vérifier la signature Airtel
    if not verify_airtel_signature(request):
        logger.error("Airtel webhook signature invalid")
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    transaction_id = data.get('transactionId')
    status = data.get('status')
    
    try:
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            payment_method='AIRTEL_MONEY'
        )
        
        if status == 'SUCCESS':
            payment.status = 'COMPLETED'
            payment.external_transaction_id = transaction_id
            payment.processed_at = timezone.now()
            payment.save()
            
            user = payment.user
            book = payment.book
            user.purchased_books.add(book)
            
            send_payment_confirmation_email(payment)
            logger.info(f"Airtel payment {transaction_id} completed")
        else:
            payment.status = 'FAILED'
            payment.error_message = f"Airtel status: {status}"
            payment.save()
            
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for Airtel transaction {transaction_id}")
    
    return JsonResponse({'status': 'received'})


def verify_airtel_signature(request):
    """Vérifier la signature Airtel Money"""
    try:
        api_key = getattr(settings, 'AIRTEL_API_KEY', '')
        signature = request.META.get('HTTP_X_AIRTEL_SIGNATURE', '')
        
        # Airtel utilise HMAC-SHA256
        expected_signature = hmac.new(
            api_key.encode(),
            request.body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Airtel signature verification error: {e}")
        return False


@csrf_exempt
@require_http_methods(["POST"])
def mpesa_webhook(request):
    """Webhook pour les paiements M-Pesa"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    body = data.get('Body', {})
    result = body.get('stkCallback', {})
    
    merchant_request_id = result.get('MerchantRequestID')
    checkout_request_id = result.get('CheckoutRequestID')
    result_code = result.get('ResultCode')
    
    try:
        payment = Payment.objects.get(
            checkout_request_id=checkout_request_id,
            payment_method='MPESA'
        )
        
        if result_code == 0:  # Success
            payment.status = 'COMPLETED'
            payment.external_transaction_id = checkout_request_id
            payment.processed_at = timezone.now()
            payment.save()
            
            user = payment.user
            book = payment.book
            user.purchased_books.add(book)
            
            send_payment_confirmation_email(payment)
            logger.info(f"M-Pesa payment {checkout_request_id} completed")
        else:
            payment.status = 'FAILED'
            payment.error_message = f"M-Pesa error code: {result_code}"
            payment.save()
            
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for M-Pesa transaction {checkout_request_id}")
    
    return JsonResponse({'ResultCode': 0})


# ==================== HELPER FUNCTIONS ====================

def send_payment_confirmation_email(payment):
    """Envoyer un email de confirmation de paiement"""
    try:
        user = payment.user
        book = payment.book
        
        subject = f"Payment Confirmation - {book.title}"
        message = f"""
        Dear {user.first_name or user.email},
        
        Your payment of {payment.amount} {payment.currency} has been successfully processed.
        
        Book: {book.title}
        Transaction ID: {payment.transaction_id}
        Date: {payment.processed_at}
        
        You can now access the book in your library.
        
        Thank you for using BNC Digital Library!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
        
    except Exception as e:
        logger.error(f"Error sending payment confirmation email: {e}")


def reconcile_pending_payments():
    """
    Tâche périodique pour réconcilier les paiements en attente.
    À exécuter via Celery ou manage.py command.
    """
    pending_payments = Payment.objects.filter(status='PENDING')
    
    for payment in pending_payments:
        try:
            if payment.payment_method == 'STRIPE':
                reconcile_stripe_payment(payment)
            elif payment.payment_method == 'PAYPAL':
                reconcile_paypal_payment(payment)
            elif payment.payment_method == 'MPESA':
                reconcile_mpesa_payment(payment)
            elif payment.payment_method == 'AIRTEL_MONEY':
                reconcile_airtel_payment(payment)
                
        except Exception as e:
            logger.error(f"Error reconciling payment {payment.id}: {e}")


def reconcile_stripe_payment(payment):
    """Réconcilier un paiement Stripe"""
    try:
        import stripe
        stripe.api_key = getattr(settings, 'STRIPE_API_KEY', None)
        
        intent = stripe.PaymentIntent.retrieve(payment.transaction_id)
        
        if intent.status == 'succeeded':
            payment.status = 'COMPLETED'
            payment.external_transaction_id = intent.id
            payment.processed_at = timezone.now()
            payment.save()
            
            user = payment.user
            book = payment.book
            user.purchased_books.add(book)
            
    except Exception as e:
        logger.error(f"Error reconciling Stripe payment: {e}")


def reconcile_paypal_payment(payment):
    """Réconcilier un paiement PayPal"""
    try:
        import requests
        
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        
        # Obtenir le token
        auth = (client_id, client_secret)
        headers = {'Accept': 'application/json'}
        
        response = requests.post(
            'https://api.paypal.com/v1/oauth2/token',
            auth=auth,
            headers=headers,
            data={'grant_type': 'client_credentials'}
        )
        
        token = response.json()['access_token']
        
        # Vérifier le paiement
        headers['Authorization'] = f'Bearer {token}'
        
        sale_response = requests.get(
            f'https://api.paypal.com/v1/sale/{payment.transaction_id}',
            headers=headers
        )
        
        sale = sale_response.json()
        
        if sale.get('state') == 'completed':
            payment.status = 'COMPLETED'
            payment.processed_at = timezone.now()
            payment.save()
            
            user = payment.user
            book = payment.book
            user.purchased_books.add(book)
            
    except Exception as e:
        logger.error(f"Error reconciling PayPal payment: {e}")


def reconcile_mpesa_payment(payment):
    """Réconcilier un paiement M-Pesa"""
    # M-Pesa n'a pas d'API query directe - utiliser les webhooks
    pass


def reconcile_airtel_payment(payment):
    """Réconcilier un paiement Airtel"""
    # Similaire à M-Pesa
    pass
