"""
Moneroo Payment Integration for BNC RDC
Handles all payments: Mobile Money (M-Pesa, Orange Money, Airtel Money) & Cards (Visa, Mastercard)
"""

import json
import os
import logging
import hmac
import hashlib
from decimal import Decimal
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import requests
from catalogue.models import Payment, Book

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════
# MONEROO CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

from django.conf import settings as django_settings

MONEROO_API_KEY = getattr(django_settings, 'MONEROO_API_KEY', '') or os.getenv('MONEROO_API_KEY', '')
MONEROO_SECRET_KEY = getattr(django_settings, 'MONEROO_SECRET_KEY', '') or os.getenv('MONEROO_SECRET_KEY', '')
MONEROO_API_URL = 'https://api.moneroo.io/v1'

# Validate configuration
if not MONEROO_API_KEY:
    logger.warning("MONEROO_API_KEY not configured - check .env file")


# ════════════════════════════════════════════════════════════════════════
# PAYMENT FORM DISPLAY
# ════════════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(['GET'])
def payment_form(request):
    """
    Display the payment initiation form
    GET /payment/initiate/
    """
    return render(request, 'payment_moneroo_form.html')


# ════════════════════════════════════════════════════════════════════════
# PAYMENT INITIATION
# ════════════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(['POST'])
def initiate_moneroo_payment(request):
    """
    Initiate a payment via Moneroo
    
    POST /payment/initiate/
    
    Required fields:
    - amount: Decimal (e.g., 100.00)
    - currency: str ('USD' or 'CDF')
    - payment_method: str ('mobile_money' or 'card')
    - reference: str (unique order ID)
    - book_id: int (optional)
    - phone: str (required for mobile_money)
    
    Returns:
    - Redirect to Moneroo payment page
    - Or JSON error response
    """
    try:
        # Extract request data
        amount = request.POST.get('amount')
        currency = request.POST.get('currency', 'USD')
        payment_method = request.POST.get('payment_method', 'mobile_money')
        reference = request.POST.get('reference')
        book_id = request.POST.get('book_id')
        phone = request.POST.get('phone', '')
        
        # Validate required fields
        if not all([amount, reference]):
            logger.error("Missing required fields: amount or reference")
            return JsonResponse(
                {'error': 'amount and reference are required'},
                status=400
            )
        
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            logger.error(f"Invalid amount: {amount}")
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Validate currency
        if currency not in ['USD', 'CDF']:
            logger.error(f"Invalid currency: {currency}")
            return JsonResponse({'error': 'Currency must be USD or CDF'}, status=400)
        
        # Validate payment method
        if payment_method not in ['mobile_money', 'card']:
            logger.error(f"Invalid payment method: {payment_method}")
            return JsonResponse({'error': 'Payment method must be mobile_money or card'}, status=400)
        
        # Create payment in database
        try:
            # Ensure book exists
            from catalogue.models import Book
            if book_id:
                book = Book.objects.get(id=book_id)
            else:
                # Fallback for testing: get first book
                book = Book.objects.first()
                if not book:
                    return JsonResponse({'error': 'No books available'}, status=400)
            
            payment = Payment.objects.create(
                user=request.user,
                transaction_id=reference,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                book=book,
                status='pending',
                phone_number=phone if payment_method == 'mobile_money' else None
            )
            logger.info(f"✅ Payment created: {reference}")
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return JsonResponse({'error': f'Error creating payment: {str(e)}'}, status=500)
        
        # Prepare Moneroo API payload
        payload = {
            'amount': float(amount),
            'currency': currency,
            'customer': {
                'email': request.user.email,
                'first_name': request.user.first_name or 'Client',
                'last_name': request.user.last_name or 'BNC',
                'phone': phone,
            },
            'customer_email': request.user.email,
            'customer_phone': phone,
            'order_id': reference,
            'order_reference': reference,
            'description': f'BNC Library - Order {reference}',
            'payment_method': payment_method,
            'return_url': request.build_absolute_uri('/payment/callback/'),
            'callback_url': request.build_absolute_uri('/api/payments/moneroo-callback/'),
        }
        
        # Call Moneroo API
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {MONEROO_API_KEY}'
            }
            
            response = requests.post(
                f'{MONEROO_API_URL}/payments/initialize',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extract payment URL
            payment_url = (
                data.get('data', {}).get('checkout_url')
                or data.get('data', {}).get('payment_url')
                or data.get('checkout_url')
                or data.get('payment_url')
            )
            
            if not payment_url:
                logger.error(f"No payment/checkout URL in Moneroo response: {data}")
                return JsonResponse(
                    {'error': 'Payment gateway error - no URL returned'},
                    status=500
                )
            
            logger.info(f"✅ Payment initialized: {reference}")
            
            # Redirect to payment page
            return redirect(payment_url)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Moneroo API error: {str(e)}")
            return JsonResponse(
                {'error': f'Payment gateway error: {str(e)}'},
                status=500
            )
    
    except Exception as e:
        logger.error(f"❌ Error in initiate_moneroo_payment: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


# ════════════════════════════════════════════════════════════════════════
# WEBHOOK CALLBACK
# ════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(['POST'])
def moneroo_callback(request):
    """
    Handle Moneroo webhook callback
    
    POST /payment/moneroo-callback/
    
    Moneroo sends:
    {
        "event": "payment.completed",
        "data": {
            "order_id": "CMD-123",
            "amount": 100.00,
            "currency": "USD",
            "status": "completed" | "failed" | "pending",
            "transaction_id": "TXN-xxx",
            "payment_method": "mobile_money" | "card",
            "signature": "hmac_signature"
        }
    }
    """
    try:
        # Parse JSON payload
        raw_body = request.body
        data = json.loads(raw_body)
        
        logger.info(f"📩 Moneroo webhook received: {data.get('event')}")
        
        event = data.get('event', '')
        payload = data.get('data', {})
        
        order_id = payload.get('order_id') or payload.get('order_reference')
        status = payload.get('status', '').lower()
        transaction_id = payload.get('transaction_id')
        signature = payload.get('signature')
        
        # Validate order ID
        if not order_id:
            logger.error("❌ Missing order_id in webhook")
            return JsonResponse({'error': 'Missing order_id'}, status=400)
        
        # Validate signature
        if signature and MONEROO_SECRET_KEY:
            expected_signature = _generate_signature(raw_body, MONEROO_SECRET_KEY)
            if not _verify_signature(signature, expected_signature):
                logger.error(f"❌ Invalid signature for order: {order_id}")
                return JsonResponse({'error': 'Invalid signature'}, status=401)
        
        # Find payment
        try:
            payment = Payment.objects.get(transaction_id=order_id)
        except Payment.DoesNotExist:
            logger.error(f"❌ Payment not found: {order_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Process based on status
        if status == 'completed':
            logger.info(f"✅ Payment completed: {order_id}")
            _handle_payment_success(payment, transaction_id)
            return JsonResponse({'status': 'success'}, status=200)
        
        elif status == 'failed':
            logger.warning(f"❌ Payment failed: {order_id}")
            _handle_payment_failure(payment)
            return JsonResponse({'status': 'failed'}, status=200)
        
        elif status == 'pending':
            logger.info(f"⏳ Payment pending: {order_id}")
            payment.status = 'pending'
            payment.save()
            return JsonResponse({'status': 'pending'}, status=200)
        
        else:
            logger.warning(f"⚠️  Unknown status: {status}")
            return JsonResponse({'status': 'unknown'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


# ════════════════════════════════════════════════════════════════════════
# PAYMENT STATUS HANDLERS
# ════════════════════════════════════════════════════════════════════════

def _handle_payment_success(payment, transaction_id=None):
    """Handle successful payment"""
    try:
        # Update payment
        payment.status = 'completed'
        if transaction_id:
            payment.external_transaction_id = transaction_id
        payment.save()
        
        logger.info(f"✅ Payment marked as COMPLETED: {payment.transaction_id}")
        
        # Grant book access
        if payment.book:
            try:
                payment.user.library.add(payment.book)
                logger.info(f"✅ Book access granted: {payment.user.id} -> {payment.book.id}")
            except Exception as e:
                logger.error(f"Error granting book access: {str(e)}")
        
        # Send confirmation email
        try:
            _send_confirmation_email(payment, transaction_id)
        except Exception as e:
            logger.warning(f"Error sending confirmation email: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}", exc_info=True)


def _handle_payment_failure(payment):
    """Handle failed payment"""
    try:
        payment.status = 'failed'
        payment.save()
        
        logger.info(f"❌ Payment marked as FAILED: {payment.transaction_id}")
        
        # Send failure email
        try:
            _send_failure_email(payment)
        except Exception as e:
            logger.warning(f"Error sending failure email: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}", exc_info=True)


# ════════════════════════════════════════════════════════════════════════
# SECURITY & EMAIL HELPERS
# ════════════════════════════════════════════════════════════════════════

def _generate_signature(data, secret):
    """Generate HMAC-SHA256 signature"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hmac.new(
        secret.encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()


def _verify_signature(provided, expected):
    """Verify signature using constant-time comparison"""
    return hmac.compare_digest(provided, expected)


def _send_confirmation_email(payment, transaction_id=None):
    """Send payment confirmation email"""
    subject = f'Payment Confirmed - Order {payment.transaction_id}'
    message = f"""
Dear {payment.user.first_name or 'User'},

Your payment of {payment.amount} {payment.currency} has been successfully processed.

Order ID: {payment.transaction_id}
Amount: {payment.amount} {payment.currency}
Payment Method: {payment.payment_method}
{f'Transaction ID: {transaction_id}' if transaction_id else ''}

Your book access has been activated.

Thank you for your purchase!

Best regards,
BNC Library Team
    """.strip()
    
    send_mail(
        subject,
        message,
        'noreply@bnc-library.com',
        [payment.user.email],
        fail_silently=True
    )
    logger.info(f"📧 Confirmation email sent: {payment.user.email}")


def _send_failure_email(payment):
    """Send payment failure email"""
    subject = f'Payment Failed - Order {payment.transaction_id}'
    message = f"""
Dear {payment.user.first_name or 'User'},

Unfortunately, your payment for order {payment.transaction_id} could not be processed.

Amount: {payment.amount} {payment.currency}

Please try again using a different payment method or contact support.

Best regards,
BNC Library Team
    """.strip()
    
    send_mail(
        subject,
        message,
        'noreply@bnc-library.com',
        [payment.user.email],
        fail_silently=True
    )
    logger.info(f"📧 Failure email sent: {payment.user.email}")


# ════════════════════════════════════════════════════════════════════════
# RETURN PAGES
# ════════════════════════════════════════════════════════════════════════

@login_required
def payment_callback(request):
    """User callback after payment (success or failure)"""
    order_id = request.GET.get('order_id')
    status = request.GET.get('status', 'unknown')
    
    context = {
        'order_id': order_id,
        'status': status,
        'message': 'Payment processed. Thank you!' if status == 'success' else 'Payment processing...'
    }
    
    return JsonResponse(context)
