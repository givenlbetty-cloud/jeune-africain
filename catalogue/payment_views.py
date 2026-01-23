"""
Vues pour la gestion des paiements avec intégration passerelles.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json

from catalogue.models import Payment, Book
from catalogue.payment_gateways import get_payment_gateway


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def initiate_payment_view(request, book_id):
    """Initier un paiement pour un livre"""
    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    # Vérifier que l'utilisateur n'a pas déjà acheté ce livre
    existing = Payment.objects.filter(
        user=request.user,
        book=book,
        status='COMPLETED'
    ).exists()
    
    if existing:
        return JsonResponse({
            'success': False,
            'error': 'Vous avez déjà acheté ce livre.'
        }, status=400)
    
    # Récupérer la méthode de paiement
    payment_method = request.POST.get('payment_method', 'CREDIT_CARD').upper()
    
    # Créer le paiement
    import uuid
    transaction_id = f"BNC_{uuid.uuid4().hex[:16].upper()}"
    final_price = book.get_final_price() if hasattr(book, 'get_final_price') else float(book.price)
    
    payment = Payment.objects.create(
        user=request.user,
        book=book,
        amount=final_price,
        currency='CDF',
        transaction_id=transaction_id,
        payment_method=payment_method,
        status='PENDING'
    )
    
    # Initialiser la passerelle de paiement
    gateway = get_payment_gateway(payment)
    result = gateway.initiate_payment()
    
    if result['success']:
        if result.get('url'):
            # Redirection vers URL externe (Stripe, PayPal)
            return JsonResponse({
                'success': True,
                'redirect_url': result['url']
            })
        else:
            # Infos de paiement (virement bancaire, etc.)
            return render(request, 'payment/checkout.html', {
                'payment': payment,
                'gateway_result': result
            })
    else:
        payment.status = 'FAILED'
        payment.save()
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Erreur lors de l\'initialisation du paiement')
        }, status=400)


@login_required(login_url='users:login')
def payment_success_view(request, payment_id):
    """Confirmation de succès du paiement"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Marquer comme complété
    payment.status = 'COMPLETED'
    payment.save()
    
    messages.success(request, f'Paiement confirmé! Vous pouvez maintenant lire "{payment.book.title}".')
    return redirect('catalogue:book_detail', book_id=payment.book.id)


@login_required(login_url='users:login')
def payment_cancel_view(request, payment_id):
    """Annulation du paiement"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Marquer comme échoué
    payment.status = 'FAILED'
    payment.save()
    
    messages.warning(request, 'Paiement annulé.')
    return redirect('catalogue:book_detail', book_id=payment.book.id)


@login_required(login_url='users:login')
def payment_history_view(request):
    """Historique des paiements de l'utilisateur"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Statistiques
    total_spent = sum(p.amount for p in payments.filter(status='COMPLETED'))
    books_owned = payments.filter(status='COMPLETED').values('book').distinct().count()
    
    context = {
        'payments': payments,
        'total_spent': total_spent,
        'books_owned': books_owned,
    }
    
    return render(request, 'payment/history.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_orange(request):
    """Webhook pour Orange Money"""
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transactionId')
        status = data.get('status')  # SUCCESS, FAILED, CANCELLED
        
        # Trouver le paiement
        payment = Payment.objects.get(external_transaction_id=transaction_id)
        
        if status == 'SUCCESS':
            payment.status = 'COMPLETED'
        elif status in ['FAILED', 'CANCELLED']:
            payment.status = 'FAILED'
        
        payment.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook_stripe(request):
    """Webhook pour Stripe"""
    try:
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_API_KEY
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            metadata = payment_intent.get('metadata', {})
            payment_id = metadata.get('payment_id')
            
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'COMPLETED'
            payment.external_transaction_id = payment_intent['id']
            payment.save()
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            metadata = payment_intent.get('metadata', {})
            payment_id = metadata.get('payment_id')
            
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'FAILED'
            payment.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ===== MOBILE MONEY VIEWS (Airtel, M-Pesa, Orange) =====

@login_required
@require_http_methods(["POST"])
def initiate_mobile_money_payment_view(request, book_id):
    """
    Initier un paiement Mobile Money
    
    POST /api/payments/mobile-money/{book_id}/
    Payload: {
        "provider": "airtel|mpesa|orange",
        "phone_number": "+256xxxxxxxxx"
    }
    """
    from django.utils import timezone
    import uuid
    from catalogue.models import ReadingSession
    
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        provider = data.get('provider', '').lower()
        phone_number = data.get('phone_number', '')
        
        # Valider
        if not provider or not phone_number:
            return JsonResponse({'success': False, 'error': 'provider et phone_number requis'}, status=400)
        
        # Vérifier accès existant
        existing = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        
        if existing:
            return JsonResponse({'success': False, 'error': 'Vous avez déjà accès'}, status=400)
        
        # Mapper provider à payment_method
        provider_map = {
            'airtel': 'airtel_money',
            'mpesa': 'mpesa',
            'orange': 'orange_money',
        }
        
        payment_method = provider_map.get(provider)
        if not payment_method:
            return JsonResponse({'success': False, 'error': 'Provider inconnu'}, status=400)
        
        # Créer paiement
        payment, created = Payment.objects.get_or_create(
            user=request.user,
            book=book,
            status='PENDING',
            defaults={
                'amount': book.price or 0,
                'currency': 'CDF',
                'payment_method': payment_method,
                'transaction_id': str(uuid.uuid4()),
                'phone_number': phone_number,
                'mobile_money_provider': provider,
            }
        )
        
        if not created:
            payment.payment_method = payment_method
            payment.phone_number = phone_number
            payment.mobile_money_provider = provider
            payment.save()
        
        # Obtenir gateway et initier
        gateway = get_payment_gateway(payment)
        result = gateway.initiate_payment()
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'payment_id': str(payment.id),
                'transaction_id': result.get('transaction_id'),
                'checkout_request_id': result.get('checkout_request_id'),
                'message': 'Paiement initié',
                'redirect_url': result.get('redirect_url')
            })
        else:
            payment.delete()
            return JsonResponse({'success': False, 'error': result.get('error')}, status=400)
    
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Livre non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def check_mobile_money_status_view(request, payment_id):
    """
    Vérifier le statut d'un paiement Mobile Money
    
    GET /api/payments/mobile-money/{payment_id}/status/
    """
    from django.utils import timezone
    from catalogue.models import ReadingSession
    
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        if payment.status == 'COMPLETED':
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'message': 'Paiement confirmé'
            })
        
        # Vérifier auprès de la gateway
        gateway = get_payment_gateway(payment)
        result = gateway.verify_payment()
        
        if result.get('success'):
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            payment.save()
            
            # Accorder l'accès
            ReadingSession.objects.get_or_create(
                user=request.user,
                book=payment.book,
                defaults={
                    'start_time': timezone.now(),
                    'duration_minutes': 0,
                    'pages_read': 0,
                    'current_page': 0,
                    'is_completed': False,
                }
            )
            
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'message': 'Accès accordé',
                'redirect_url': f"/books/book/{payment.book.id}/"
            })
        else:
            return JsonResponse({
                'success': False,
                'status': result.get('status', 'pending'),
                'message': 'En attente...'
            })
    
    except Payment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Paiement non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mpesa_webhook(request):
    """Webhook M-Pesa"""
    from django.utils import timezone
    from catalogue.models import ReadingSession
    
    try:
        data = json.loads(request.body)
        result = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = result.get('CheckoutRequestID')
        result_code = result.get('ResultCode')
        
        if not checkout_request_id:
            return JsonResponse({'ResultCode': '1', 'ResultDesc': 'Manquant'})
        
        payment = Payment.objects.filter(
            checkout_request_id=checkout_request_id,
            mobile_money_provider='mpesa'
        ).first()
        
        if not payment:
            return JsonResponse({'ResultCode': '1', 'ResultDesc': 'Non trouvé'})
        
        if result_code == 0:
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            
            callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
            for item in callback_metadata:
                if item.get('Name') == 'Amount':
                    payment.amount = item.get('Value')
                elif item.get('Name') == 'TransactionId':
                    payment.external_transaction_id = item.get('Value')
            
            payment.webhook_data = result
            payment.save()
            
            ReadingSession.objects.get_or_create(
                user=payment.user,
                book=payment.book,
                defaults={
                    'start_time': timezone.now(),
                    'duration_minutes': 0,
                    'pages_read': 0,
                    'current_page': 0,
                    'is_completed': False,
                }
            )
        else:
            payment.status = 'FAILED'
            payment.webhook_data = result
            payment.save()
        
        return JsonResponse({'ResultCode': '0', 'ResultDesc': 'OK'})
    except Exception as e:
        return JsonResponse({'ResultCode': '1', 'ResultDesc': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def airtel_webhook(request):
    """Webhook Airtel Money"""
    from django.utils import timezone
    from catalogue.models import ReadingSession
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('data', {}).get('transaction', {}).get('id')
        status = data.get('data', {}).get('transaction', {}).get('status')
        
        if not transaction_id:
            return JsonResponse({'status': 'error'})
        
        payment = Payment.objects.filter(
            checkout_request_id=transaction_id,
            mobile_money_provider='airtel'
        ).first()
        
        if not payment:
            return JsonResponse({'status': 'error'})
        
        if status == 'SUCCESS':
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            payment.external_transaction_id = transaction_id
            
            ReadingSession.objects.get_or_create(
                user=payment.user,
                book=payment.book,
                defaults={
                    'start_time': timezone.now(),
                    'duration_minutes': 0,
                    'pages_read': 0,
                    'current_page': 0,
                    'is_completed': False,
                }
            )
        else:
            payment.status = 'FAILED'
        
        payment.webhook_data = data
        payment.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error'})


@csrf_exempt
@require_http_methods(["POST"])
def orange_webhook(request):
    """Webhook Orange Money RDC"""
    from django.utils import timezone
    from catalogue.models import ReadingSession
    from django.db.models import Q
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        reference = data.get('reference')
        
        if not transaction_id:
            return JsonResponse({'status': 'error'})
        
        payment = Payment.objects.filter(
            Q(checkout_request_id=transaction_id) | Q(merchant_request_id=reference),
            mobile_money_provider='orange'
        ).first()
        
        if not payment:
            return JsonResponse({'status': 'error'})
        
        if status == 'SUCCESS':
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            payment.external_transaction_id = transaction_id
            
            ReadingSession.objects.get_or_create(
                user=payment.user,
                book=payment.book,
                defaults={
                    'start_time': timezone.now(),
                    'duration_minutes': 0,
                    'pages_read': 0,
                    'current_page': 0,
                    'is_completed': False,
                }
            )
        else:
            payment.status = 'FAILED'
        
        payment.webhook_data = data
        payment.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error'})
