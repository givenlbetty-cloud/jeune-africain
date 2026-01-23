"""
Management command to setup OAuth applications in Django admin.
Run this after configuring Google OAuth credentials.

Usage:
    python manage.py setup_oauth --provider google --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
    python manage.py setup_oauth --list
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup OAuth applications for social authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all configured OAuth apps',
        )
        parser.add_argument(
            '--provider',
            type=str,
            help='OAuth provider (google, apple, windows)',
        )
        parser.add_argument(
            '--client-id',
            type=str,
            help='OAuth Client ID',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='OAuth Client Secret',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Application name (optional, defaults to provider name)',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_oauth_apps()
        elif options['provider'] and options['client_id'] and options['client_secret']:
            self.setup_oauth_app(
                options['provider'],
                options['client_id'],
                options['client_secret'],
                options.get('name')
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Please provide either --list or --provider with --client-id and --client-secret'
                )
            )
            self.print_help()

    def list_oauth_apps(self):
        """List all configured OAuth applications"""
        apps = SocialApp.objects.all()
        
        if not apps.exists():
            self.stdout.write(self.style.WARNING('No OAuth apps configured yet.'))
            self.stdout.write(self.style.NOTICE('\n📋 To setup Google OAuth:'))
            self.stdout.write('1. Create Google OAuth 2.0 credentials at: https://console.cloud.google.com/')
            self.stdout.write('2. Set Authorized redirect URIs to: http://localhost:8000/auth/google/callback/')
            self.stdout.write('3. Run: python manage.py setup_oauth --provider google --client-id YOUR_ID --client-secret YOUR_SECRET')
            return

        self.stdout.write(self.style.SUCCESS('✅ Configured OAuth Applications:'))
        self.stdout.write('=' * 80)
        
        for app in apps:
            sites = list(app.sites.values_list('name', flat=True))
            self.stdout.write(f'\n📱 {app.name}')
            self.stdout.write(f'   Provider: {app.provider}')
            self.stdout.write(f'   Client ID: {app.client_id[:20]}...' if len(app.client_id) > 20 else f'   Client ID: {app.client_id}')
            self.stdout.write(f'   Sites: {", ".join(sites) if sites else "None"}')

    def setup_oauth_app(self, provider, client_id, client_secret, name=None):
        """Setup or update an OAuth application"""
        
        # Validate provider
        valid_providers = ['google', 'apple', 'windows', 'github', 'facebook']
        if provider.lower() not in valid_providers:
            raise CommandError(f'Provider must be one of: {", ".join(valid_providers)}')
        
        app_name = name or provider.title()
        
        try:
            # Get or create the app
            app, created = SocialApp.objects.get_or_create(
                provider=provider.lower(),
                defaults={
                    'name': app_name,
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            # If existing, update credentials
            if not created:
                app.name = app_name
                app.client_id = client_id
                app.secret = client_secret
                app.save()
                action = 'Updated'
            else:
                action = 'Created'
            
            # Assign to current site
            site = Site.objects.get_current()
            if site not in app.sites.all():
                app.sites.add(site)
                self.stdout.write(self.style.SUCCESS(f'✅ {action} {provider.title()} OAuth app'))
                self.stdout.write(f'   Name: {app.name}')
                self.stdout.write(f'   Provider: {app.provider}')
                self.stdout.write(f'   Assigned to site: {site.name}')
                self.stdout.write(f'\n🌐 Redirect URI: http://{site.domain}/auth/google/callback/')
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ {action} {provider.title()} OAuth app'))
                self.stdout.write(f'   Already assigned to site: {site.name}')
                
        except Exception as e:
            raise CommandError(f'Error setting up OAuth app: {str(e)}')
