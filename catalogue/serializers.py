"""
DRF Serializers pour BNC API
Sécurité DRM: N'inclut PAS les fichiers numériques (pdf_file, epub_file)
"""

from rest_framework import serializers
from .models import Author, AuthorMedia, Library, Book, AuthorBook, LibraryBook, Payment


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
        fields = ['id', 'author', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


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
        """Retourne la note moyenne (future implémentation)"""
        # Pour l'instant, retournez une valeur fictive
        # Cette logique sera améliorée lors de l'ajout du système de notations
        return 4.5


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
