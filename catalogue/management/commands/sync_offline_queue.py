"""
Django management command: Sync offline queue
python manage.py sync_offline_queue [--user-id=USER_ID] [--all]

Traite tous les éléments en attente de synchronisation dans SyncQueue
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from catalogue.offline_sync import SyncQueueProcessor, sync_offline_queue
from catalogue.models import SyncQueue
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Synchronise la queue offline des utilisateurs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID de l\'utilisateur à synchroniser'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Synchroniser tous les utilisateurs avec des items en attente'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Afficher les détails du traitement'
        )
    
    def handle(self, *args, **options):
        verbose = options.get('verbose')
        
        if options.get('user_id'):
            # Synchroniser un utilisateur spécifique
            try:
                user = User.objects.get(id=options['user_id'])
                self.sync_user(user, verbose)
            except User.DoesNotExist:
                raise CommandError(f"Utilisateur avec ID {options['user_id']} non trouvé")
        
        elif options.get('all'):
            # Synchroniser tous les utilisateurs
            self.sync_all_users(verbose)
        
        else:
            # Synchroniser les utilisateurs avec items en attente
            self.sync_pending_users(verbose)
    
    def sync_user(self, user, verbose):
        """Synchroniser un utilisateur spécifique"""
        self.stdout.write(f"Synchronisation de l'utilisateur {user.username}...")
        
        try:
            result = sync_offline_queue(user)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Synchronisation complète pour {user.username}"
                )
            )
            
            if verbose:
                self.print_results(result)
        
        except Exception as e:
            logger.error(f"Erreur sync utilisateur {user.id}: {str(e)}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"✗ Erreur: {str(e)}")
            )
    
    def sync_all_users(self, verbose):
        """Synchroniser tous les utilisateurs"""
        users = User.objects.filter(is_active=True)
        self.stdout.write(f"Synchronisation de {users.count()} utilisateurs...")
        
        processor = SyncQueueProcessor()
        
        for user in users:
            try:
                result = processor.process_user_queue(user)
                
                if verbose and result['total'] > 0:
                    self.stdout.write(
                        f"  {user.username}: {result['successful']} réussis, "
                        f"{result['failed']} échoués"
                    )
            
            except Exception as e:
                logger.error(f"Erreur sync {user.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"  {user.username}: Erreur")
                )
        
        results = processor.results
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Synchronisation complète: {len(results['successful'])} réussis, "
                f"{len(results['failed'])} échoués"
            )
        )
        
        if verbose:
            self.print_results(results)
    
    def sync_pending_users(self, verbose):
        """Synchroniser les utilisateurs avec items en attente"""
        pending_users = SyncQueue.objects.filter(
            synced=False
        ).values_list('user_id', flat=True).distinct()
        
        pending_count = pending_users.count()
        
        if pending_count == 0:
            self.stdout.write(
                self.style.SUCCESS("✓ Aucun item en attente de synchronisation")
            )
            return
        
        self.stdout.write(
            f"Synchronisation de {pending_count} utilisateurs avec items en attente..."
        )
        
        processor = SyncQueueProcessor()
        
        for user_id in pending_users:
            user = User.objects.get(id=user_id)
            try:
                result = processor.process_user_queue(user)
                
                if verbose and result['total'] > 0:
                    self.stdout.write(
                        f"  {user.username}: {len(result['successful'])} réussis, "
                        f"{len(result['failed'])} échoués"
                    )
            
            except Exception as e:
                logger.error(f"Erreur sync {user_id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"  {user.username}: Erreur")
                )
        
        results = processor.results
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Synchronisation complète: {len(results['successful'])} réussis, "
                f"{len(results['failed'])} échoués"
            )
        )
        
        if verbose:
            self.print_results(results)
    
    def print_results(self, results):
        """Afficher les résultats détaillés"""
        if isinstance(results, dict) and 'successful' in results:
            successful = results.get('successful', [])
            failed = results.get('failed', [])
        else:
            return
        
        if successful:
            self.stdout.write("\nActions réussies:")
            for item in successful[:10]:  # Afficher les 10 premiers
                action = item.get('action', 'unknown')
                result_id = item.get('id', 'unknown')
                self.stdout.write(f"  ✓ {action} (ID: {result_id})")
            
            if len(successful) > 10:
                self.stdout.write(f"  ... et {len(successful) - 10} autres")
        
        if failed:
            self.stdout.write("\nActions échouées:")
            for item in failed[:10]:  # Afficher les 10 premiers
                action = item.get('action', 'unknown')
                error = item.get('error', 'Unknown error')
                self.stdout.write(f"  ✗ {action}: {error}")
            
            if len(failed) > 10:
                self.stdout.write(f"  ... et {len(failed) - 10} autres")

