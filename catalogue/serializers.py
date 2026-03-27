"""
DRF Serializers pour BNC API
Sécurité DRM: N'inclut PAS les fichiers numériques (pdf_file, epub_file)
"""

from rest_framework import serializers
from .models import (
    Author, AuthorMedia, Library, Book, AuthorBook, LibraryBook, Payment,
    Review, Highlight, Note, ReadingSession,
    ForumCategory, Discussion, Comment, Vote, ForumNotification,
    PDFAnnotation, AudiobookMetadata, AudiobookChapter, ListeningProgress,
    VideoMaterial, VideoPlayback, Podcast, PodcastEpisode,
    PodcastSubscription, PodcastProgress,
    TrendingBook, UserRecommendation
)


class AuthorMediaSerializer(serializers.ModelSerializer):
    """Serializer pour les vidéos/podcasts des auteurs"""
    
    class Meta:
        model = AuthorMedia
        fields = ['id', 'title', 'media_type', 'platform', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer pour les auteurs avec leurs médias"""
    media = AuthorMediaSerializer(source='authormedia_set', many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'biography', 'birth_date', 'nationality',
            'website', 'is_verified', 'photo', 'media'
        ]
        read_only_fields = ['id', 'is_verified']


class AuthorBookSerializer(serializers.ModelSerializer):
    """Serializer pour les relations Author-Book"""
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = AuthorBook
        fields = ['id', 'author', 'role']
        read_only_fields = ['id']


class LibrarySerializer(serializers.ModelSerializer):
    """Serializer pour les bibliothèques"""
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Library
        fields = [
            'id', 'name', 'description', 'location',
            'city', 'country', 'logo', 'is_active',
            'books_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_books_count(self, obj):
        """Compte les livres de la bibliothèque"""
        return obj.books.count()


class BookListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des livres (données allégées)
    🔐 IMPORTANT: N'inclut PAS pdf_file ni epub_file (DRM Protection)
    """
    authors = AuthorSerializer(many=True, read_only=True, source='get_authors')
    library = LibrarySerializer(read_only=True, source='library_set.first')
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'description',
            'genre', 'language', 'pages_count',
            'price', 'discount_percentage', 'final_price',
            'is_published', 'cover', 'authors', 'library',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_final_price(self, obj):
        """Calcule le prix final après réduction"""
        if obj.discount_percentage:
            reduction = obj.price * (obj.discount_percentage / 100)
            return obj.price - reduction
        return obj.price


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un seul livre
    🔐 IMPORTANT: N'inclut PAS pdf_file ni epub_file (DRM Protection)
    Inclut métadonnées complètes et relations
    """
    authors = AuthorSerializer(many=True, read_only=True, source='get_authors')
    author_books = AuthorBookSerializer(source='authorbook_set', many=True, read_only=True)
    library = LibrarySerializer(read_only=True, source='library_set.first')
    final_price = serializers.SerializerMethodField()
    rating_avg = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'description',
            'genre', 'language', 'pages_count',
            'publication_date', 'price', 'discount_percentage',
            'final_price', 'is_published', 'is_paid',
            'cover', 'authors', 'author_books',
            'library', 'rating_avg',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_final_price(self, obj):
        """Calcule le prix final après réduction"""
        if obj.discount_percentage:
            reduction = obj.price * (obj.discount_percentage / 100)
            return obj.price - reduction
        return obj.price
    
    def get_rating_avg(self, obj):
        """Retourne la note moyenne calculée depuis les reviews"""
        from django.db.models import Avg
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg else None


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les paiements"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'reference_number', 'amount',
            'currency', 'payment_method', 'payment_status',
            'payment_date', 'created_at'
        ]
        read_only_fields = ['id', 'reference_number', 'created_at']


# ============================================================================
# SERIALIZERS D'ACHAT DE LIVRES
# ============================================================================

class PurchaseBookSerializer(serializers.Serializer):
    """Serializer pour l'achat de livres"""
    book_id = serializers.CharField(required=True, help_text="ID du livre à acheter")
    
    def validate_book_id(self, value):
        """Valide que le livre existe"""
        try:
            Book.objects.get(id=value)
        except Book.DoesNotExist:
            raise serializers.ValidationError(f"Le livre avec l'ID {value} n'existe pas.")
        return value


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour afficher les paiements avec le livre"""
    book = BookListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user_email', 'book', 'amount', 'currency', 
            'transaction_id', 'status', 'payment_method', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ===================================
# Nouveaux Serializers - Phase 2
# ===================================

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer pour les critiques de livres."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user_name', 'user_email', 'book', 'rating', 'title', 'content',
            'is_spoiler', 'helpful_count', 'unhelpful_count', 'is_verified_purchase',
            'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'helpful_count', 'unhelpful_count', 'created_at', 'updated_at']


class HighlightSerializer(serializers.ModelSerializer):
    """Serializer pour les surlignages."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Highlight
        fields = [
            'id', 'user_name', 'book', 'page_number', 'text', 'color',
            'location', 'note', 'is_private', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']





class NoteSerializer(serializers.ModelSerializer):
    """Serializer pour les notes personnelles."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'user_name', 'book', 'page_number', 'title', 'content',
            'tags', 'tags_list', 'is_pinned', 'is_private', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_tags_list(self, obj):
        """Convertir les tags en liste."""
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',')]
        return []

class RecommendationSerializer(serializers.Serializer):
    """Serializer pour les recommandations personnalisées."""
    
    book = BookDetailSerializer(read_only=True)
    reason = serializers.CharField(help_text="Raison de la recommandation")
    score = serializers.FloatField(help_text="Score de pertinence (0-100)")
    
    class Meta:
        fields = ['book', 'reason', 'score']


class TrendingBooksSerializer(serializers.Serializer):
    """Serializer pour les livres tendance."""
    
    book = BookDetailSerializer(read_only=True)
    trending_score = serializers.FloatField(help_text="Score de tendance")
    reads_count = serializers.IntegerField(help_text="Nombre de lectures récentes")
    
    class Meta:
        fields = ['book', 'trending_score', 'reads_count']


class BestRatedBooksSerializer(serializers.Serializer):
    """Serializer pour les meilleurs livres."""
    
    book = BookDetailSerializer(read_only=True)
    average_rating = serializers.FloatField(help_text="Note moyenne")
    rating_count = serializers.IntegerField(help_text="Nombre d'évaluations")
    
    class Meta:
        fields = ['book', 'average_rating', 'rating_count']

# Alias pour compatibilité
BookSerializer = BookDetailSerializer


# ==================== ANALYTICS AVANCÉES ====================
# NOTE: Les serializers ci-dessous dépendent de modèles non implémentés
# (UserAnalytics, UserAchievements) et seront activés à la Phase 10

"""
# Désactivé pour Phase 8
class UserAnalyticsSerializer(serializers.ModelSerializer):
    # Serializer pour les statistiques utilisateur
    pass

class UserAchievementsSerializer(serializers.ModelSerializer):
    # Serializer pour les accomplissements
    pass

class ReadingTrendsSerializer(serializers.Serializer):
    # Serializer pour les tendances de lecture
    pass

class GenreStatsSerializer(serializers.Serializer):
    # Serializer pour les statistiques par genre
    pass

class PreferenceStatsSerializer(serializers.Serializer):
    # Serializer pour les préférences utilisateur
    pass

class AchievementProgressSerializer(serializers.Serializer):
    # Serializer pour la progression des badges
    pass
"""


# ============================================================================
# PHASE 8: FORUM COMMUNAUTAIRE - SERIALIZERS
# ============================================================================

class ForumCategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories du forum."""
    discussion_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'order', 'is_active', 'discussion_count', 'comment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_discussion_count(self, obj):
        return obj.discussions.count()
    
    def get_comment_count(self, obj):
        """Compte le nombre total de commentaires dans cette catégorie."""
        comment_count = Comment.objects.filter(
            discussion__category=obj
        ).count()
        return comment_count


class VoteSerializer(serializers.ModelSerializer):
    """Serializer pour les votes."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'user', 'user_username', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires avec réponses imbriquées."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'discussion', 'author', 'author_username', 'author_avatar',
            'parent', 'content', 'upvotes_count', 'is_edited', 'is_answer',
            'replies', 'reply_count', 'user_vote',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'upvotes_count', 'is_edited', 'created_at', 'updated_at'
        ]
    
    def get_author_avatar(self, obj):
        """Retourner l'avatar de l'utilisateur s'il existe."""
        if hasattr(obj.author, 'profile_image') and obj.author.profile_image:
            return obj.author.profile_image.url
        return None
    
    def get_replies(self, obj):
        """Retourner les réponses imbriquées."""
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, read_only=True).data
    
    def get_reply_count(self, obj):
        return obj.replies.count()
    
    def get_user_vote(self, obj):
        """Retourner le vote de l'utilisateur actuel s'il existe."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            if vote:
                return VoteSerializer(vote).data
        return None


class DiscussionListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des discussions (résumé)."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = [
            'id', 'category', 'category_name', 'author', 'author_username',
            'title', 'status', 'views_count', 'comments_count', 'upvotes_count',
            'last_comment_at', 'user_vote', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'views_count', 'comments_count', 'upvotes_count',
            'last_comment_at', 'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        """Retourner le vote de l'utilisateur actuel."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            if vote:
                return VoteSerializer(vote).data
        return None


class DiscussionDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une discussion avec commentaires."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_vote = serializers.SerializerMethodField()
    user_can_edit = serializers.SerializerMethodField()
    user_can_close = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = [
            'id', 'category', 'category_name', 'author', 'author_username',
            'title', 'content', 'status', 'is_edited',
            'views_count', 'comments_count', 'upvotes_count',
            'comments', 'user_vote', 'user_can_edit', 'user_can_close',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'views_count', 'comments_count', 'upvotes_count',
            'is_edited', 'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            if vote:
                return VoteSerializer(vote).data
        return None
    
    def get_user_can_edit(self, obj):
        """Vérifier si l'utilisateur peut modifier la discussion."""
        request = self.context.get('request')
        return request and request.user == obj.author
    
    def get_user_can_close(self, obj):
        """Vérifier si l'utilisateur peut fermer la discussion."""
        request = self.context.get('request')
        return request and (request.user == obj.author or request.user.is_staff)


class ForumNotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications du forum."""
    discussion_title = serializers.CharField(
        source='discussion.title', read_only=True, allow_null=True
    )
    comment_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumNotification
        fields = [
            'id', 'user', 'discussion', 'discussion_title', 'comment',
            'comment_preview', 'notification_type', 'message', 'is_read',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at'
        ]
    
    def get_comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment.content[:100]
            if len(obj.comment.content) > 100:
                preview += "..."
            return preview
        return None


# ==================== PHASE 9: SÉRIALISEURS INTÉGRATION MÉDIA ====================

class PDFAnnotationSerializer(serializers.ModelSerializer):
    """Serializer pour les annotations PDF."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    annotation_type_display = serializers.CharField(source='get_annotation_type_display', read_only=True)
    
    class Meta:
        model = PDFAnnotation
        fields = [
            'id', 'user', 'user_name', 'book', 'book_title',
            'annotation_type', 'annotation_type_display',
            'page_number', 'x_start', 'y_start', 'x_end', 'y_end',
            'text', 'color', 'note_content', 'is_synced',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_name', 'book_title', 'created_at', 'updated_at']


class AudiobookChapterSerializer(serializers.ModelSerializer):
    """Serializer pour les chapitres audiobook."""
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = AudiobookChapter
        fields = [
            'id', 'audiobook', 'chapter_number', 'title',
            'duration_seconds', 'duration_minutes',
            'start_time', 'end_time', 'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration_minutes(self, obj):
        return round(obj.duration_seconds / 60, 2)


class AudiobookMetadataSerializer(serializers.ModelSerializer):
    """Serializer pour les métadonnées audiobook."""
    chapters = AudiobookChapterSerializer(many=True, read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    total_duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AudiobookMetadata
        fields = [
            'id', 'book', 'book_title', 'narrator',
            'duration_hours', 'total_duration_seconds',
            'bitrate', 'file_format', 'audio_file', 'cover_image',
            'is_published', 'chapters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'book_title', 'chapters', 'created_at', 'updated_at']
    
    def get_total_duration_seconds(self, obj):
        return obj.total_duration_seconds


class ListeningProgressSerializer(serializers.ModelSerializer):
    """Serializer pour la progression d'écoute audiobook."""
    audiobook_title = serializers.CharField(source='audiobook.book.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ListeningProgress
        fields = [
            'id', 'user', 'user_name', 'audiobook', 'audiobook_title',
            'current_chapter', 'current_time', 'total_time_listened',
            'completion_percentage', 'is_completed', 'last_listened_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'audiobook_title',
            'created_at', 'updated_at'
        ]


class VideoMaterialSerializer(serializers.ModelSerializer):
    """Serializer pour les matériaux vidéo."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    uploader_name = serializers.CharField(source='uploader.username', read_only=True, allow_null=True)
    video_type_display = serializers.CharField(source='get_video_type_display', read_only=True)
    
    class Meta:
        model = VideoMaterial
        fields = [
            'id', 'book', 'book_title', 'title', 'description',
            'video_type', 'video_type_display', 'video_file',
            'external_url', 'duration_seconds', 'thumbnail',
            'uploader', 'uploader_name', 'view_count',
            'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'uploader_name', 'video_type_display',
            'view_count', 'created_at', 'updated_at'
        ]


class VideoPlaybackSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique de lecture vidéo."""
    video_title = serializers.CharField(source='video.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = VideoPlayback
        fields = [
            'id', 'user', 'user_name', 'video', 'video_title',
            'current_time', 'completion_percentage', 'is_completed',
            'playback_count', 'last_played_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'video_title',
            'created_at', 'updated_at'
        ]


class PodcastEpisodeSerializer(serializers.ModelSerializer):
    """Serializer pour les épisodes podcast."""
    podcast_title = serializers.CharField(source='podcast.title', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = PodcastEpisode
        fields = [
            'id', 'podcast', 'podcast_title', 'episode_number',
            'title', 'description', 'duration_seconds', 'duration_minutes',
            'audio_url', 'pubdate', 'guid', 'is_explicit', 'created_at'
        ]
        read_only_fields = ['id', 'podcast_title', 'created_at']
    
    def get_duration_minutes(self, obj):
        return round(obj.duration_seconds / 60, 2)


class PodcastSerializer(serializers.ModelSerializer):
    """Serializer pour les podcasts."""
    episodes = PodcastEpisodeSerializer(many=True, read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True, allow_null=True)
    subscriptions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Podcast
        fields = [
            'id', 'book', 'book_title', 'title', 'description',
            'author', 'rss_feed_url', 'image_url', 'website_url',
            'language', 'episode_count', 'subscriptions_count',
            'is_active', 'last_synced_at', 'episodes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'subscriptions_count', 'episodes',
            'created_at', 'updated_at'
        ]
    
    def get_subscriptions_count(self, obj):
        return obj.subscriptions.filter(is_active=True).count()


class PodcastSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les abonnements podcast."""
    podcast_title = serializers.CharField(source='podcast.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PodcastSubscription
        fields = [
            'id', 'user', 'user_name', 'podcast', 'podcast_title',
            'is_active', 'notification_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'podcast_title',
            'created_at', 'updated_at'
        ]


class PodcastProgressSerializer(serializers.ModelSerializer):
    """Serializer pour la progression d'écoute podcast."""
    episode_title = serializers.CharField(source='episode.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PodcastProgress
        fields = [
            'id', 'user', 'user_name', 'episode', 'episode_title',
            'current_time', 'completion_percentage', 'is_completed',
            'playback_count', 'is_bookmarked', 'last_played_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'episode_title',
            'created_at', 'updated_at'
        ]


# ==================== PHASE 10: SÉRIALISEURS RECOMMANDATIONS ====================

class TrendingBookSerializer(serializers.ModelSerializer):
    """Serializer pour les livres en tendance."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover_image', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    
    class Meta:
        model = TrendingBook
        fields = [
            'id', 'book', 'book_title', 'book_cover',
            'period', 'period_display', 'rank',
            'reads_count', 'ratings_count', 'avg_rating',
            'purchases_count', 'trend_score', 'calculated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'book_cover', 'period_display',
            'calculated_at'
        ]


class UserRecommendationSerializer(serializers.ModelSerializer):
    """Serializer pour les recommandations utilisateur."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover_image', read_only=True)
    book_rating = serializers.FloatField(source='book.average_rating', read_only=True)
    book_author = serializers.CharField(source='book.primary_author', read_only=True)
    recommendation_type_display = serializers.CharField(
        source='get_recommendation_type_display', read_only=True
    )
    
    class Meta:
        model = UserRecommendation
        fields = [
            'id', 'user', 'book', 'book_title', 'book_cover',
            'book_rating', 'book_author', 'recommendation_type',
            'recommendation_type_display', 'score',
            'is_viewed', 'is_liked', 'is_purchased', 'is_read',
            'created_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'user', 'book_title', 'book_cover', 'book_rating',
            'book_author', 'recommendation_type_display', 'created_at'
        ]


class PersonalizedFeedSerializer(serializers.Serializer):
    """Serializer pour le feed personnalisé."""
    recommendations = UserRecommendationSerializer(many=True, read_only=True)
    trending = TrendingBookSerializer(many=True, read_only=True)
    similar_books = BookDetailSerializer(many=True, read_only=True)
    
    class Meta:
        fields = ['recommendations', 'trending', 'similar_books']


class RecommendationStatsSerializer(serializers.Serializer):
    """Statistiques sur les recommandations."""
    total_recommendations = serializers.IntegerField()
    viewed_recommendations = serializers.IntegerField()
    purchased_from_recommendations = serializers.IntegerField()
    average_recommendation_score = serializers.FloatField()
    most_common_type = serializers.CharField()
    conversion_rate = serializers.FloatField()


class SimilarBooksSerializer(serializers.Serializer):
    """Livres similaires avec score de similarité."""
    book = BookDetailSerializer(read_only=True)
    similarity_score = serializers.FloatField()
    reason = serializers.CharField()


class UserPreferenceSerializer(serializers.Serializer):
    """Préférences utilisateur."""
    favorite_genres = serializers.ListField(child=serializers.CharField())
    favorite_authors = serializers.ListField(child=serializers.CharField())
    preferred_languages = serializers.ListField(child=serializers.CharField())
    average_rating_given = serializers.FloatField()
    reading_frequency = serializers.CharField()
    book_preferences = serializers.DictField()

