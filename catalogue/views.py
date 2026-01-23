"""API Views pour BNC - REST Framework"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
# from django_filters.rest_framework import DjangoFilterBackend  # Temporarily disabled
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone

from .models import (
    Book, Author, Library, ReadingSession, Payment, Review, Highlight, Note,
    TrendingBook, UserRecommendation
)
from .serializers import (
    BookListSerializer, BookDetailSerializer, AuthorSerializer,
    LibrarySerializer, PaymentSerializer, PurchaseBookSerializer, PaymentDetailSerializer,
    ReviewSerializer, HighlightSerializer, NoteSerializer,
    RecommendationSerializer, TrendingBooksSerializer, BestRatedBooksSerializer
)
from .recommendations import get_user_recommendations


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'isbn']
    ordering_fields = ['title', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def read(self, request, pk=None):
        try:
            book = self.get_object()
        except Book.DoesNotExist:
            return Response({'error': 'Livre non trouve'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        if book.is_paid:
            payment = Payment.objects.filter(
                user=request.user, book=book, 
                payment_status='COMPLETED'
            ).exists()
            if not payment:
                return Response({
                    'error': 'Livre payant - Acces refuse',
                    'book_id': str(book.id),
                    'price': book.price
                }, status=status.HTTP_403_FORBIDDEN)
        
        session, created = ReadingSession.objects.get_or_create(
            user=request.user, book=book, 
            defaults={'current_page': 1}
        )
        if not created:
            session.sessions_count += 1
            session.save()
        
        return Response({
            'book': BookDetailSerializer(book).data,
            'access_type': 'free' if not book.is_paid else 'premium',
            'reading_session_id': str(session.id)
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def recommendations(self, request):
        """
        Obtenir les recommandations personnalisées.
        
        GET /api/books/recommendations/?limit=10
        
        Si l'utilisateur est authentifié: recommandations personnalisées
        Sinon: livres tendance
        """
        limit = int(request.query_params.get('limit', 10))
        
        if request.user.is_authenticated:
            # Recommandations personnalisées basées sur l'historique
            recommended_books = get_user_recommendations(request.user, limit=limit)
            return Response({
                'type': 'personalized',
                'books': BookDetailSerializer(recommended_books, many=True).data,
                'count': len(recommended_books)
            })
        else:
            # Livres tendance pour les utilisateurs anonymes
            trending_books = Book.objects.filter(
                is_published=True
            ).order_by('-rating', '-rating_count')[:limit]
            return Response({
                'type': 'trending',
                'books': BookDetailSerializer(trending_books, many=True).data,
                'count': trending_books.count()
            })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def trending(self, request):
        """
        Obtenir les livres tendance actuels.
        
        GET /api/books/trending/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        days = int(request.query_params.get('days', 30))
        
        from django.utils import timezone
        from datetime import timedelta
        
        recent_reads = ReadingSession.objects.filter(
            start_time__gte=timezone.now() - timedelta(days=days)
        ).values('book_id').annotate(
            reads_count=Count('id')
        ).order_by('-reads_count')[:limit]
        
        book_ids = [r['book_id'] for r in recent_reads]
        books = Book.objects.filter(id__in=book_ids)
        
        return Response({
            'type': 'trending',
            'period_days': days,
            'books': BookDetailSerializer(books, many=True).data,
            'count': len(book_ids)
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def best_rated(self, request):
        """
        Obtenir les meilleurs livres selon les notes.
        
        GET /api/books/best_rated/?limit=10&min_rating=3.5
        """
        limit = int(request.query_params.get('limit', 10))
        min_rating = float(request.query_params.get('min_rating', 3.5))
        
        best_books = Book.objects.filter(
            is_published=True,
            rating__gte=min_rating,
            rating_count__gte=5  # Au moins 5 évaluations
        ).order_by('-rating', '-rating_count')[:limit]
        
        return Response({
            'type': 'best_rated',
            'minimum_rating': min_rating,
            'books': BookDetailSerializer(best_books, many=True).data,
            'count': best_books.count()
        })


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.filter(is_verified=True)
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'biography']
    ordering_fields = ['first_name', 'created_at']
    ordering = ['first_name']
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def books(self, request, pk=None):
        try:
            author = self.get_object()
        except Author.DoesNotExist:
            return Response({'error': 'Auteur non trouve'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        books = author.book_set.filter(is_published=True)
        return Response({
            'author': AuthorSerializer(author).data,
            'books': BookListSerializer(books, many=True).data,
            'total': books.count()
        })


class LibraryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Library.objects.filter(is_active=True)
    serializer_class = LibrarySerializer
    permission_classes = [AllowAny]
    search_fields = ['name', 'city', 'country']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def books(self, request, pk=None):
        try:
            library = self.get_object()
        except Library.DoesNotExist:
            return Response({'error': 'Bibliotheque non trouvee'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        books = library.books.filter(is_published=True)
        return Response({
            'library': LibrarySerializer(library).data,
            'books': BookListSerializer(books, many=True).data,
            'total': books.count()
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['payment_date', 'created_at']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        Recherche avancée avec filtres.
        
        GET /api/search/?q=harry&type=book,author
        GET /api/search/?q=&publisher=Penguin&country=US
        GET /api/search/?author=Rowling&genre=fantasy
        """
        query = request.query_params.get('q', '').strip()
        types = request.query_params.get('type', 'book,author')
        search_types = types.split(',')
        
        # Filtres avancés
        publisher = request.query_params.get('publisher', '').strip()
        country = request.query_params.get('country', '').strip()
        author = request.query_params.get('author', '').strip()
        genre = request.query_params.get('genre', '').strip()
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        language = request.query_params.get('language', '').strip()
        
        results = {}
        
        if 'book' in search_types:
            # Filtres de base
            q = Q(is_published=True)
            
            if query:
                q &= (Q(title__icontains=query) | 
                      Q(description__icontains=query) | 
                      Q(isbn__icontains=query))
            
            # Filtres avancés
            if publisher:
                q &= Q(publisher__icontains=publisher)
            if country:
                q &= Q(country_origin__icontains=country)
            if author:
                q &= Q(authors__first_name__icontains=author) | Q(authors__last_name__icontains=author)
            if genre:
                q &= Q(genre=genre)
            if language:
                q &= Q(language=language)
            if min_price:
                try:
                    q &= Q(price__gte=float(min_price))
                except ValueError:
                    pass
            if max_price:
                try:
                    q &= Q(price__lte=float(max_price))
                except ValueError:
                    pass
            
            books = Book.objects.filter(q).distinct()[:20]
            results['books'] = BookListSerializer(books, many=True).data
            results['books_count'] = books.count()
        
        if 'author' in search_types:
            q = Q(is_verified=True)
            
            if query:
                q &= (Q(first_name__icontains=query) | 
                      Q(last_name__icontains=query) | 
                      Q(biography__icontains=query))
            
            if country:
                q &= Q(nationality__icontains=country)
            
            authors = Author.objects.filter(q).distinct()[:10]
            results['authors'] = AuthorSerializer(authors, many=True).data
            results['authors_count'] = authors.count()
        
        if 'library' in search_types:
            q = Q(is_active=True)
            
            if query:
                q &= (Q(name__icontains=query) | 
                      Q(city__icontains=query))
            
            if country:
                q &= Q(country__icontains=country)
            
            libs = Library.objects.filter(q).distinct()[:5]
            results['libraries'] = LibrarySerializer(libs, many=True).data
            results['libraries_count'] = libs.count()
        
        total = sum(v for k, v in results.items() if k.endswith('_count'))
        
        return Response({
            'query': query,
            'filters': {
                'publisher': publisher,
                'country': country,
                'author': author,
                'genre': genre,
                'language': language,
                'price_range': [min_price, max_price] if min_price or max_price else None
            },
            'results': results,
            'total_results': total
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def publishers(self, request):
        """Lister tous les éditeurs uniques"""
        publishers = Book.objects.filter(
            is_published=True,
            publisher__isnull=False
        ).exclude(publisher__exact='').values_list('publisher', flat=True).distinct().order_by('publisher')
        
        return Response({
            'publishers': list(publishers),
            'count': len(list(publishers))
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def countries(self, request):
        """Lister tous les pays d'origine uniques"""
        countries = Book.objects.filter(
            is_published=True,
            country_origin__isnull=False
        ).exclude(country_origin__exact='').values_list('country_origin', flat=True).distinct().order_by('country_origin')
        
        return Response({
            'countries': list(countries),
            'count': len(list(countries))
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def author_countries(self, request):
        """Lister tous les pays d'origine des auteurs"""
        countries = Author.objects.filter(
            is_verified=True
        ).exclude(nationality__exact='').values_list('nationality', flat=True).distinct().order_by('nationality')
        
        return Response({
            'countries': list(countries),
            'count': len(list(countries))
        })


# ============================================================================
# API D'ACHAT DE LIVRES
# ============================================================================

class PurchaseBookView(APIView):
    """
    Endpoint pour l'achat de livres
    POST /api/purchase/
    
    Règles de sécurité:
    - Authentification requise (READER)
    - Un utilisateur peut acheter n'importe quel livre
    - Crée un enregistrement Payment avec le statut "pending"
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Acheter un livre
        
        Body:
        {
            "book_id": "uuid-du-livre"
        }
        
        Response:
        {
            "id": "uuid-du-paiement",
            "book": {...},
            "amount": 15000.00,
            "currency": "CDF",
            "status": "pending",
            "transaction_id": "TXN_12345",
            "message": "Paiement en attente. Veuillez procéder au paiement."
        }
        """
        serializer = PurchaseBookSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer le livre
            book = Book.objects.get(id=serializer.validated_data['book_id'])
            
            # Vérifier que l'utilisateur n'a pas déjà acheté ce livre
            existing_payment = Payment.objects.filter(
                user=request.user,
                book=book,
                status__in=['completed', 'processing']
            ).exists()
            
            if existing_payment:
                return Response(
                    {"error": "Vous avez déjà acheté ce livre."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculer le prix final (avec réduction si applicable)
            final_price = book.get_final_price() if hasattr(book, 'get_final_price') else float(book.price)
            
            # Générer un ID de transaction unique
            import uuid
            transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            
            # Créer le paiement avec statut "pending"
            payment = Payment.objects.create(
                user=request.user,
                book=book,
                amount=final_price,
                currency="CDF",
                transaction_id=transaction_id,
                status="pending",
                payment_method="pending"  # Sera défini lors de la confirmation du paiement
            )
            
            # Sérialiser et retourner
            payment_serializer = PaymentDetailSerializer(payment)
            
            return Response(
                {
                    **payment_serializer.data,
                    "message": "Paiement en attente. Veuillez procéder au paiement."
                },
                status=status.HTTP_201_CREATED
            )
            
        except Book.DoesNotExist:
            return Response(
                {"error": "Le livre n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la création du paiement: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(APIView):
    """
    Endpoint pour voir l'historique des paiements
    GET /api/payment-history/
    
    Retourne uniquement les paiements de l'utilisateur authentifié
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Récupérer l'historique des paiements de l'utilisateur
        
        Query params (optionnel):
        - status: pending, completed, failed, refunded
        - page: numéro de page (défaut: 1)
        
        Response:
        {
            "count": 5,
            "next": null,
            "previous": null,
            "results": [...]
        }
        """
        # Récupérer les paiements de l'utilisateur
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        
        # Filtrer par statut si fourni
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_payments = paginator.paginate_queryset(payments, request)
        
        serializer = PaymentDetailSerializer(paginated_payments, many=True)
        return paginator.get_paginated_response(serializer.data)


class PaymentStatusView(APIView):
    """
    Endpoint pour vérifier le statut d'un paiement
    GET /api/payment/{payment_id}/status/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id):
        """
        Récupérer le statut d'un paiement
        
        Response:
        {
            "id": "uuid",
            "status": "pending|completed|failed|refunded",
            "amount": 15000.00,
            "book": {...},
            "created_at": "2025-12-05T10:30:00Z"
        }
        """
        try:
            # Vérifier que le paiement appartient à l'utilisateur
            payment = Payment.objects.get(id=payment_id, user=request.user)
            serializer = PaymentDetailSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Paiement non trouvé ou accès refusé."},
                status=status.HTTP_404_NOT_FOUND
            )


# ===================================
# API ViewSets - Phase 2
# ===================================

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les critiques de livres.
    
    GET /api/reviews/ - Lister les critiques
    POST /api/reviews/ - Créer une critique (auth requise)
    GET /api/reviews/{id}/ - Détail critique
    PUT /api/reviews/{id}/ - Modifier (prop. seulement)
    DELETE /api/reviews/{id}/ - Supprimer (prop. seulement)
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['rating', 'created_at', 'helpful_count']
    ordering = ['-helpful_count', '-created_at']
    
    def get_queryset(self):
        """
        - GET: Afficher les critiques publiées sauf si c'est l'auteur
        - POST/PUT/DELETE: Seulement les critiques de l'utilisateur
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        """Assigner l'utilisateur courant."""
        serializer.save(user=self.request.user)


class HighlightViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les surlignages.
    
    GET /api/highlights/?book={book_id} - Surlignages du livre
    POST /api/highlights/ - Créer surlignage
    PUT /api/highlights/{id}/ - Modifier
    DELETE /api/highlights/{id}/ - Supprimer
    """
    serializer_class = HighlightSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['page_number', 'created_at']
    ordering = ['page_number', '-created_at']
    
    def get_queryset(self):
        """Seulement les surlignages de l'utilisateur (ou non-privés)."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return Highlight.objects.filter(user=self.request.user)
        
        return Highlight.objects.filter(is_private=False) | Highlight.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Assigner l'utilisateur courant."""
        serializer.save(user=self.request.user)





class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les notes personnelles.
    
    GET /api/notes/?book={book_id} - Notes du livre
    POST /api/notes/ - Créer note
    PUT /api/notes/{id}/ - Modifier
    DELETE /api/notes/{id}/ - Supprimer
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['is_pinned', 'created_at', 'updated_at']
    ordering = ['-is_pinned', '-created_at']
    
    def get_queryset(self):
        """Seulement les notes de l'utilisateur."""
        return Note.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Assigner l'utilisateur courant."""
        serializer.save(user=self.request.user)


# ==================== ANALYTICS AVANCÉES ====================
# NOTE: UserAnalytics et UserAchievements ne sont pas encore implémentés
# Ces ViewSets seront activés à la Phase 10 (Performance & Analytics)



# ==================== PHASE 9: VIEWSETS INTÉGRATION MÉDIA ====================

from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    PDFAnnotation, AudiobookMetadata, ListeningProgress,
    VideoMaterial, VideoPlayback, Podcast,
    PodcastSubscription, PodcastProgress, PodcastEpisode
)
from .serializers import (
    PDFAnnotationSerializer, AudiobookMetadataSerializer,
    ListeningProgressSerializer, VideoMaterialSerializer,
    VideoPlaybackSerializer, PodcastSerializer,
    PodcastSubscriptionSerializer, PodcastProgressSerializer,
    PodcastEpisodeSerializer
)


class PDFAnnotationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les annotations PDF."""
    serializer_class = PDFAnnotationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'note_content', 'book__title']
    ordering_fields = ['created_at', 'page_number', 'annotation_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = PDFAnnotation.objects.all()
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_annotations(self, request):
        """Récupérer les annotations de l'utilisateur connecté."""
        annotations = PDFAnnotation.objects.filter(user=request.user)
        serializer = self.get_serializer(annotations, many=True)
        return Response(serializer.data)


class AudiobookMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les métadonnées audiobook."""
    queryset = AudiobookMetadata.objects.all()
    serializer_class = AudiobookMetadataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['book__title', 'narrator', 'author']
    ordering_fields = ['created_at', 'duration_hours']
    ordering = ['-created_at']


class ListeningProgressViewSet(viewsets.ModelViewSet):
    """ViewSet pour la progression d'écoute audiobook."""
    serializer_class = ListeningProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'completion_percentage']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return ListeningProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Récupérer les audiobooks en cours d'écoute."""
        progress = ListeningProgress.objects.filter(
            user=request.user, is_completed=False
        )
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Récupérer les audiobooks complétés."""
        progress = ListeningProgress.objects.filter(
            user=request.user, is_completed=True
        )
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)


class VideoMaterialViewSet(viewsets.ModelViewSet):
    """ViewSet pour les matériaux vidéo."""
    serializer_class = VideoMaterialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'book__title']
    ordering_fields = ['created_at', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = VideoMaterial.objects.all()
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        video_type = self.request.query_params.get('video_type')
        if video_type:
            queryset = queryset.filter(video_type=video_type)
        is_published = self.request.query_params.get('is_published')
        if is_published:
            queryset = queryset.filter(is_published=is_published == 'true')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Incrémenter le nombre de vues."""
        video = self.get_object()
        video.view_count += 1
        video.save()
        return Response({'view_count': video.view_count})


class VideoPlaybackViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'historique de lecture vidéo."""
    serializer_class = VideoPlaybackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'completion_percentage']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return VideoPlayback.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def watching(self, request):
        """Récupérer les vidéos en cours de lecture."""
        playback = VideoPlayback.objects.filter(
            user=request.user, is_completed=False
        )
        serializer = self.get_serializer(playback, many=True)
        return Response(serializer.data)


class PodcastViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les podcasts."""
    queryset = Podcast.objects.filter(is_active=True)
    serializer_class = PodcastSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'author']
    ordering_fields = ['created_at', 'episode_count']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def sync_episodes(self, request, pk=None):
        """Synchroniser les épisodes depuis le flux RSS."""
        podcast = self.get_object()
        podcast.last_synced_at = timezone.now()
        podcast.save()
        return Response({'status': 'syncing'})


class PodcastSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les abonnements podcast."""
    serializer_class = PodcastSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'is_active']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return PodcastSubscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Récupérer les abonnements actifs."""
        subscriptions = PodcastSubscription.objects.filter(
            user=request.user, is_active=True
        )
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)


class PodcastProgressViewSet(viewsets.ModelViewSet):
    """ViewSet pour la progression d'écoute podcast."""
    serializer_class = PodcastProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'completion_percentage']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return PodcastProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def bookmarked(self, request):
        """Récupérer les épisodes marqués."""
        progress = PodcastProgress.objects.filter(
            user=request.user, is_bookmarked=True
        )
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)



# ==================== PHASE 10: VIEWSETS RECOMMANDATIONS ====================

from .models import TrendingBook, UserRecommendation
from .serializers import (
    TrendingBookSerializer, UserRecommendationSerializer,
    PersonalizedFeedSerializer, RecommendationStatsSerializer,
    SimilarBooksSerializer, UserPreferenceSerializer
)


class TrendingBooksViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les livres en tendance."""
    serializer_class = TrendingBookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['book__title', 'book__description']
    ordering_fields = ['rank', 'trend_score', 'calculated_at']
    ordering = ['rank']
    
    def get_queryset(self):
        period = self.request.query_params.get('period', '7d')
        queryset = TrendingBook.objects.filter(period=period)
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Tendances des dernières 24 heures."""
        trending = TrendingBook.objects.filter(period='1d').order_by('rank')[:10]
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def week(self, request):
        """Tendances de la semaine."""
        trending = TrendingBook.objects.filter(period='7d').order_by('rank')[:20]
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def month(self, request):
        """Tendances du mois."""
        trending = TrendingBook.objects.filter(period='30d').order_by('rank')[:50]
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)


class UserRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les recommandations utilisateur."""
    serializer_class = UserRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['score', 'created_at']
    ordering = ['-score']
    
    def get_queryset(self):
        return UserRecommendation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Marquer une recommandation comme consultée."""
        recommendation = self.get_object()
        recommendation.is_viewed = True
        recommendation.save()
        return Response({'status': 'marked as viewed'})
    
    @action(detail=True, methods=['post'])
    def mark_liked(self, request, pk=None):
        """Marquer une recommandation comme aimée."""
        recommendation = self.get_object()
        recommendation.is_liked = not recommendation.is_liked
        recommendation.save()
        return Response({'is_liked': recommendation.is_liked})
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Récupérer les recommandations par type."""
        rec_type = request.query_params.get('type')
        if rec_type:
            recommendations = UserRecommendation.objects.filter(
                user=request.user, recommendation_type=rec_type
            )
        else:
            recommendations = UserRecommendation.objects.filter(user=request.user)
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Recommandations les plus appréciées."""
        recommendations = UserRecommendation.objects.filter(
            user=request.user, is_liked=True
        ).order_by('-score')[:20]
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques sur les recommandations."""
        user_recs = UserRecommendation.objects.filter(user=request.user)
        total = user_recs.count()
        viewed = user_recs.filter(is_viewed=True).count()
        purchased = user_recs.filter(is_purchased=True).count()
        liked = user_recs.filter(is_liked=True).count()
        
        stats = {
            'total_recommendations': total,
            'viewed_recommendations': viewed,
            'purchased_from_recommendations': purchased,
            'liked_recommendations': liked,
            'average_recommendation_score': round(
                user_recs.aggregate(Avg('score'))['score__avg'] or 0, 2
            ),
            'conversion_rate': round((purchased / total * 100) if total > 0 else 0, 2),
            'types': list(user_recs.values('recommendation_type').annotate(
                count=Count('id')
            ))
        }
        return Response(stats)


class PersonalizedFeedViewSet(viewsets.ViewSet):
    """ViewSet pour le feed personnalisé."""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Récupérer le feed personnalisé complet."""
        user = request.user
        
        # Récupérer les recommandations
        recommendations = UserRecommendation.objects.filter(
            user=user, is_viewed=False
        ).order_by('-score')[:10]
        
        # Récupérer les tendances
        trending = TrendingBook.objects.filter(period='7d').order_by('rank')[:5]
        
        # Livres similaires (basé sur les lectures récentes)
        recent_reads = ReadingSession.objects.filter(
            user=user
        ).values_list('book_id', flat=True)[:5]
        
        similar_books = Book.objects.filter(
            category__in=Book.objects.filter(id__in=recent_reads).values('category')
        ).exclude(id__in=recent_reads)[:5]
        
        data = {
            'recommendations': UserRecommendationSerializer(
                recommendations, many=True
            ).data,
            'trending': TrendingBookSerializer(trending, many=True).data,
            'similar_books': BookDetailSerializer(similar_books, many=True).data,
        }
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def preferences(self, request):
        """Récupérer les préférences de l'utilisateur."""
        user = request.user
        
        # Genres favoris
        favorite_genres = Book.objects.filter(
            reads__user=user
        ).values_list('category__name', flat=True).distinct()
        
        # Auteurs favoris
        favorite_authors = Author.objects.filter(
            books__reads__user=user
        ).values_list('first_name', 'last_name').distinct()
        
        # Notes moyennes
        avg_rating = Review.objects.filter(user=user).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        data = {
            'favorite_genres': list(favorite_genres),
            'favorite_authors': [f"{f} {l}" for f, l in favorite_authors],
            'average_rating_given': round(avg_rating, 2),
            'total_books_read': ReadingSession.objects.filter(user=user).count(),
            'total_reviews': Review.objects.filter(user=user).count(),
        }
        return Response(data)


class SimilarBooksViewSet(viewsets.ViewSet):
    """ViewSet pour les livres similaires."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def retrieve(self, request, pk=None):
        """Récupérer les livres similaires à un livre."""
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Livre non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Trouver les livres similaires (même catégorie, même auteur, notes similaires)
        similar = Book.objects.filter(
            Q(category=book.category) |
            Q(authors=book.primary_author) |
            Q(average_rating__gte=book.average_rating - 0.5,
              average_rating__lte=book.average_rating + 0.5)
        ).exclude(id=book.id).distinct()[:10]
        
        serializer = SimilarBooksSerializer(
            [{'book': s, 'similarity_score': 0.8, 'reason': 'Similar category'}
             for s in similar],
            many=True
        )
        return Response(serializer.data)

