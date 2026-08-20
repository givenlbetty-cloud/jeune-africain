"""
Intégration des passerelles de paiement.
Support: Stripe, Paypal, Airtel Money, M-Pesa, Orange Money RDC, Virement bancaire
"""

import requests
import json
import base64
import os
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from catalogue.models import Payment


class PaymentGateway:
    """Classe de base pour les passerelles de paiement"""
    
    def __init__(self, payment):
        self.payment = payment
    
    def initiate_payment(self):
        """Initialiser le paiement"""
        raise NotImplementedError
    
    def verify_payment(self):
        """Vérifier le statut du paiement"""
        raise NotImplementedError


class StripePaymentGateway(PaymentGateway):
    """Intégration Stripe"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_key = settings.STRIPE_API_KEY if hasattr(settings, 'STRIPE_API_KEY') else None
    
    def initiate_payment(self):
        """Créer une session de paiement Stripe"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'Stripe non configuré'
            }
        
        try:
            import stripe
            stripe.api_key = self.api_key
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': self.payment.currency.lower(),
                        'product_data': {
                            'name': self.payment.book.title,
                        },
                        'unit_amount': int(self.payment.amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.SITE_URL + f'/payment/success/{self.payment.id}/',
                cancel_url=settings.SITE_URL + f'/payment/cancel/{self.payment.id}/',
                metadata={
                    'payment_id': str(self.payment.id),
                    'user_id': str(self.payment.user.id),
                }
            )
            
            return {
                'success': True,
                'url': session.url,
                'session_id': session.id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class PayPalPaymentGateway(PaymentGateway):
    """Intégration PayPal"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.client_id = settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else None
        self.client_secret = settings.PAYPAL_CLIENT_SECRET if hasattr(settings, 'PAYPAL_CLIENT_SECRET') else None
        self.api_base = 'https://api-m.sandbox.paypal.com'  # Sandbox, à changer en prod
    
    def get_access_token(self):
        """Obtenir un token d'accès PayPal"""
        try:
            response = requests.post(
                f'{self.api_base}/v1/oauth2/token',
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials'}
            )
            return response.json()['access_token']
        except Exception as e:
            return None
    
    def initiate_payment(self):
        """Créer un ordre PayPal"""
        if not self.client_id or not self.client_secret:
            return {
                'success': False,
                'error': 'PayPal non configuré'
            }
        
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'error': 'Impossible d\'obtenir le token PayPal'}
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': self.payment.currency,
                        'value': str(self.payment.amount)
                    },
                    'description': f'Livre: {self.payment.book.title}'
                }],
                'application_context': {
                    'return_url': settings.SITE_URL + f'/payment/success/{self.payment.id}/',
                    'cancel_url': settings.SITE_URL + f'/payment/cancel/{self.payment.id}/',
                    'brand_name': 'BNC - Bibliothèque Numérique',
                    'locale': 'fr_FR',
                    'user_action': 'PAY_NOW'
                }
            }
            
            response = requests.post(
                f'{self.api_base}/v2/checkout/orders',
                headers=headers,
                json=data
            )
            
            order = response.json()
            
            # Sauvegarder l'order_id
            self.payment.external_transaction_id = order.get('id')
            self.payment.save()
            
            # Trouver l'URL d'approbation
            approve_link = next(
                (link['href'] for link in order.get('links', []) if link['rel'] == 'approve'),
                None
            )
            
            return {
                'success': True,
                'url': approve_link,
                'order_id': order.get('id')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class OrangeMoneyGateway(PaymentGateway):
    """Intégration Orange Money / Mobile Money"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_key = settings.ORANGE_MONEY_API_KEY if hasattr(settings, 'ORANGE_MONEY_API_KEY') else None
        self.api_base = 'https://api.orange.com'
    
    def initiate_payment(self):
        """Créer une transaction Orange Money"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'Orange Money non configuré'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Formater le numéro de téléphone utilisateur
            phone = self.payment.user.phone or ''
            
            data = {
                'amount': str(self.payment.amount),
                'currency': self.payment.currency,
                'orderRef': self.payment.transaction_id,
                'notificationUrl': settings.SITE_URL + '/payment/orange-webhook/',
                'returnUrl': settings.SITE_URL + f'/payment/success/{self.payment.id}/',
                'merchantUid': 'BNC_MERCHANT',
                'description': f'Achat: {self.payment.book.title}'
            }
            
            response = requests.post(
                f'{self.api_base}/orange-money/payment',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'redirect_url': result.get('paymentUrl'),
                    'transaction_id': result.get('transactionId')
                }
            else:
                return {
                    'success': False,
                    'error': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class BankTransferGateway(PaymentGateway):
    """Système de virement bancaire"""
    
    def initiate_payment(self):
        """Générer les détails de virement bancaire"""
        return {
            'success': True,
            'method': 'BANK_TRANSFER',
            'bank_details': {
                'beneficiary': 'Bibliothèque Numérique Continentale',
                'iban': 'SN14 BMCD 0000 0000 0000 0000 000',  # Exemple
                'bic': 'BMCDSN',
                'amount': self.payment.amount,
                'currency': self.payment.currency,
                'reference': self.payment.transaction_id,
                'message': f'Achat livre: {self.payment.book.title}'
            },
            'note': 'Veuillez effectuer le virement et fournir la preuve pour valider votre achat.'
        }


# ===== MONEROO (ALL-IN-ONE) =====
class MonerooPaymentGateway(PaymentGateway):
    """Intégration Moneroo (Mobile Money & Cartes)"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_key = (
            getattr(settings, 'MONEROO_API_KEY', '')
            or os.getenv('MONEROO_API_KEY', '')
            or getattr(settings, 'MONEROO_PUBLIC_KEY', '')
            or os.getenv('MONEROO_PUBLIC_KEY', '')
        )
        self.api_url = getattr(settings, 'MONEROO_API_URL', '') or os.getenv('MONEROO_API_URL', 'https://api.moneroo.io/v1')
        
    def initiate_payment(self):
        if not self.api_key:
            return {
                'success': False,
                'error': 'Moneroo non configuré (Clé API manquante)'
            }
            
        try:
            # Determine payment method for Moneroo
            method = 'mobile_money'
            if self.payment.payment_method.upper() in ['CARD', 'CREDIT_CARD', 'VISA', 'MASTERCARD']:
                method = 'card'
            
            # Use specific mobile money provider if set (mpesa, orange_money, airtel_money)
            # This forces Moneroo to use the specific method instead of the generic checkout
            provider = getattr(self.payment, 'mobile_money_provider', None)
            if provider and provider in ['mpesa', 'orange_money', 'airtel_money']:
                method = provider

            # Prepare customer data
            first_name = self.payment.user.first_name or 'Client'
            last_name = self.payment.user.last_name or 'BNC'
            
            # Clean phone number (remove +, spaces, etc)
            raw_phone = getattr(self.payment, 'phone_number', '') or ''
            clean_phone = ''.join(filter(str.isdigit, str(raw_phone)))
            
            # Force DRC format (243) for all numbers
            if clean_phone:
                if clean_phone.startswith('243'):
                    pass # Already has prefix
                elif clean_phone.startswith('0'):
                    clean_phone = '243' + clean_phone.lstrip('0')
                else:
                    clean_phone = '243' + clean_phone
            
            payload = {
                'amount': float(self.payment.amount),
                'currency': getattr(settings, 'MONEROO_CURRENCY', self.payment.currency),
                'customer': {
                    'email': self.payment.user.email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': int(clean_phone) if clean_phone else 0,
                    'country': 'CD'
                },
                # Top-level fields for checkout pre-fill compatibility
                'customer_phone': clean_phone if clean_phone else "",
                'customer_email': self.payment.user.email,
                'customer_first_name': first_name,
                'customer_last_name': last_name,
                'country': 'CD',
                
                'order_id': self.payment.transaction_id,
                'order_reference': self.payment.transaction_id,
                'description': f'BNC Library - {self.payment.book.title}',
                'payment_method': method,
                'return_url': settings.SITE_URL + '/payment/callback/',
                'callback_url': settings.SITE_URL + '/api/payments/moneroo-callback/',
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                f'{self.api_url}/payments/initialize',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Moneroo response status: {response.status_code}")
            logger.debug(f"Moneroo response body: {response.text}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Check for 'payment_url' OR 'checkout_url'
                payment_url = (
                    data.get('data', {}).get('payment_url') or 
                    data.get('data', {}).get('checkout_url') or 
                    data.get('payment_url') or
                    data.get('checkout_url')
                )
                
                if payment_url:
                    return {
                        'success': True,
                        'url': payment_url
                    }
            
            return {
                'success': False,
                'error': f"Erreur Moneroo ({response.status_code}): {response.text}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def get_payment_gateway(payment):
    """Retourner la passerelle de paiement appropriée"""
    method = payment.payment_method.upper()
    
    # Check if we should use Moneroo for everything (except Bank Transfer)
    use_moneroo = getattr(settings, 'USE_MONEROO_FOR_ALL', False) or os.getenv('USE_MONEROO_FOR_ALL', 'True') == 'True'
    
    if use_moneroo and method not in ['BANK_TRANSFER', 'CASH']:
        return MonerooPaymentGateway(payment)
    
    gateways = {
        'CREDIT_CARD': StripePaymentGateway,
        'PAYPAL': PayPalPaymentGateway,
        'AIRTEL_MONEY': AirtelMoneyGateway,
        'MPESA': MPesaGateway,
        'ORANGE_MONEY': OrangeMoneyRDCGateway,
        'MOBILE_MONEY': MonerooPaymentGateway,
        'MONEROO': MonerooPaymentGateway,
        'BANK_TRANSFER': BankTransferGateway,
        'CASH': BankTransferGateway,
    }
    
    gateway_class = gateways.get(method, BankTransferGateway)
    return gateway_class(payment)


# ===== AIRTEL MONEY =====
class AirtelMoneyGateway(PaymentGateway):
    """Intégration Airtel Money (Ouganda, Burundi, RDC)"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_url = getattr(settings, 'AIRTEL_MONEY_API_URL', 'https://openapiuat.airtel.africa')
        self.client_id = getattr(settings, 'AIRTEL_MONEY_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'AIRTEL_MONEY_CLIENT_SECRET', '')
        self.business_code = getattr(settings, 'AIRTEL_MONEY_BUSINESS_CODE', '')
        self.timeout = 30
    
    def get_access_token(self):
        """Obtenir un token OAuth2"""
        try:
            url = f"{self.api_url}/auth/oauth2/token"
            auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            payload = {'grant_type': 'client_credentials'}
            
            response = requests.post(url, headers=headers, data=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"Airtel Money Token Error: {str(e)}")
            return None
    
    def initiate_payment(self):
        """Initier un paiement Airtel Money"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'error': 'Authentication failed'}
            
            url = f"{self.api_url}/merchant/v2/payments/"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            phone = str(self.payment.phone_number).replace('+', '')
            
            payload = {
                'reference': str(self.payment.id),
                'subscriber': {'msisdn': phone},
                'transaction': {
                    'amount': str(self.payment.amount),
                    'currency': self.payment.currency,
                    'id': str(self.payment.id)
                },
                'merchant': {
                    'businesscode': self.business_code,
                    'name': 'BNC Library'
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                transaction_id = data.get('data', {}).get('transaction', {}).get('id')
                
                self.payment.merchant_request_id = str(self.payment.id)
                self.payment.checkout_request_id = transaction_id
                self.payment.mobile_money_provider = 'airtel'
                self.payment.webhook_data = data
                self.payment.save()
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'message': 'Payment initiated'
                }
            
            return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self):
        """Vérifier le statut du paiement"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'status': 'unknown'}
            
            url = f"{self.api_url}/standard/v2/payments/status"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            payload = {'reference': str(self.payment.merchant_request_id)}
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('data', {}).get('transaction', {}).get('status', 'unknown')
                
                return {
                    'success': status == 'SUCCESS',
                    'status': status,
                    'data': data
                }
            
            return {'success': False, 'status': 'unknown'}
        except Exception as e:
            return {'success': False, 'status': 'unknown', 'error': str(e)}


# ===== M-PESA =====
class MPesaGateway(PaymentGateway):
    """Intégration M-Pesa (Safaricom Kenya)"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_url = getattr(settings, 'MPESA_API_URL', 'https://sandbox.safaricom.co.ke')
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.business_shortcode = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.callback_url = getattr(settings, 'MPESA_CALLBACK_URL', f"{settings.SITE_URL}/api/payments/webhook/mpesa/")
        self.timeout = 30
    
    def get_access_token(self):
        """Obtenir un token OAuth2"""
        try:
            url = f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(url, auth=(self.consumer_key, self.consumer_secret), timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"M-Pesa Token Error: {str(e)}")
            return None
    
    def get_timestamp(self):
        """Générer timestamp M-Pesa"""
        return datetime.now().strftime('%Y%m%d%H%M%S')
    
    def initiate_payment(self):
        """Initier un STK Push M-Pesa"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'error': 'Authentication failed'}
            
            url = f"{self.api_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            timestamp = self.get_timestamp()
            password = base64.b64encode(
                f"{self.business_shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            phone = str(self.payment.phone_number).replace('+', '').replace(' ', '')
            if not phone.startswith('254'):
                phone = '254' + phone.lstrip('0')[-9:]
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(self.payment.amount),
                'PartyA': phone,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone,
                'CallBackURL': self.callback_url,
                'AccountReference': str(self.payment.id),
                'TransactionDesc': 'Book Purchase'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('ResponseCode') == '0':
                    checkout_request_id = data.get('CheckoutRequestID')
                    
                    self.payment.merchant_request_id = data.get('RequestID')
                    self.payment.checkout_request_id = checkout_request_id
                    self.payment.mobile_money_provider = 'mpesa'
                    self.payment.webhook_data = data
                    self.payment.save()
                    
                    return {
                        'success': True,
                        'checkout_request_id': checkout_request_id,
                        'message': 'STK push sent'
                    }
            
            return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self):
        """Vérifier le statut M-Pesa"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'status': 'unknown'}
            
            url = f"{self.api_url}/mpesa/stkpushquery/v1/query"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            timestamp = self.get_timestamp()
            password = base64.b64encode(
                f"{self.business_shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': self.payment.checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                result_code = data.get('ResultCode')
                
                return {
                    'success': result_code == '0',
                    'status': 'completed' if result_code == '0' else 'failed',
                    'data': data
                }
            
            return {'success': False, 'status': 'unknown'}
        except Exception as e:
            return {'success': False, 'status': 'unknown', 'error': str(e)}


# ===== ORANGE MONEY RDC =====
class OrangeMoneyRDCGateway(PaymentGateway):
    """Intégration Orange Money RDC"""
    
    def __init__(self, payment):
        super().__init__(payment)
        self.api_url = getattr(settings, 'ORANGE_MONEY_API_URL', 'https://api.orange.com/orange-money-webservices/dev')
        self.client_id = getattr(settings, 'ORANGE_MONEY_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'ORANGE_MONEY_CLIENT_SECRET', '')
        self.merchant_id = getattr(settings, 'ORANGE_MONEY_MERCHANT_ID', '')
        self.merchant_key = getattr(settings, 'ORANGE_MONEY_MERCHANT_KEY', '')
        self.timeout = 30
    
    def get_access_token(self):
        """Obtenir un token OAuth2"""
        try:
            url = f"{self.api_url}/login"
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"Orange Money Token Error: {str(e)}")
            return None
    
    def initiate_payment(self):
        """Initier un paiement Orange Money"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'error': 'Authentication failed'}
            
            url = f"{self.api_url}/transact"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            phone = str(self.payment.phone_number).replace('+', '').replace(' ', '')
            if not phone.startswith('243'):
                phone = '243' + phone.lstrip('0')
            
            payload = {
                'merchant': self.merchant_id,
                'merchant_key': self.merchant_key,
                'reference': str(self.payment.id),
                'notif_url': f"{settings.SITE_URL}/api/payments/webhook/orange/",
                'return_url': f"{settings.SITE_URL}/payment/success/",
                'cancel_url': f"{settings.SITE_URL}/payment/cancel/",
                'amount': str(self.payment.amount),
                'currency': self.payment.currency,
                'lang': 'fr',
                'customer': {
                    'msisdn': phone,
                    'email': getattr(self.payment.user, 'email', ''),
                    'first_name': 'Customer',
                    'last_name': 'BNC'
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('status') == 'SUCCESS':
                    transaction_id = data.get('transaction_id')
                    
                    self.payment.merchant_request_id = str(self.payment.id)
                    self.payment.checkout_request_id = transaction_id
                    self.payment.mobile_money_provider = 'orange'
                    self.payment.webhook_data = data
                    self.payment.save()
                    
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'redirect_url': data.get('redirect_url'),
                        'message': 'Payment initiated'
                    }
            
            return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self):
        """Vérifier le statut du paiement"""
        try:
            token = self.get_access_token()
            if not token:
                return {'success': False, 'status': 'unknown'}
            
            url = f"{self.api_url}/checkTransaction"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'merchant': self.merchant_id,
                'transaction_id': self.payment.checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                return {
                    'success': status == 'SUCCESS',
                    'status': status,
                    'data': data
                }
            
            return {'success': False, 'status': 'unknown'}
        except Exception as e:
            return {'success': False, 'status': 'unknown', 'error': str(e)}
