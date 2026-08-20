"""
Donation views for BNC RDC
Anonymous donations via Moneroo + informational Mobile Money numbers from admin.
"""

import uuid
import json
import logging
import requests
from decimal import Decimal

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from catalogue.models import Donateur, MerchantPaymentAccount

logger = logging.getLogger(__name__)

MONEROO_API_KEY = (
    getattr(settings, 'MONEROO_API_KEY', '')
    or getattr(settings, 'MONEROO_PUBLIC_KEY', '')
    or os.getenv('MONEROO_PUBLIC_KEY', '')
    or os.getenv('MONEROO_API_KEY', '')
)
MONEROO_API_URL = getattr(settings, 'MONEROO_API_URL', '') or os.getenv('MONEROO_API_URL', 'https://api.moneroo.io/v1')


@require_http_methods(["GET", "POST"])
def donation_view(request):
    """
    GET: Affiche le formulaire de don (anonyme, pas de login requis).
    POST: Crée un Donateur + redirige vers Moneroo pour le paiement.
    """
    # Récupérer les comptes Mobile Money actifs pour affichage informatif
    merchant_accounts = MerchantPaymentAccount.objects.filter(
        is_active=True,
        payment_method__in=['mpesa', 'airtel_money', 'orange_money']
    ).order_by('payment_method')

    if request.method == 'GET':
        context = {
            'merchant_accounts': merchant_accounts,
        }
        return render(request, 'donation/donate.html', context)

    # POST: traiter le formulaire
    nom = (request.POST.get('nom') or 'Anonyme').strip()[:200]
    contact = (request.POST.get('contact') or '').strip()[:200]
    message = (request.POST.get('message') or '').strip()[:300]
    montant_str = request.POST.get('montant', '').strip()

    # Validation du montant
    try:
        montant = Decimal(montant_str)
        if montant <= 0:
            raise ValueError
    except (ValueError, TypeError):
        context = {
            'merchant_accounts': merchant_accounts,
            'error': 'Veuillez entrer un montant valide.',
            'form_data': {'nom': nom, 'contact': contact, 'message': message, 'montant': montant_str},
        }
        return render(request, 'donation/donate.html', context)

    # Créer le donateur
    transaction_ref = f"DON_{uuid.uuid4().hex[:16].upper()}"
    donateur = Donateur.objects.create(
        nom=nom,
        contact=contact,
        message=message,
        montant=montant,
        transaction_id=transaction_ref,
        status='pending',
        is_visible=True,
    )

    # Appeler Moneroo pour initier le paiement
    site_url = getattr(settings, 'SITE_URL', request.build_absolute_uri('/'))
    payload = {
        'amount': float(montant),
        'currency': 'CDF',
        'customer': {
            'email': contact if '@' in contact else 'donateur@bnc-rdc.com',
            'first_name': nom.split()[0] if nom.split() else 'Donateur',
            'last_name': nom.split()[-1] if len(nom.split()) > 1 else 'BNC',
            'phone': contact if '@' not in contact else '',
        },
        'description': f'Don BNC - {nom}',
        'return_url': f'{site_url.rstrip("/")}/donation/merci/{donateur.pk}/',
        'callback_url': f'{site_url.rstrip("/")}/api/payments/donation-webhook/',
        'metadata': {
            'donation_id': str(donateur.pk),
            'type': 'donation',
        },
    }

    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MONEROO_API_KEY}',
        }
        response = requests.post(
            f'{MONEROO_API_URL}/payments/initialize',
            json=payload,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        payment_url = (
            data.get('data', {}).get('checkout_url')
            or data.get('data', {}).get('payment_url')
            or data.get('checkout_url')
            or data.get('payment_url')
        )
        if not payment_url:
            logger.error(f"Moneroo donation: no payment/checkout URL in response: {data}")
            donateur.status = 'failed'
            donateur.save()
            context = {
                'merchant_accounts': merchant_accounts,
                'error': 'Erreur de la passerelle de paiement. Veuillez réessayer.',
                'form_data': {'nom': nom, 'contact': contact, 'message': message, 'montant': montant_str},
            }
            return render(request, 'donation/donate.html', context)

        logger.info(f"Donation payment initialized: {transaction_ref}")
        return redirect(payment_url)

    except requests.exceptions.RequestException as e:
        logger.error(f"Moneroo donation API error: {e}")
        donateur.status = 'failed'
        donateur.save()
        context = {
            'merchant_accounts': merchant_accounts,
            'error': 'Erreur de connexion au service de paiement. Veuillez réessayer.',
            'form_data': {'nom': nom, 'contact': contact, 'message': message, 'montant': montant_str},
        }
        return render(request, 'donation/donate.html', context)


@require_http_methods(["GET"])
def donation_thank_you(request, donation_id):
    """Page de remerciement après don."""
    try:
        donateur = Donateur.objects.get(pk=donation_id)
    except Donateur.DoesNotExist:
        donateur = None
    return render(request, 'donation/merci.html', {'donateur': donateur})


@csrf_exempt
@require_http_methods(["POST"])
def donation_webhook(request):
    """
    Webhook Moneroo pour les dons.
    POST /api/payments/donation-webhook/
    """
    try:
        data = json.loads(request.body)
        logger.info(f"Donation webhook received: {data.get('event')}")

        payload = data.get('data', {})
        metadata = payload.get('metadata', {})
        donation_id = metadata.get('donation_id')
        status = (payload.get('status') or '').lower()

        if not donation_id:
            logger.error("Donation webhook: missing donation_id in metadata")
            return JsonResponse({'error': 'Missing donation_id'}, status=400)

        try:
            donateur = Donateur.objects.get(pk=donation_id)
        except Donateur.DoesNotExist:
            logger.error(f"Donation webhook: donateur not found: {donation_id}")
            return JsonResponse({'error': 'Donateur not found'}, status=404)

        if status == 'completed':
            donateur.status = 'completed'
            donateur.save()
            logger.info(f"Donation completed: {donateur.transaction_id}")
        elif status == 'failed':
            donateur.status = 'failed'
            donateur.save()
            logger.warning(f"Donation failed: {donateur.transaction_id}")
        else:
            logger.info(f"Donation status update: {status} for {donateur.transaction_id}")

        return JsonResponse({'status': 'ok'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Donation webhook error: {e}", exc_info=True)
        return JsonResponse({'error': 'Server error'}, status=500)
