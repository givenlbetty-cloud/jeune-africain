"""
Intégration Flutterwave pour les paiements Mobile Money RDC
Supporte: Airtel Money, Orange Money, Vodacom M-Pesa, Moov Money
"""

import requests
import json
import logging
from django.conf import settings
from decimal import Decimal
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class FlutterwavePaymentGateway:
    """
    Classe pour gérer les paiements Mobile Money via Flutterwave
    """
    
    # Réseaux mobiles supportés en RDC
    MOBILE_NETWORKS = {
        'airtel': {
            'name': 'Airtel Money',
            'code': 'AIRTEL',
            'icon': '📱',
            'min_amount': Decimal('100'),
            'max_amount': Decimal('500000'),
        },
        'orange': {
            'name': 'Orange Money',
            'code': 'ORANGE',
            'icon': '🟠',
            'min_amount': Decimal('100'),
            'max_amount': Decimal('500000'),
        },
        'vodacom': {
            'name': 'Vodacom M-Pesa',
            'code': 'MPESA',
            'icon': '💰',
            'min_amount': Decimal('100'),
            'max_amount': Decimal('500000'),
        },
        'moov': {
            'name': 'Moov Money',
            'code': 'MOOV',
            'icon': '📲',
            'min_amount': Decimal('100'),
            'max_amount': Decimal('500000'),
        },
    }
    
    # Configuration Flutterwave
    BASE_URL = 'https://api.flutterwave.com/v3'
    TIMEOUT = 30
    
    def __init__(self):
        """Initialiser avec les clés API"""
        self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', '')
        self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', '')
        
        if not self.secret_key or not self.public_key:
            logger.warning("Flutterwave keys not configured - using demo mode")
    
    def get_networks(self) -> Dict:
        """Retourner les réseaux mobiles disponibles"""
        return self.MOBILE_NETWORKS
    
    def validate_amount(self, amount: Decimal, network: str) -> Tuple[bool, str]:
        """Valider le montant pour un réseau"""
        if network not in self.MOBILE_NETWORKS:
            return False, f"Réseau {network} non supporté"
        
        network_config = self.MOBILE_NETWORKS[network]
        min_amount = network_config['min_amount']
        max_amount = network_config['max_amount']
        
        if amount < min_amount:
            return False, f"Montant minimum: {min_amount} USD"
        
        if amount > max_amount:
            return False, f"Montant maximum: {max_amount} USD"
        
        return True, "OK"
    
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """Valider le numéro de téléphone RDC"""
        # Format RDC: +243XXXXXXXXX ou 0XXXXXXXXX
        phone = phone.strip()
        
        # Retirer les espaces et tirets
        phone = phone.replace(' ', '').replace('-', '')
        
        # Vérifier si c'est un format valide
        if phone.startswith('0'):
            phone = '+243' + phone[1:]
        elif not phone.startswith('+243'):
            return False, "Format invalide. Utilisez: +243XXXXXXXXX ou 0XXXXXXXXX"
        
        # Vérifier la longueur
        if len(phone) != 13:  # +243 (4) + 9 chiffres
            return False, "Numéro de téléphone invalide"
        
        return True, phone
    
    def create_payment_request(
        self,
        user_email: str,
        user_phone: str,
        user_name: str,
        amount: Decimal,
        network: str,
        book_id: str,
        transaction_ref: str,
    ) -> Dict:
        """
        Créer une requête de paiement Flutterwave
        
        Args:
            user_email: Email de l'utilisateur
            user_phone: Numéro de téléphone (format international)
            user_name: Nom complet
            amount: Montant en USD
            network: Réseau (airtel, orange, vodacom, moov)
            book_id: ID du livre
            transaction_ref: Référence unique de transaction
        
        Returns:
            Dict avec les détails de la transaction
        """
        
        # Valider les données
        valid, message = self.validate_amount(amount, network)
        if not valid:
            return {'success': False, 'error': message}
        
        valid, phone = self.validate_phone_number(user_phone)
        if not valid:
            return {'success': False, 'error': phone}
        
        # Configuration réseau
        network_config = self.MOBILE_NETWORKS.get(network, {})
        
        # Préparer les données pour Flutterwave
        payload = {
            'tx_ref': transaction_ref,
            'amount': str(amount),
            'currency': 'USD',
            'customer': {
                'email': user_email,
                'phonenumber': phone,
                'name': user_name,
            },
            'customizations': {
                'title': 'BNC Digital Library',
                'description': f'Achat de livre - Référence: {book_id}',
                'logo': 'https://bnc-digital.com/logo.png',
            },
            'meta': {
                'book_id': book_id,
                'network': network,
                'payment_type': 'mobile_money',
            },
        }
        
        # En mode test/demo, retourner une réponse simulée
        if not self.secret_key or not self.public_key:
            return self._create_demo_response(payload, transaction_ref, network_config)
        
        # Appel API Flutterwave
        return self._call_flutterwave_api(payload, phone, network_config)
    
    def _call_flutterwave_api(self, payload: Dict, phone: str, network_config: Dict) -> Dict:
        """Appeler l'API Flutterwave"""
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            # Ajouter les détails du réseau mobile
            payload['payment_options'] = f'{network_config["code"]}'
            
            response = requests.post(
                f'{self.BASE_URL}/charges',
                json=payload,
                headers=headers,
                timeout=self.TIMEOUT,
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'transaction_id': data['data']['id'],
                        'reference': data['data']['tx_ref'],
                        'amount': data['data']['amount'],
                        'status': 'pending',
                        'phone': phone,
                        'message': 'Paiement en cours. Confirmez sur votre téléphone.',
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Erreur de paiement'),
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erreur serveur Flutterwave: {response.status_code}',
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Flutterwave API error: {str(e)}")
            return {
                'success': False,
                'error': 'Erreur de connexion. Veuillez réessayer.',
            }
    
    def _create_demo_response(self, payload: Dict, transaction_ref: str, network_config: Dict) -> Dict:
        """Créer une réponse de démonstration (mode test)"""
        return {
            'success': True,
            'transaction_id': f'DEMO_{transaction_ref}',
            'reference': transaction_ref,
            'amount': payload['amount'],
            'status': 'pending',
            'phone': payload['customer']['phonenumber'],
            'network': network_config['name'],
            'message': f'Paiement en cours via {network_config["name"]}. Confirmez sur votre téléphone.',
            'demo_mode': True,
        }
    
    def verify_transaction(self, transaction_id: str) -> Dict:
        """
        Vérifier le statut d'une transaction
        
        Returns:
            Dict avec le statut (successful, failed, pending)
        """
        if not self.secret_key:
            # Mode démo - simuler un paiement réussi après 5 secondes
            return {
                'success': True,
                'status': 'successful',
                'message': 'Paiement confirmé! Le livre est maintenant accessible.',
                'demo_mode': True,
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
            }
            
            response = requests.get(
                f'{self.BASE_URL}/transactions/{transaction_id}/verify',
                headers=headers,
                timeout=self.TIMEOUT,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'status': data['data']['status'],
                    'amount': data['data']['amount'],
                    'reference': data['data']['tx_ref'],
                }
            else:
                return {
                    'success': False,
                    'status': 'error',
                    'error': 'Impossible de vérifier la transaction',
                }
        
        except Exception as e:
            logger.error(f"Transaction verification error: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
            }
    
    def initiate_charge(self, transaction_id: str, otp: Optional[str] = None) -> Dict:
        """
        Initier la charge (après confirmation OTP)
        
        Args:
            transaction_id: ID de la transaction
            otp: Code OTP entré par l'utilisateur
        
        Returns:
            Réponse de confirmation
        """
        if not self.secret_key:
            # Mode démo
            return {
                'success': True,
                'status': 'successful',
                'message': 'Paiement confirmé avec succès!',
                'demo_mode': True,
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'otp': otp or '123456',  # L'utilisateur entre le code reçu
            }
            
            response = requests.post(
                f'{self.BASE_URL}/charges/{transaction_id}/resolve',
                json=payload,
                headers=headers,
                timeout=self.TIMEOUT,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': data['status'] == 'success',
                    'status': data['data']['status'],
                    'message': data.get('message', 'Paiement confirmé'),
                }
            else:
                return {
                    'success': False,
                    'error': 'Erreur lors de la confirmation',
                }
        
        except Exception as e:
            logger.error(f"Charge initiation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }


# Instance globale
flutterwave = FlutterwavePaymentGateway()
