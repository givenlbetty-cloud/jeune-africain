"""
ViewSets pour le Forum Communautaire - Phase 8
API endpoints pour discussions, commentaires, votes
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
import uuid

from .models import (
    ForumCategory, Discussion, Comment, Vote, ForumNotification
)
from .serializers import (
    ForumCategorySerializer, DiscussionListSerializer, DiscussionDetailSerializer,
    CommentSerializer, VoteSerializer, ForumNotificationSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination standard pour le forum."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permettre aux propriétaires de modifier leurs propres contenus."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Permettre la lecture anonyme, mais requérir l'authentification pour les modifications."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


# ==================== API VIEWSETS ====================

class ForumCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories du forum."""
    queryset = ForumCategory.objects.filter(is_active=True)
    serializer_class = ForumCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']


class DiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = ForumCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']
    ordering = ['order']
    
    def get_permissions(self):
        """Seul le staff peut créer/modifier les catégories."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    @action(detail=True, methods=['get'])
    def discussions(self, request, pk=None):
        """Retourner les discussions d'une catégorie."""
        category = self.get_object()
        discussions = category.discussions.annotate(
            comment_count_annotated=Count('comments')
        ).order_by('-created_at')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(discussions, request)
        if page is not None:
            serializer = DiscussionListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = DiscussionListSerializer(discussions, many=True, context={'request': request})
        return Response(serializer.data)


class DiscussionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les discussions."""
    queryset = Discussion.objects.select_related(
        'category', 'author'
    ).prefetch_related('comments', 'votes')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'category__name']
    ordering_fields = ['created_at', 'views_count', 'comments_count', 'upvotes_count']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Retourner le serializer approprié."""
        if self.action == 'retrieve':
            return DiscussionDetailSerializer
        return DiscussionListSerializer
    
    def get_queryset(self):
        """Filtrer les discussions par catégorie si spécifié."""
        queryset = super().get_queryset()
        
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par utilisateur si spécifié
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Incrémenter les vues lors de la consultation."""
        instance = self.get_object()
        instance.increment_views()
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Créer une discussion avec l'utilisateur actuel comme auteur."""
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        """Marquer comme modifié lors de la mise à jour."""
        # Vérifier que l'utilisateur est le propriétaire
        if self.request.user != serializer.instance.author and not self.request.user.is_staff:
            raise PermissionError("Vous ne pouvez modifier que vos propres discussions.")
        serializer.save(is_edited=True)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Fermer une discussion."""
        discussion = self.get_object()
        
        if request.user != discussion.author and not request.user.is_staff:
            return Response(
                {'detail': 'Vous ne pouvez fermer que vos propres discussions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        discussion.status = 'closed'
        discussion.save()
        
        return Response({'status': 'Discussion fermée.'})
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Épingler une discussion (staff only)."""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Seul le staff peut épingler une discussion.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        discussion = self.get_object()
        discussion.status = 'pinned'
        discussion.save()
        
        return Response({'status': 'Discussion épinglée.'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        """Upvoter une discussion."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentification requise.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        discussion = self.get_object()
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            discussion=discussion,
            defaults={'value': 1}
        )
        
        if not created:
            vote.value = 1
            vote.save()
        
        # Mettre à jour le compteur
        discussion.upvotes_count = discussion.votes.filter(value=1).count()
        discussion.save(update_fields=['upvotes_count'])
        
        return Response({'status': 'Discussion upvotée.'})
    
    @action(detail=True, methods=['post'])
    def remove_vote(self, request, pk=None):
        """Retirer le vote d'une discussion."""
        discussion = self.get_object()
        Vote.objects.filter(user=request.user, discussion=discussion).delete()
        
        discussion.upvotes_count = discussion.votes.filter(value=1).count()
        discussion.save(update_fields=['upvotes_count'])
        
        return Response({'status': 'Vote retiré.'})
    
    @action(detail=True, methods=['get'])
    def top_comments(self, request, pk=None):
        """Retourner les commentaires les plus upvotés."""
        discussion = self.get_object()
        comments = discussion.comments.filter(parent__isnull=True).order_by('-upvotes_count')[:5]
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commentaires."""
    queryset = Comment.objects.select_related(
        'discussion', 'author', 'parent'
    ).prefetch_related('replies', 'votes')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'upvotes_count']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Filtrer les commentaires par discussion."""
        queryset = super().get_queryset()
        
        discussion_id = self.request.query_params.get('discussion')
        if discussion_id:
            queryset = queryset.filter(discussion_id=discussion_id, parent__isnull=True)
        
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Créer un commentaire avec l'utilisateur actuel."""
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        """Marquer le commentaire comme modifié."""
        serializer.save(is_edited=True)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        """Upvoter un commentaire."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentification requise.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = self.get_object()
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'value': 1}
        )
        
        if not created:
            vote.value = 1
            vote.save()
        
        # Mettre à jour le compteur
        comment.upvotes_count = comment.votes.filter(value=1).count()
        comment.save(update_fields=['upvotes_count'])
        
        return Response({'status': 'Commentaire upvoté.'})
    
    @action(detail=True, methods=['post'])
    def remove_vote(self, request, pk=None):
        """Retirer le vote d'un commentaire."""
        comment = self.get_object()
        Vote.objects.filter(user=request.user, comment=comment).delete()
        
        comment.upvotes_count = comment.votes.filter(value=1).count()
        comment.save(update_fields=['upvotes_count'])
        
        return Response({'status': 'Vote retiré.'})
    
    @action(detail=True, methods=['post'])
    def mark_answer(self, request, pk=None):
        """Marquer un commentaire comme réponse acceptée."""
        comment = self.get_object()
        discussion = comment.discussion
        
        if request.user != discussion.author and not request.user.is_staff:
            return Response(
                {'detail': 'Seul l\'auteur peut marquer une réponse acceptée.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Retirer le marquage des autres commentaires
        discussion.comments.update(is_answer=False)
        
        # Marquer ce commentaire
        comment.is_answer = True
        comment.save()
        
        return Response({'status': 'Réponse acceptée.'})
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Créer une réponse à ce commentaire."""
        parent_comment = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(
            author=request.user,
            discussion=parent_comment.discussion,
            parent=parent_comment
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ForumNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les notifications du forum."""
    serializer_class = ForumNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'is_read']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Retourner uniquement les notifications de l'utilisateur actuel."""
        return ForumNotification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues."""
        ForumNotification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'status': 'Toutes les notifications ont été marquées comme lues.'})


# ==================== FRONTEND VIEWS ====================

def forum_categories_view(request):
    """Liste toutes les catégories de forum"""
    categories = ForumCategory.objects.filter(is_active=True).order_by('name')
    discussions = Discussion.objects.order_by('-created_at')[:10]
    
    context = {
        'categories': categories,
        'discussions': discussions,
    }
    
    return render(request, 'catalogue/forum_categories_list.html', context)


def forum_category_detail_view(request, category_id):
    """Détail d'une catégorie avec ses discussions"""
    category = get_object_or_404(ForumCategory, id=category_id, is_active=True)
    
    # Récupérer les discussions
    discussions = category.discussions.order_by('-updated_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(discussions, 20)
    page_obj = paginator.get_page(page)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'discussions': page_obj.object_list,
    }
    
    return render(request, 'catalogue/category_detail.html', context)


def forum_threads_view(request):
    """Liste toutes les discussions"""
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '-created_at')
    page = request.GET.get('page', 1)
    
    discussions = Discussion.objects.all()
    
    # Recherche
    if query:
        discussions = discussions.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    # Tri
    discussions = discussions.order_by(sort)
    
    # Pagination
    paginator = Paginator(discussions, 20)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'discussions': page_obj.object_list,
        'query': query,
        'sort': sort,
        'total_count': discussions.count(),
    }
    
    return render(request, 'catalogue/threads_list.html', context)


def forum_thread_detail_view(request, thread_id):
    """Détail d'une discussion avec ses commentaires"""
    discussion = get_object_or_404(Discussion, id=thread_id)
    
    # Incrémenter le compteur de vues
    discussion.views_count = (discussion.views_count or 0) + 1
    discussion.save(update_fields=['views_count'])
    
    # Récupérer les commentaires
    comments = discussion.comments.select_related('author').order_by('created_at')
    
    # Vérifier si l'utilisateur a voté
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(
            user=request.user,
            discussion=discussion
        ).first()
    
    # Pagination des commentaires
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'discussion': discussion,
        'page_obj': page_obj,
        'comments': page_obj.object_list,
        'user_vote': user_vote,
    }
    
    return render(request, 'catalogue/thread_detail.html', context)


@login_required
def create_forum_thread_view(request):
    """Créer une nouvelle discussion"""
    if request.method == 'GET':
        categories = ForumCategory.objects.filter(is_active=True)
        context = {'categories': categories}
        return render(request, 'catalogue/create_thread.html', context)
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        category_id = request.POST.get('category_id', '')
        
        if not title or not content or not category_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Tous les champs sont requis'
            })
        
        category = get_object_or_404(ForumCategory, id=category_id, is_active=True)
        
        discussion = Discussion.objects.create(
            id=uuid.uuid4(),
            title=title,
            content=content,
            author=request.user,
            category=category
        )
        
        return redirect('catalogue:forum_thread_detail', thread_id=discussion.id)


@login_required
def edit_forum_thread_view(request, thread_id):
    """Modifier une discussion"""
    discussion = get_object_or_404(Discussion, id=thread_id)
    
    # Vérifier que l'utilisateur est l'auteur
    if discussion.author != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Vous ne pouvez pas modifier cette discussion'
        }, status=403)
    
    if request.method == 'POST':
        discussion.title = request.POST.get('title', discussion.title)
        discussion.content = request.POST.get('content', discussion.content)
        discussion.updated_at = timezone.now()
        discussion.save()
        
        return redirect('catalogue:forum_thread_detail', thread_id=discussion.id)
    
    context = {'discussion': discussion}
    return render(request, 'catalogue/edit_thread.html', context)


@login_required
@require_http_methods(["POST"])
def delete_forum_thread_view(request, thread_id):
    """Supprimer une discussion"""
    discussion = get_object_or_404(Discussion, id=thread_id)
    
    # Vérifier que l'utilisateur est l'auteur ou modérateur
    if discussion.author != request.user and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Vous ne pouvez pas supprimer cette discussion'
        }, status=403)
    
    discussion.delete()
    return JsonResponse({'status': 'success'})


@login_required
def reply_to_thread_view(request, thread_id):
    """Ajouter un commentaire à une discussion"""
    discussion = get_object_or_404(Discussion, id=thread_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Le contenu est requis'
            })
        
        comment = Comment.objects.create(
            id=uuid.uuid4(),
            content=content,
            author=request.user,
            discussion=discussion
        )
        
        return redirect('catalogue:forum_thread_detail', thread_id=discussion.id)
    
    context = {'discussion': discussion}
    return render(request, 'catalogue/reply_form.html', context)


@login_required
def edit_forum_reply_view(request, reply_id):
    """Modifier un commentaire"""
    comment = get_object_or_404(Comment, id=reply_id)
    
    # Vérifier que l'utilisateur est l'auteur
    if comment.author != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Vous ne pouvez pas modifier ce commentaire'
        }, status=403)
    
    if request.method == 'POST':
        comment.content = request.POST.get('content', comment.content)
        comment.updated_at = timezone.now()
        comment.save()
        
        return redirect('catalogue:forum_thread_detail', thread_id=comment.discussion.id)
    
    context = {'comment': comment}
    return render(request, 'catalogue/edit_reply.html', context)


@login_required
@require_http_methods(["POST"])
def delete_forum_reply_view(request, reply_id):
    """Supprimer un commentaire"""
    comment = get_object_or_404(Comment, id=reply_id)
    
    # Vérifier que l'utilisateur est l'auteur ou modérateur
    if comment.author != request.user and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Vous ne pouvez pas supprimer ce commentaire'
        }, status=403)
    
    discussion_id = comment.discussion.id
    comment.delete()
    
    return JsonResponse({'status': 'success', 'discussion_id': str(discussion_id)})


@login_required
@require_http_methods(["POST"])
def vote_thread_view(request, thread_id):
    """Voter pour/contre une discussion"""
    discussion = get_object_or_404(Discussion, id=thread_id)
    raw_vote_type = request.POST.get('vote_type', 'upvote')  # upvote ou downvote
    
    # Mapper le type de vote vers la valeur numérique (-1, 0, 1)
    value = 1 if raw_vote_type == 'upvote' else -1
    
    vote, created = Vote.objects.get_or_create(
        user=request.user,
        discussion=discussion,
        defaults={'value': value}
    )
    
    current_vote_state = None
    
    if not created:
        if vote.value == value:
            # Si on clique à nouveau sur le même vote, on l'annule (toggle)
            vote.delete()
            current_vote_state = None
        else:
            # Sinon on change la valeur
            vote.value = value
            vote.save()
            current_vote_state = raw_vote_type
    else:
        current_vote_state = raw_vote_type
    
    # Recalculer le total des votes
    total = discussion.votes.aggregate(total=Sum('value'))['total'] or 0
    
    return JsonResponse({
        'status': 'success',
        'vote_type': current_vote_state,
        'total_votes': total
    })


@login_required
@require_http_methods(["POST"])
def vote_reply_view(request, reply_id):
    """Voter pour/contre un commentaire"""
    comment = get_object_or_404(Comment, id=reply_id)
    vote_type = request.POST.get('vote_type', 'upvote')
    
    vote, created = Vote.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'vote_type': vote_type, 'content_type': 'comment'}
    )
    
    if not created:
        if vote.vote_type == vote_type:
            vote.delete()
            vote_type = None
        else:
            vote.vote_type = vote_type
            vote.save()
    
    return JsonResponse({
        'status': 'success',
        'vote_type': vote_type,
        'total_votes': comment.votes.count()
    })


# ==================== API VIEWS ====================

@require_http_methods(["GET"])
def forum_api_view(request):
    """API pour récupérer les discussions"""
    discussions = Discussion.objects.values(
        'id', 'title', 'author__username', 'created_at'
    ).annotate(
        comment_count=Count('comments'),
        vote_count=Count('votes')
    )
    
    return JsonResponse({
        'count': discussions.count(),
        'results': list(discussions)
    })


@require_http_methods(["GET"])
def forum_categories_api_view(request):
    """API pour récupérer les catégories"""
    categories = ForumCategory.objects.filter(is_active=True).values(
        'id', 'name', 'description'
    ).annotate(
        discussion_count=Count('discussions')
    )
    
    return JsonResponse({
        'count': categories.count(),
        'results': list(categories)
    })

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'Notification marquée comme lue.'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Retourner le nombre de notifications non lues."""
        count = ForumNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})
