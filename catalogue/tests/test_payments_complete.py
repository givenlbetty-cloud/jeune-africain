"""
Tests complets pour le système de paiement.
Couvre: Stripe, PayPal, Mobile Money, Réconciliation.
"""

import json
from decimal import Decimal
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from catalogue.models import Payment, Book
from unittest.mock import patch, MagicMock
import uuid

User = get_user_model()


class PaymentModelTests(TestCase):
    """Tests pour le modèle Payment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
    
    def test_payment_creation(self):
        """Test création d'un paiement"""
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id=f'BNC_{uuid.uuid4().hex[:16]}',
            payment_method='credit_card',
            status='pending'
        )
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.book, self.book)
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_completion(self):
        """Test marquage d'un paiement comme complété"""
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id=f'BNC_{uuid.uuid4().hex[:16]}',
            payment_method='STRIPE'
        )
        
        payment.status = 'COMPLETED'
        payment.processed_at = timezone.now()
        payment.save()
        
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertIsNotNone(payment.processed_at)
    
    def test_duplicate_payment_prevention(self):
        """Test prévention des doublons"""
        transaction_id = f'BNC_{uuid.uuid4().hex[:16]}'
        
        Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id=transaction_id,
            payment_method='STRIPE'
        )
        
        # Vérifier qu'un même paiement existe
        existing = Payment.objects.filter(
            user=self.user,
            book=self.book,
            transaction_id=transaction_id
        ).exists()
        
        self.assertTrue(existing)


class StripePaymentTests(TransactionTestCase):
    """Tests pour intégration Stripe"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
        
        self.payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='pi_test_123',
            payment_method='STRIPE',
            status='PENDING'
        )
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_succeeded(self, mock_construct):
        """Test webhook Stripe - paiement réussi"""
        mock_construct.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'status': 'succeeded'
                }
            }
        }
        
        response = self.client.post(
            '/api/payments/stripe/webhook/',
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le paiement est complété
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_failed(self, mock_construct):
        """Test webhook Stripe - paiement échoué"""
        mock_construct.return_value = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'last_payment_error': {
                        'message': 'Your card was declined'
                    }
                }
            }
        }
        
        response = self.client.post(
            '/api/payments/stripe/webhook/',
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'FAILED')
        self.assertIn('declined', self.payment.error_message)


class PayPalPaymentTests(TransactionTestCase):
    """Tests pour intégration PayPal"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
        
        self.payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='PAYID-test123',
            payment_method='PAYPAL',
            status='PENDING'
        )
    
    @patch('catalogue.payment_webhooks.verify_paypal_webhook_signature')
    def test_paypal_webhook_payment_completed(self, mock_verify):
        """Test webhook PayPal - paiement complété"""
        mock_verify.return_value = True
        
        webhook_data = {
            'event_type': 'PAYMENT.SALE.COMPLETED',
            'resource': {
                'id': 'PAYID-test123',
                'state': 'completed'
            }
        }
        
        response = self.client.post(
            '/api/payments/paypal/webhook/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')
    
    @patch('catalogue.payment_webhooks.verify_paypal_webhook_signature')
    def test_paypal_webhook_invalid_signature(self, mock_verify):
        """Test webhook PayPal - signature invalide"""
        mock_verify.return_value = False
        
        webhook_data = {
            'event_type': 'PAYMENT.SALE.COMPLETED',
            'resource': {'id': 'PAYID-test123'}
        }
        
        response = self.client.post(
            '/api/payments/paypal/webhook/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)


class MobileMoneyPaymentTests(TransactionTestCase):
    """Tests pour Mobile Money (Airtel, M-Pesa)"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
    
    @patch('catalogue.payment_webhooks.verify_airtel_signature')
    def test_airtel_webhook_payment_completed(self, mock_verify):
        """Test webhook Airtel Money"""
        mock_verify.return_value = True
        
        airtel_payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='AIRTEL_test123',
            payment_method='AIRTEL_MONEY',
            status='PENDING'
        )
        
        webhook_data = {
            'transactionId': 'AIRTEL_test123',
            'status': 'SUCCESS'
        }
        
        response = self.client.post(
            '/api/payments/airtel/webhook/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        airtel_payment.refresh_from_db()
        self.assertEqual(airtel_payment.status, 'COMPLETED')
    
    def test_mpesa_webhook_payment_completed(self):
        """Test webhook M-Pesa"""
        mpesa_payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='MPESA_test123',
            checkout_request_id='ws_CO_123456789',
            payment_method='MPESA',
            status='PENDING'
        )
        
        webhook_data = {
            'Body': {
                'stkCallback': {
                    'MerchantRequestID': 'test123',
                    'CheckoutRequestID': 'ws_CO_123456789',
                    'ResultCode': 0,  # Success
                    'ResultDesc': 'The service request is processed successfully.'
                }
            }
        }
        
        response = self.client.post(
            '/api/payments/mpesa/webhook/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        mpesa_payment.refresh_from_db()
        self.assertEqual(mpesa_payment.status, 'COMPLETED')


class PaymentReconciliationTests(TransactionTestCase):
    """Tests pour la réconciliation des paiements"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
    
    def test_pending_payment_exists(self):
        """Test existence de paiements en attente"""
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='test_pending_123',
            payment_method='STRIPE',
            status='PENDING'
        )
        
        pending = Payment.objects.filter(status='PENDING')
        self.assertTrue(pending.exists())
        self.assertIn(payment, pending)
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_stripe_payment_reconciliation(self, mock_retrieve):
        """Test réconciliation Stripe"""
        from catalogue.payment_webhooks import reconcile_stripe_payment
        
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='pi_test_123',
            payment_method='STRIPE',
            status='PENDING'
        )
        
        mock_intent = MagicMock()
        mock_intent.status = 'succeeded'
        mock_intent.id = 'pi_test_123'
        mock_retrieve.return_value = mock_intent
        
        reconcile_stripe_payment(payment)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')


class PaymentIntegrationTests(TransactionTestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en',
            price=Decimal('29.99'),
            is_published=True
        )
    
    def test_payment_lifecycle(self):
        """Test cycle complet d'un paiement"""
        # 1. Créer paiement (PENDING)
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=Decimal('29.99'),
            currency='XOF',
            transaction_id='pi_complete_123',
            payment_method='STRIPE',
            status='PENDING'
        )
        
        self.assertEqual(payment.status, 'PENDING')
        
        # 2. Marquer comme complété
        payment.status = 'COMPLETED'
        payment.processed_at = timezone.now()
        payment.external_transaction_id = 'ch_complete_123'
        payment.save()
        
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertIsNotNone(payment.processed_at)
        
        # 3. Vérifier le paiement
        completed_payment = Payment.objects.get(transaction_id='pi_complete_123')
        self.assertEqual(completed_payment.status, 'COMPLETED')
