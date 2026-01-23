"""
Management command pour réconcilier les paiements en attente.

Usage:
    python manage.py reconcile_payments
    python manage.py reconcile_payments --payment-method STRIPE
    python manage.py reconcile_payments --hours 24
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Payment
from catalogue.payment_webhooks import (
    reconcile_stripe_payment,
    reconcile_paypal_payment,
    reconcile_mpesa_payment,
    reconcile_airtel_payment,
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reconcile pending payments with payment gateways'

    def add_arguments(self, parser):
        parser.add_argument(
            '--payment-method',
            type=str,
            default=None,
            help='Specific payment method to reconcile (STRIPE, PAYPAL, MPESA, AIRTEL_MONEY)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Only reconcile payments created in the last N hours (default: 24)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reconcile all pending payments regardless of creation time',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Starting payment reconciliation...'))
        
        # Construire la query
        pending_payments = Payment.objects.filter(status='PENDING')
        
        # Filtrer par méthode de paiement
        if options['payment_method']:
            method = options['payment_method'].upper()
            pending_payments = pending_payments.filter(payment_method=method)
            self.stdout.write(f'   Filtering by method: {method}')
        
        # Filtrer par date si non-all
        if not options['all']:
            hours_ago = timezone.now() - timedelta(hours=options['hours'])
            pending_payments = pending_payments.filter(created_at__gte=hours_ago)
            self.stdout.write(f'   Filtering payments from last {options["hours"]} hours')
        
        total = pending_payments.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('   No pending payments found'))
            return
        
        self.stdout.write(f'   Found {total} pending payments')
        
        # Réconcilier chaque paiement
        reconciled = 0
        failed = 0
        
        for payment in pending_payments:
            try:
                self.reconcile_payment(payment)
                reconciled += 1
                
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'   ✗ Error reconciling {payment.transaction_id}: {e}'
                    )
                )
                logger.error(f"Reconciliation error for {payment.id}: {e}")
        
        # Résumé
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS(f'✅ Reconciliation complete!'))
        self.stdout.write(f'   Total processed: {reconciled}/{total}')
        if failed > 0:
            self.stdout.write(self.style.WARNING(f'   Failed: {failed}'))

    def reconcile_payment(self, payment):
        """Réconcilier un paiement spécifique"""
        method = payment.payment_method
        
        if method == 'STRIPE':
            reconcile_stripe_payment(payment)
            status_update = 'STRIPE'
        elif method == 'PAYPAL':
            reconcile_paypal_payment(payment)
            status_update = 'PAYPAL'
        elif method == 'MPESA':
            reconcile_mpesa_payment(payment)
            status_update = 'M-PESA'
        elif method == 'AIRTEL_MONEY':
            reconcile_airtel_payment(payment)
            status_update = 'AIRTEL'
        else:
            status_update = 'UNKNOWN'
        
        # Vérifier le statut mis à jour
        payment.refresh_from_db()
        
        if payment.status == 'COMPLETED':
            self.stdout.write(
                self.style.SUCCESS(
                    f'   ✓ {status_update}: {payment.transaction_id} → COMPLETED'
                )
            )
        elif payment.status == 'FAILED':
            self.stdout.write(
                self.style.ERROR(
                    f'   ✗ {status_update}: {payment.transaction_id} → FAILED'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'   ⚠ {status_update}: {payment.transaction_id} → {payment.status}'
                )
            )
