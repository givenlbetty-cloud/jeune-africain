"""
Tests complets pour le Forum Communautaire - Phase 8
Testons: Catégories, Discussions, Commentaires, Votes, Notifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from catalogue.models import (
    ForumCategory, Discussion, Comment, Vote, ForumNotification
)

User = get_user_model()


class ForumCategoryModelTest(TestCase):
    """Tests pour le modèle ForumCategory."""
    
    def setUp(self):
        """Créer les données de test."""
        self.category = ForumCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category',
            icon='💬'
        )
    
    def test_category_creation(self):
        """Tester la création d'une catégorie."""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
    
    def test_category_str(self):
        """Tester la représentation en string."""
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_discussion_count(self):
        """Tester le compteur de discussions."""
        self.assertEqual(self.category.discussion_count, 0)
        
        user = User.objects.create_user(username='test', email='test@example.com', password='test')
        Discussion.objects.create(
            category=self.category,
            author=user,
            title='Test Discussion',
            content='Content'
        )
        self.assertEqual(self.category.discussion_count, 1)


class DiscussionModelTest(TestCase):
    """Tests pour le modèle Discussion."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='author', email='author@example.com', password='test')
        self.category = ForumCategory.objects.create(
            name='Test',
            slug='test'
        )
        self.discussion = Discussion.objects.create(
            category=self.category,
            author=self.user,
            title='Test Discussion',
            content='This is a test discussion.'
        )
    
    def test_discussion_creation(self):
        """Tester la création d'une discussion."""
        self.assertEqual(self.discussion.title, 'Test Discussion')
        self.assertEqual(self.discussion.author, self.user)
        self.assertEqual(self.discussion.status, 'open')
    
    def test_increment_views(self):
        """Tester l'incrémentation des vues."""
        self.assertEqual(self.discussion.views_count, 0)
        self.discussion.increment_views()
        self.assertEqual(self.discussion.views_count, 1)
    
    def test_is_pinned(self):
        """Tester la propriété is_pinned."""
        self.assertFalse(self.discussion.is_pinned)
        self.discussion.status = 'pinned'
        self.assertTrue(self.discussion.is_pinned)
    
    def test_is_closed(self):
        """Tester la propriété is_closed."""
        self.assertFalse(self.discussion.is_closed)
        self.discussion.status = 'closed'
        self.assertTrue(self.discussion.is_closed)


class CommentModelTest(TestCase):
    """Tests pour le modèle Comment."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.category = ForumCategory.objects.create(
            name='Test',
            slug='test'
        )
        self.discussion = Discussion.objects.create(
            category=self.category,
            author=self.user,
            title='Test',
            content='Content'
        )
        self.comment = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            content='This is a comment.'
        )
    
    def test_comment_creation(self):
        """Tester la création d'un commentaire."""
        self.assertEqual(self.comment.content, 'This is a comment.')
        self.assertEqual(self.comment.author, self.user)
    
    def test_comment_updates_discussion(self):
        """Tester que le commentaire met à jour les compteurs."""
        # Recharger depuis la base de données
        updated_discussion = Discussion.objects.get(pk=self.discussion.pk)
        self.assertEqual(updated_discussion.comments_count, 1)
        self.assertIsNotNone(updated_discussion.last_comment_at)
    
    def test_reply_count(self):
        """Tester le compteur de réponses."""
        self.assertEqual(self.comment.reply_count, 0)
        
        reply = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            parent=self.comment,
            content='Reply'
        )
        self.assertEqual(self.comment.reply_count, 1)
    
    def test_nested_replies(self):
        """Tester les réponses imbriquées."""
        reply1 = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            parent=self.comment,
            content='Reply 1'
        )
        
        reply2 = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            parent=reply1,
            content='Reply to reply'
        )
        
        self.assertEqual(self.comment.reply_count, 1)
        self.assertEqual(reply1.reply_count, 1)


class VoteModelTest(TestCase):
    """Tests pour le modèle Vote."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.category = ForumCategory.objects.create(
            name='Test',
            slug='test'
        )
        self.discussion = Discussion.objects.create(
            category=self.category,
            author=self.user,
            title='Test',
            content='Content'
        )
    
    def test_vote_on_discussion(self):
        """Tester le vote sur une discussion."""
        vote = Vote.objects.create(
            user=self.user,
            discussion=self.discussion,
            value=1
        )
        self.assertEqual(self.discussion.upvotes_count, 1)
    
    def test_vote_on_comment(self):
        """Tester le vote sur un commentaire."""
        comment = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            content='Comment'
        )
        
        vote = Vote.objects.create(
            user=self.user,
            comment=comment,
            value=1
        )
        self.assertEqual(comment.upvotes_count, 1)


class ForumCategoryAPITest(APITestCase):
    """Tests API pour les catégories du forum."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.client = APIClient()
        
        self.category = ForumCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test'
        )
    
    def test_list_categories(self):
        """Tester la liste des catégories."""
        response = self.client.get('/api/forum-categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_retrieve_category(self):
        """Tester la récupération d'une catégorie."""
        response = self.client.get(f'/api/forum-categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')


class DiscussionAPITest(APITestCase):
    """Tests API pour les discussions."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='test')
        self.client = APIClient()
        
        self.category = ForumCategory.objects.create(
            name='Test',
            slug='test'
        )
        
        self.discussion = Discussion.objects.create(
            category=self.category,
            author=self.user,
            title='Test Discussion',
            content='Content'
        )
    
    def test_list_discussions(self):
        """Tester la liste des discussions."""
        response = self.client.get('/api/forum-discussions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_discussion_authenticated(self):
        """Tester la création d'une discussion authentifié."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'category': self.category.id,
            'title': 'New Discussion',
            'content': 'New content'
        }
        
        response = self.client.post('/api/forum-discussions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], self.user.id)
    
    def test_create_discussion_anonymous(self):
        """Tester que les anonymes ne peuvent pas créer."""
        data = {
            'category': self.category.id,
            'title': 'New Discussion',
            'content': 'Content'
        }
        
        response = self.client.post('/api/forum-discussions/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_discussion(self):
        """Tester la récupération d'une discussion."""
        response = self.client.get(f'/api/forum-discussions/{self.discussion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Discussion')
        # Vérifier que les vues ont été incrémentées
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.views_count, 1)
    
    def test_update_discussion_owner(self):
        """Tester que seul le propriétaire peut modifier."""
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(
            f'/api/forum-discussions/{self.discussion.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_discussion_non_owner(self):
        """Tester que les non-propriétaires ne peuvent pas modifier."""
        self.client.force_authenticate(user=self.other_user)
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(
            f'/api/forum-discussions/{self.discussion.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_close_discussion(self):
        """Tester la fermeture d'une discussion."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/forum-discussions/{self.discussion.id}/close/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.status, 'closed')
    
    def test_upvote_discussion(self):
        """Tester l'upvote d'une discussion."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/forum-discussions/{self.discussion.id}/upvote/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.discussion.refresh_from_db()
        self.assertEqual(self.discussion.upvotes_count, 1)


class CommentAPITest(APITestCase):
    """Tests API pour les commentaires."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.client = APIClient()
        
        self.category = ForumCategory.objects.create(name='Test', slug='test')
        self.discussion = Discussion.objects.create(
            category=self.category,
            author=self.user,
            title='Test',
            content='Content'
        )
    
    def test_create_comment(self):
        """Tester la création d'un commentaire."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'discussion': self.discussion.id,
            'content': 'This is a comment.'
        }
        
        response = self.client.post('/api/forum-comments/', data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_reply_to_comment(self):
        """Tester la réponse à un commentaire."""
        self.client.force_authenticate(user=self.user)
        
        comment = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            content='Original comment'
        )
        
        data = {
            'discussion': self.discussion.id,
            'parent': comment.id,
            'content': 'Reply'
        }
        
        response = self.client.post('/api/forum-comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_upvote_comment(self):
        """Tester l'upvote d'un commentaire."""
        self.client.force_authenticate(user=self.user)
        
        comment = Comment.objects.create(
            discussion=self.discussion,
            author=self.user,
            content='Comment'
        )
        
        response = self.client.post(
            f'/api/forum-comments/{comment.id}/upvote/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        comment.refresh_from_db()
        self.assertEqual(comment.upvotes_count, 1)


class ForumNotificationAPITest(APITestCase):
    """Tests API pour les notifications du forum."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.client = APIClient()
    
    def test_list_notifications(self):
        """Tester la liste des notifications."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/forum-notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unread_count(self):
        """Tester le compteur de non-lus."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/forum-notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 0)


class ForumIntegrationTest(APITestCase):
    """Tests d'intégration du forum complet."""
    
    def setUp(self):
        """Créer les données de test."""
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='test')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='test')
        self.client = APIClient()
        
        self.category = ForumCategory.objects.create(name='Test', slug='test')
    
    def test_full_discussion_flow(self):
        """Tester le flux complet: créer → commenter → voter."""
        # User1 crée une discussion
        self.client.force_authenticate(user=self.user1)
        
        discussion_data = {
            'category': self.category.id,
            'title': 'Integration Test Discussion',
            'content': 'Let\'s test the forum!'
        }
        
        response = self.client.post('/api/forum-discussions/', discussion_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        discussion_id = response.data['id']
        
        # User2 ajoute un commentaire
        self.client.force_authenticate(user=self.user2)
        
        comment_data = {
            'discussion': discussion_id,
            'content': 'Great discussion!'
        }
        
        response = self.client.post('/api/forum-comments/', comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        
        # User1 upvote le commentaire
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(
            f'/api/forum-comments/{comment_id}/upvote/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que tout est à jour
        response = self.client.get(f'/api/forum-discussions/{discussion_id}/')
        self.assertEqual(response.data['comments_count'], 1)
