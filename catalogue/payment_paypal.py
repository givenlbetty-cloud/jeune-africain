"""
PayPal Payment Integration for BNC Digital Library
Supports sandbox and live modes
"""

import os
import logging
from decimal import Decimal

try:
    import paypalrestsdk
except ImportError:
    paypalrestsdk = None

logger = logging.getLogger(__name__)


class PayPalClient:
    """
    Client for PayPal API interactions
    
    Supports both Sandbox (testing) and Live (production) modes
    """
    
    def __init__(self):
        """Initialize PayPal client with credentials from environment"""
        if not paypalrestsdk:
            logger.error("paypalrestsdk not installed. Run: pip install paypalrestsdk")
            raise ImportError("paypalrestsdk is required")
        
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.api_url = os.getenv('PAYPAL_API_URL', 
                                'https://api-m.sandbox.paypal.com')
        
        if not self.client_id or not self.client_secret:
            logger.error("PayPal credentials not configured in environment")
            raise ValueError("PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set")
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            'mode': self.mode,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        
        logger.info(f"PayPal client initialized in {self.mode} mode")
    
    def create_payment(self, amount, currency, description, 
                      return_url, cancel_url, order_id=None, email=None):
        """
        Create a PayPal payment
        
        Args:
            amount (Decimal): Payment amount
            currency (str): ISO currency code (USD, EUR, etc.)
            description (str): Payment description
            return_url (str): URL to redirect after successful payment
            cancel_url (str): URL to redirect if payment is cancelled
            order_id (str): Order ID for tracking
            email (str): Customer email
        
        Returns:
            (success: bool, approval_url: str, payment_id: str)
        
        Example:
            success, url, payment_id = client.create_payment(
                amount=Decimal('50.00'),
                currency='USD',
                description='Book purchase',
                return_url='https://yourdomain.com/paypal/success/',
                cancel_url='https://yourdomain.com/paypal/cancel/',
                order_id='ORDER-123'
            )
            
            if success:
                redirect(url)  # Redirect user to PayPal
        """
        try:
            # Validate inputs
            if not self._validate_inputs(amount, currency):
                return False, None, None
            
            # Create payment dictionary
            payment_dict = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency,
                        "details": {
                            "subtotal": str(amount)
                        }
                    },
                    "description": description,
                    "custom": order_id or str(order_id)
                }]
            }
            
            # Add email if provided
            if email:
                payment_dict["payer"]["email"] = email
            
            # Create payment
            payment = paypalrestsdk.Payment(payment_dict)
            
            if payment.create():
                logger.info(f"PayPal payment created: {payment.id}")
                logger.debug(f"Order: {order_id}, Amount: {amount} {currency}")
                
                # Extract approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == 'approval_url':
                        approval_url = link.href
                        break
                
                if not approval_url:
                    logger.error(f"No approval URL found in payment: {payment.id}")
                    return False, None, None
                
                return True, approval_url, payment.id
            else:
                logger.error(f"PayPal payment creation failed: {payment.error}")
                logger.error(f"Details: {payment.message}")
                return False, None, None
        
        except Exception as e:
            logger.error(f"PayPal payment creation error: {str(e)}", exc_info=True)
            return False, None, None
    
    def execute_payment(self, payment_id, payer_id):
        """
        Execute a PayPal payment after user approval
        
        Args:
            payment_id (str): ID of the payment to execute
            payer_id (str): ID of the payer (from PayPal redirect)
        
        Returns:
            (success: bool, transaction_id: str)
        
        Example:
            success, tx_id = client.execute_payment(payment_id, payer_id)
            
            if success:
                print(f"Payment successful, Transaction ID: {tx_id}")
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logger.info(f"PayPal payment executed: {payment.id}")
                
                # Extract transaction ID
                transaction_id = None
                if (payment.transactions and 
                    len(payment.transactions) > 0 and
                    payment.transactions[0].related_resources):
                    
                    related_resources = payment.transactions[0].related_resources
                    if related_resources and len(related_resources) > 0:
                        if hasattr(related_resources[0], 'sale'):
                            transaction_id = related_resources[0].sale.id
                
                if not transaction_id:
                    logger.warning(f"No transaction ID found for payment: {payment.id}")
                
                return True, transaction_id
            else:
                logger.error(f"PayPal payment execution failed: {payment.error}")
                logger.error(f"Details: {payment.message}")
                return False, None
        
        except Exception as e:
            logger.error(f"PayPal payment execution error: {str(e)}", exc_info=True)
            return False, None
    
    def get_payment_details(self, payment_id):
        """
        Get details of a PayPal payment
        
        Args:
            payment_id (str): PayPal payment ID
        
        Returns:
            dict: Payment details or None on error
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if not payment:
                logger.error(f"Payment not found: {payment_id}")
                return None
            
            return {
                'id': payment.id,
                'state': payment.state,
                'amount': payment.transactions[0].amount.total,
                'currency': payment.transactions[0].amount.currency,
                'payer_email': (payment.payer.payer_info.email 
                               if payment.payer and payment.payer.payer_info else None),
            }
        
        except Exception as e:
            logger.error(f"Error getting payment details: {str(e)}")
            return None
    
    def _validate_inputs(self, amount, currency):
        """
        Validate payment inputs
        
        Args:
            amount (Decimal): Payment amount
            currency (str): Currency code
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Valid currencies for PayPal
        valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'CHF', 'SEK', 'NZD',
                          'MXN', 'SGD', 'HKD', 'NOK', 'CZK', 'DKK', 'PLN', 'ZAR']
        
        if currency not in valid_currencies:
            logger.error(f"Unsupported currency: {currency}")
            return False
        
        if amount <= 0:
            logger.error(f"Invalid amount: {amount}")
            return False
        
        return True


def initiate_paypal_payment(amount, currency, description, 
                           return_url, cancel_url, order_id=None, email=None):
    """
    Convenience function to initiate a PayPal payment
    
    Args:
        amount (Decimal): Payment amount
        currency (str): ISO currency code
        description (str): Payment description
        return_url (str): Success redirect URL
        cancel_url (str): Cancellation redirect URL
        order_id (str): Order ID for tracking
        email (str): Customer email
    
    Returns:
        (success: bool, approval_url: str, payment_id: str)
    
    Usage:
        from decimal import Decimal
        from catalogue.payment_paypal import initiate_paypal_payment
        
        success, url, payment_id = initiate_paypal_payment(
            amount=Decimal('50.00'),
            currency='USD',
            description='Book purchase',
            return_url='https://yourdomain.com/paypal/success/',
            cancel_url='https://yourdomain.com/paypal/cancel/',
            order_id='ORDER-123',
            email='user@example.com'
        )
        
        if success:
            return redirect(url)
    """
    try:
        client = PayPalClient()
        return client.create_payment(amount, currency, description,
                                    return_url, cancel_url, order_id, email)
    except Exception as e:
        logger.error(f"Error initiating PayPal payment: {str(e)}")
        return False, None, None
