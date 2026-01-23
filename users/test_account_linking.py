"""
Tests pour Account Linking
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse

User = get_user_model()


class AccountLinkingTestCase(TestCase):
    """Tests pour la fonctionnalité Account Linking"""
    
    def setUp(self):
        """Créer des données de test"""
        self.client = Client()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un compte OAuth de test
        self.google_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='google_123',
            extra_data={
                'id': 'google_123',
                'email': 'test@gmail.com',
                'name': 'Test User',
                'picture': 'https://example.com/test.jpg'
            }
        )
    
    def test_manage_accounts_page_loads(self):
        """Test: Page de gestion des comptes se charge"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Gérer mes comptes', response.content.decode())
    
    def test_manage_accounts_requires_login(self):
        """Test: Redirection vers login si non authentifié"""
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_shows_connected_accounts(self):
        """Test: Affiche les comptes connectés"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        
        content = response.content.decode()
        self.assertIn('Google', content)
        self.assertIn('test@gmail.com', content)
    
    def test_disconnect_account(self):
        """Test: Déconnecter un compte OAuth"""
        # Ajouter un mot de passe pour pouvoir délier
        self.user.set_password('testpass123')
        self.user.save()
        
        self.client.login(username='testuser', password='testpass123')
        
        # Vérifier que le compte existe
        self.assertTrue(
            SocialAccount.objects.filter(
                user=self.user,
                provider='google'
            ).exists()
        )
        
        # Délier le compte
        response = self.client.post(
            reverse('fr:socialaccount_disconnect_account', args=[self.google_account.id]),
            follow=True
        )
        
        # Vérifier que le compte a été supprimé
        self.assertFalse(
            SocialAccount.objects.filter(
                user=self.user,
                provider='google'
            ).exists()
        )
    
    def test_cannot_disconnect_last_auth_method(self):
        """Test: Impossible de délier le dernier moyen d'authentification"""
        # Supprimer le mot de passe
        self.user.password = ''
        self.user.save()
        
        self.client.login(username='testuser', password='')
        
        # Essayer de délier le compte
        response = self.client.post(
            reverse('fr:socialaccount_disconnect_account', args=[self.google_account.id]),
            follow=True
        )
        
        # Vérifier que le compte n'a pas été supprimé
        self.assertTrue(
            SocialAccount.objects.filter(
                user=self.user,
                provider='google'
            ).exists()
        )
    
    def test_cannot_disconnect_other_users_account(self):
        """Test: Impossible de délier un compte d'un autre utilisateur"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
        
        self.client.login(username='otheruser', password='otherpass')
        
        # Essayer de délier le compte du premier utilisateur
        response = self.client.post(
            reverse('fr:socialaccount_disconnect_account', args=[self.google_account.id])
        )
        
        # Vérifier que le compte n'a pas été supprimé
        self.assertTrue(
            SocialAccount.objects.filter(
                user=self.user,
                provider='google'
            ).exists()
        )
    
    def test_link_multiple_accounts(self):
        """Test: Lier plusieurs comptes au même utilisateur"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ajouter un compte Apple
        apple_account = SocialAccount.objects.create(
            user=self.user,
            provider='apple',
            uid='apple_123',
            extra_data={
                'id': 'apple_123',
                'email': 'test@icloud.com',
                'name': 'Test User'
            }
        )
        
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        content = response.content.decode()
        
        # Vérifier que les deux comptes sont affichés
        self.assertIn('Google', content)
        self.assertIn('Apple', content)
        self.assertEqual(
            SocialAccount.objects.filter(user=self.user).count(),
            2
        )
    
    def test_account_linking_api_status(self):
        """Test: API pour récupérer le status des comptes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('fr:socialaccount_account_linking_status'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('google', data['connected_providers'])
        self.assertEqual(data['account_count'], 1)
        self.assertEqual(len(data['accounts']), 1)
    
    def test_merge_profiles(self):
        """Test: Fusionner les données de profil"""
        # Ajouter un compte Apple avec des données différentes
        apple_account = SocialAccount.objects.create(
            user=self.user,
            provider='apple',
            uid='apple_123',
            extra_data={
                'id': 'apple_123',
                'email': 'newemail@icloud.com',
                'name': 'New Test Name'
            }
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Fusionner les profils
        response = self.client.post(
            reverse('fr:socialaccount_merge_profiles'),
            {'primary_account_id': apple_account.id},
            follow=True
        )
        
        # Vérifier que le profil a été mis à jour
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@icloud.com')


class AccountLinkingIntegrationTestCase(TestCase):
    """Tests d'intégration pour Account Linking"""
    
    def setUp(self):
        """Créer des données de test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_full_account_linking_flow(self):
        """Test: Flux complet de liaison de comptes"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Afficher la page de gestion
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Créer un compte OAuth
        google_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='google_123',
            extra_data={'email': 'test@gmail.com', 'name': 'Google User'}
        )
        
        # 3. Vérifier qu'il apparaît sur la page
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        content = response.content.decode()
        self.assertIn('Google', content)
        
        # 4. Ajouter un autre compte
        apple_account = SocialAccount.objects.create(
            user=self.user,
            provider='apple',
            uid='apple_123',
            extra_data={'email': 'test@icloud.com', 'name': 'Apple User'}
        )
        
        # 5. Vérifier qu'ils sont tous les deux affichés
        response = self.client.get(reverse('fr:socialaccount_manage_accounts'))
        content = response.content.decode()
        self.assertIn('Google', content)
        self.assertIn('Apple', content)
