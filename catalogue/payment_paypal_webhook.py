"""
PayPal Webhook Handler for BNC Digital Library
Processes payment confirmations from PayPal IPN (Instant Payment Notifications)
"""

import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings

logger = logging.getLogger(__name__)

# Import models - adjust based on your actual models
try:
    from catalogue.models import Order, Payment
except ImportError:
    Order = None
    Payment = None


@csrf_exempt
@require_http_methods(['POST'])
def paypal_webhook(request):
    """
    Handle PayPal Instant Payment Notifications (IPN)
    
    This endpoint is called by PayPal when a payment status changes.
    
    Endpoint: POST /api/webhooks/paypal/
    
    PayPal Event Types:
    - CHECKOUT.ORDER.COMPLETED: Payment completed
    - CHECKOUT.ORDER.PAYMENT_APPROVED: Payment approved (before completion)
    - PAYMENT.SALE.COMPLETED: Sale completed (older API)
    - PAYMENT.SALE.DENIED: Sale denied
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        event_type = data.get('event_type', '')
        
        logger.info(f"PayPal webhook received: {event_type}")
        logger.debug(f"Payload: {data}")
        
        # Route based on event type
        if event_type == 'CHECKOUT.ORDER.COMPLETED':
            _process_order_completed(data)
        
        elif event_type == 'CHECKOUT.ORDER.PAYMENT_APPROVED':
            _process_payment_approved(data)
        
        elif event_type == 'PAYMENT.SALE.COMPLETED':
            _process_sale_completed(data)
        
        elif event_type == 'PAYMENT.SALE.DENIED':
            _process_payment_failed(data)
        
        else:
            logger.warning(f"Unhandled event type: {event_type}")
        
        # Return success to PayPal
        return JsonResponse({'status': 'success'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def _process_order_completed(data):
    """
    Process completed order webhook (newer PayPal API)
    
    Triggered when:
    - Customer completes checkout and payment is approved
    """
    try:
        resource = data.get('resource', {})
        payment_source = resource.get('payment_source', {})
        
        # Extract order ID
        order_id = resource.get('custom_id') or resource.get('id')
        
        if not order_id:
            logger.error("No order ID found in webhook")
            return
        
        # Find order
        if not Order:
            logger.error("Order model not imported")
            return
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order not found: {order_id}")
            return
        except ValueError:
            logger.error(f"Invalid order ID: {order_id}")
            return
        
        # Extract payment details
        amount = Decimal(resource.get('purchase_units', [{}])[0]
                        .get('amount', {})
                        .get('value', 0))
        
        currency = resource.get('purchase_units', [{}])[0] \
                   .get('amount', {}) \
                   .get('currency_code', 'USD')
        
        status = resource.get('status', 'UNKNOWN')
        payment_id = resource.get('id')
        
        logger.info(f"Processing completed order: {order_id}, Status: {status}")
        
        if status == 'APPROVED' or status == 'COMPLETED':
            _process_payment_success(order, amount, currency, payment_id, 'paypal')
        elif status == 'PAYER_ACTION_REQUIRED':
            _process_payment_pending(order)
        else:
            _process_payment_failed(data, order)
    
    except Exception as e:
        logger.error(f"Error processing order completed: {str(e)}", exc_info=True)


def _process_sale_completed(data):
    """
    Process sale completed webhook (older PayPal API)
    
    Triggered when:
    - Sale/transaction is completed
    """
    try:
        resource = data.get('resource', {})
        invoice_number = resource.get('invoice_number') or resource.get('custom')
        
        if not invoice_number:
            logger.warning("No invoice number in sale completed webhook")
            return
        
        if not Order:
            logger.error("Order model not imported")
            return
        
        try:
            order = Order.objects.get(id=invoice_number)
        except Order.DoesNotExist:
            logger.warning(f"Order not found for invoice: {invoice_number}")
            return
        
        amount = Decimal(resource.get('amount', 0))
        currency = resource.get('currency_code', 'USD')
        transaction_id = resource.get('id')
        
        _process_payment_success(order, amount, currency, transaction_id, 'paypal')
    
    except Exception as e:
        logger.error(f"Error processing sale completed: {str(e)}", exc_info=True)


def _process_payment_approved(data):
    """Process payment approved webhook"""
    try:
        resource = data.get('resource', {})
        order_id = resource.get('custom_id') or resource.get('id')
        
        logger.info(f"Payment approved: {order_id}")
        logger.debug(f"Resource: {resource}")
    
    except Exception as e:
        logger.error(f"Error processing payment approved: {str(e)}")


def _process_payment_failed(data, order=None):
    """
    Process failed payment webhook
    """
    try:
        resource = data.get('resource', {})
        payment_id = resource.get('id')
        
        logger.warning(f"Payment failed: {payment_id}")
        
        if order:
            order.payment_status = 'FAILED'
            order.save()
            
            logger.info(f"Order marked as FAILED: {order.id}")
            
            # Send failure email
            _send_payment_failure_email(order)
    
    except Exception as e:
        logger.error(f"Error processing payment failure: {str(e)}", exc_info=True)


def _process_payment_success(order, amount, currency, payment_id, payment_method):
    """
    Process successful payment
    
    Args:
        order: Order object
        amount: Payment amount
        currency: Currency code
        payment_id: PayPal payment/transaction ID
        payment_method: Payment method (e.g., 'paypal')
    """
    try:
        if not Payment:
            logger.error("Payment model not imported")
            return
        
        # Create or update payment record
        payment, created = Payment.objects.update_or_create(
            order=order,
            defaults={
                'amount': amount,
                'currency': currency,
                'status': 'COMPLETED',
                'transaction_id': payment_id,
                'payment_method': payment_method
            }
        )
        
        # Update order status
        order.payment_status = 'COMPLETED'
        order.save()
        
        logger.info(f"Payment processed successfully: Order={order.id}, PaymentID={payment_id}")
        
        # Grant access to book
        if hasattr(order, 'book') and hasattr(order.user, 'access_books'):
            order.user.access_books.add(order.book)
            logger.info(f"Book access granted: User={order.user.id}, Book={order.book.id}")
        
        # Send confirmation email
        _send_payment_confirmation_email(order, payment_id)
    
    except Exception as e:
        logger.error(f"Error processing payment success: {str(e)}", exc_info=True)


def _process_payment_pending(order):
    """
    Process pending payment (awaiting user action)
    """
    try:
        order.payment_status = 'PENDING'
        order.save()
        
        logger.info(f"Payment pending (user action required): {order.id}")
    
    except Exception as e:
        logger.error(f"Error processing pending payment: {str(e)}")


def _send_payment_confirmation_email(order, transaction_id):
    """
    Send payment confirmation email to customer
    
    Args:
        order: Order object
        transaction_id: PayPal transaction ID
    """
    try:
        user = order.user
        
        # Email context
        context = {
            'order': order,
            'user': user,
            'transaction_id': transaction_id,
            'amount': order.amount,
            'currency': getattr(order, 'currency', 'USD'),
            'payment_method': 'PayPal',
        }
        
        # Render email template
        try:
            subject = f"Payment Confirmation - Order #{order.id}"
            html_message = render_to_string(
                'emails/payment_confirmation.html',
                context
            )
            text_message = f"Your payment of {order.amount} has been received. Transaction ID: {transaction_id}"
        except Exception:
            # Fallback if template doesn't exist
            subject = f"Payment Confirmation - Order #{order.id}"
            html_message = None
            text_message = f"Your payment of {order.amount} has been received. Transaction ID: {transaction_id}"
        
        # Send email
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message if html_message else None,
            fail_silently=False
        )
        
        logger.info(f"Confirmation email sent: {user.email}")
    
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}", exc_info=True)


def _send_payment_failure_email(order):
    """
    Send payment failure email to customer
    
    Args:
        order: Order object
    """
    try:
        user = order.user
        
        subject = f"Payment Failed - Order #{order.id}"
        message = f"""
Your payment for order #{order.id} has failed.

Please try again using another payment method.

If the problem persists, please contact support.
        """.strip()
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
        logger.info(f"Failure email sent: {user.email}")
    
    except Exception as e:
        logger.error(f"Error sending failure email: {str(e)}", exc_info=True)
