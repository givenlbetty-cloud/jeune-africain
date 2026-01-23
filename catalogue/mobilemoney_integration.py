"""
Intégration Flutterwave pour Mobile Money
Supporte tous les réseaux RDC: Airtel, Orange, Vodacom, Moov
"""

import requests
import json
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class FlutterwavePayment:
    """Classe pour gérer les paiements Flutterwave"""
    
    BASE_URL = "https://api.flutterwave.com/v3"
    
    # Réseaux Mobile Money supportés en RDC
    NETWORKS_RDC = {
        'airtel': {
            'name': 'Airtel Money',
            'code': 'airtel',
            'icon': '📱',
        },
        'orange': {
            'name': 'Orange Money',
            'code': 'orange',
            'icon': '🟠',
        },
        'vodacom': {
            'name': 'Vodacom M-Pesa',
            'code': 'vodacom',
            'icon': '📲',
        },
        'moov': {
            'name': 'Moov Money',
            'code': 'moov',
            'icon': '💳',
        },
    }
    
    def __init__(self):
        """Initialiser avec les clés Flutterwave"""
        self.secret_key = settings.FLUTTERWAVE_SECRET_KEY
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        
        if not self.secret_key or not self.public_key:
            logger.error("❌ Flutterwave keys not configured in settings")
    
    def initiate_payment(self, user, book, amount, phone, network):
        """
        Initier un paiement Mobile Money
        
        Args:
            user: Utilisateur
            book: Livre à acheter
            amount: Montant en CDF
            phone: Numéro de téléphone
            network: Réseau (airtel/orange/vodacom/moov)
        
        Returns:
            dict: Réponse de l'API
        """
        try:
            # Valider les données
            if network not in self.NETWORKS_RDC:
                return {
                    'success': False,
                    'error': f'Réseau non supporté: {network}'
                }
            
            # Préparer la requête
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'tx_ref': f"BNC-{user.id}-{book.id}-{int(amount)}",
                'amount': str(amount),
                'currency': 'CDF',
                'customer': {
                    'email': user.email,
                    'phonenumber': phone,
                    'name': f"{user.first_name} {user.last_name}",
                },
                'customizations': {
                    'title': 'BNC Digital Library',
                    'description': f'Achat: {book.title}',
                    'logo': settings.SITE_URL + '/static/images/logo.png' if hasattr(settings, 'SITE_URL') else None,
                },
                'meta': {
                    'user_id': user.id,
                    'book_id': book.id,
                    'network': network,
                    'phone': phone,
                },
                'redirect_url': f"{settings.SITE_URL}/payment/callback/" if hasattr(settings, 'SITE_URL') else None,
            }
            
            # Ajouter le paramètre du réseau pour Mobile Money
            if network in ['airtel', 'orange', 'vodacom', 'moov']:
                payload['payment_method'] = 'mobilemoneyrwanda' if network == 'vodacom' else f'mobileoney{network}'
                payload['phone_number'] = phone
            
            logger.info(f"🔄 Initiating payment for user {user.email}, book {book.id}, network {network}")
            
            # Faire la requête
            response = requests.post(
                f"{self.BASE_URL}/charges?type=mobile_money_{network}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                logger.info(f"✅ Payment initiated: {result.get('data', {}).get('id')}")
                return {
                    'success': True,
                    'data': result.get('data'),
                    'reference': result.get('data', {}).get('tx_ref'),
                }
            else:
                logger.error(f"❌ Payment failed: {result.get('message')}")
                return {
                    'success': False,
                    'error': result.get('message', 'Erreur lors de l\'initialisation du paiement'),
                }
        
        except Exception as e:
            logger.error(f"❌ Exception in initiate_payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, transaction_id):
        """
        Vérifier le statut d'un paiement
        
        Args:
            transaction_id: ID de la transaction
        
        Returns:
            dict: Statut de la transaction
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
            }
            
            response = requests.get(
                f"{self.BASE_URL}/transactions/{transaction_id}/verify",
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                return {
                    'success': True,
                    'status': data.get('status'),  # 'successful', 'pending', 'failed'
                    'amount': data.get('amount'),
                    'currency': data.get('currency'),
                    'reference': data.get('tx_ref'),
                    'data': data,
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message'),
                }
        
        except Exception as e:
            logger.error(f"❌ Exception in verify_payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_networks(self):
        """Retourner la liste des réseaux disponibles"""
        return self.NETWORKS_RDC
    
    @staticmethod
    def format_phone(phone, network):
        """
        Formater le numéro de téléphone selon le réseau
        
        RDC codes:
        - Airtel: +243 (0) 81/82/83/84/85
        - Orange: +243 (0) 80/87/89
        - Vodacom: +243 (0) 99/98
        - Moov: +243 (0) 97
        """
        phone = phone.replace(' ', '').replace('-', '')
        
        if not phone.startswith('+243'):
            if phone.startswith('0'):
                phone = '+243' + phone[1:]
            else:
                phone = '+243' + phone
        
        return phone
