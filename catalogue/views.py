"""API Views pour BNC - REST Framework"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Book, Author, Library, ReadingSession, Payment
from .serializers import (
    BookListSerializer, BookDetailSerializer, AuthorSerializer,
    LibrarySerializer, PaymentSerializer
)


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'language', 'is_paid']
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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['payment_status', 'payment_method']
    ordering_fields = ['payment_date', 'created_at']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        query = request.query_params.get('q', '').strip()
        types = request.query_params.get('type', 'book,author')
        search_types = types.split(',')
        
        if not query:
            return Response({'error': 'Parametre q requis'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        if 'book' in search_types:
            q = Q(title__icontains=query)
            q |= Q(description__icontains=query)
            q |= Q(isbn__icontains=query)
            books = Book.objects.filter(is_published=True).filter(q)[:10]
            results['books'] = BookListSerializer(books, many=True).data
        
        if 'author' in search_types:
            q = Q(first_name__icontains=query)
            q |= Q(last_name__icontains=query)
            q |= Q(biography__icontains=query)
            authors = Author.objects.filter(is_verified=True).filter(q)[:10]
            results['authors'] = AuthorSerializer(authors, many=True).data
        
        if 'library' in search_types:
            q = Q(name__icontains=query)
            q |= Q(city__icontains=query)
            libs = Library.objects.filter(is_active=True).filter(q)[:5]
            results['libraries'] = LibrarySerializer(libs, many=True).data
        
        total = sum(len(v) if isinstance(v, list) else 0 
                   for v in results.values())
        return Response({
            'query': query,
            'results': results,
            'total_results': total
        })
