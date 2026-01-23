"""
Vues personnalisées pour l'administration avec dashboards.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta
from .models import Book, Library, ReadingSession, Payment, Author, Category, ReaderActivity
from users.models import CustomUser
from .stats import DashboardSummary


@staff_member_required
def admin_dashboard(request):
    """Dashboard administrateur avec statistiques clés."""
    
    # Obtenir les données de résumé
    summary = DashboardSummary.get_summary()
    
    # Statistiques en temps réel
    context = {
        'summary': summary,
        'page_title': 'Dashboard Administrateur',
        
        # KPI cartes
        'total_users': summary['users']['total'],
        'active_users': summary['users']['active'],
        'total_books': summary['books']['total'],
        'published_books': summary['books']['published'],
        'total_libraries': summary['libraries']['total'],
        'active_libraries': summary['libraries']['active'],
        
        # Graphiques
        'books_by_genre': summary['books']['by_genre'],
        'users_by_subscription': summary['users']['by_subscription'],
        'payments_by_method': summary['payments']['by_method'],
        'activities_by_type': summary['activity']['by_type'],
        
        # Listes
        'most_read_books': summary['books']['most_read'],
        'prolific_authors': summary['authors']['prolific'],
        'recent_users_count': summary['users']['recent'],
        'new_users_count': summary['users']['new'],
        
        # Données financières
        'total_revenue': summary['payments']['total_revenue'],
        'reading_sessions': summary['reading']['total_sessions'],
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def reader_statistics(request):
    """Statistiques détaillées des lecteurs."""
    
    # Lecteurs actifs vs inactifs
    active_readers = CustomUser.objects.filter(is_active=True).count()
    inactive_readers = CustomUser.objects.filter(is_active=False).count()
    
    # Lecteurs par statut d'abonnement
    subscription_stats = CustomUser.objects.values('subscription_status').annotate(
        count=Count('id')
    )
    
    # Lecteurs nouvellement inscrits (7 jours)
    new_readers = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Lecteurs actifs (connectés dans les 7 jours)
    active_recent = CustomUser.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Lecteurs par rôle
    by_role = CustomUser.objects.values('role').annotate(count=Count('id'))
    
    context = {
        'page_title': 'Statistiques des Lecteurs',
        'active_readers': active_readers,
        'inactive_readers': inactive_readers,
        'new_readers': new_readers,
        'active_recent': active_recent,
        'subscription_stats': list(subscription_stats),
        'by_role': list(by_role),
    }
    
    return render(request, 'admin/reader_statistics.html', context)


@staff_member_required
def book_statistics(request):
    """Statistiques détaillées des livres."""
    
    # Livres publiés vs non publiés
    published = Book.objects.filter(is_published=True).count()
    unpublished = Book.objects.filter(is_published=False).count()
    
    # Livres gratuits vs payants
    free = Book.objects.filter(is_paid=False).count()
    paid = Book.objects.filter(is_paid=True).count()
    
    # Livres par catégorie
    by_category = Category.objects.annotate(
        book_count=Count('books')
    ).values('name', 'book_count').order_by('-book_count')
    
    # Livres par langue
    by_language = Book.objects.values('language').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Livres par genre
    by_genre = Book.objects.values('genre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Top livres lus
    top_read = Book.objects.all().order_by('-reads_count')[:5]
    
    # Top livres téléchargés
    top_downloaded = Book.objects.all().order_by('-downloads_count')[:5]
    
    # Statistiques de prix
    price_stats = Book.objects.filter(is_paid=True).aggregate(
        avg_price=Avg('price'),
        min_price=Min('price'),
        max_price=Max('price'),
        total_price=Sum('price'),
    )
    
    context = {
        'page_title': 'Statistiques des Livres',
        'published': published,
        'unpublished': unpublished,
        'free': free,
        'paid': paid,
        'by_category': list(by_category),
        'by_language': list(by_language),
        'by_genre': list(by_genre),
        'top_read': top_read,
        'top_downloaded': top_downloaded,
        'price_stats': price_stats,
    }
    
    return render(request, 'admin/book_statistics.html', context)


@staff_member_required
def activity_statistics(request):
    """Statistiques d'activité."""
    
    # Activités par type
    activities_by_type = ReaderActivity.objects.values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Activités des 7 derniers jours
    recent_date = timezone.now() - timedelta(days=7)
    recent_activities = ReaderActivity.objects.filter(
        timestamp__gte=recent_date
    ).count()
    
    # Livres les plus populaires
    popular_books = ReaderActivity.objects.values(
        'book__title', 'book__id'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Sessions de lecture
    reading_sessions = ReadingSession.objects.count()
    completed_sessions = ReadingSession.objects.filter(is_completed=True).count()
    
    context = {
        'page_title': 'Statistiques d\'Activité',
        'activities_by_type': list(activities_by_type),
        'recent_activities': recent_activities,
        'popular_books': list(popular_books),
        'reading_sessions': reading_sessions,
        'completed_sessions': completed_sessions,
    }
    
    return render(request, 'admin/activity_statistics.html', context)


"""
Vues d'import/export en masse
"""

import json
import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from tablib import Dataset


@staff_member_required
@require_http_methods(["GET", "POST"])
def import_data(request):
    """Interface d'import de données en masse."""
    from .imports import RESOURCES  # Import local pour éviter les imports circulaires
    
    if request.method == 'POST':
        resource_type = request.POST.get('resource_type')
        import_format = request.POST.get('format', 'csv')
        file_obj = request.FILES.get('import_file')
        
        if not file_obj or not resource_type:
            messages.error(request, 'Sélectionnez un type de ressource et un fichier')
            return redirect('import_data')
        
        try:
            # Charger le fichier
            imported_data = Dataset()
            content = file_obj.read().decode('utf-8-sig')
            
            if import_format == 'csv':
                imported_data.load(content, 'csv')
            elif import_format == 'json':
                imported_data.load(content, 'json')
            elif import_format == 'yaml':
                imported_data.load(content, 'yaml')
            else:
                raise ValueError(f"Format non supporté: {import_format}")
            
            # Importer les données
            if resource_type in RESOURCES:
                resource = RESOURCES[resource_type]()
                result = resource.import_data(imported_data, raise_errors=True)
                
                messages.success(
                    request,
                    f'Import réussi! Créés: {result.totals.get("new", 0)}, '
                    f'Mis à jour: {result.totals.get("update", 0)}, '
                    f'Erreurs: {result.totals.get("error", 0)}'
                )
            else:
                messages.error(request, f'Type de ressource invalide: {resource_type}')
        
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'import: {str(e)}')
        
        return redirect('import_data')
    
    # GET - Afficher le formulaire
    context = {
        'page_title': 'Import de Données',
        'resources': list(RESOURCES.keys()),
        'formats': ['csv', 'json', 'yaml'],
    }
    
    return render(request, 'admin/import_data.html', context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def export_data(request):
    """Interface d'export de données en masse."""
    
    if request.method == 'POST':
        resource_type = request.POST.get('resource_type')
        export_format = request.POST.get('format', 'csv')
        
        if not resource_type:
            messages.error(request, 'Sélectionnez un type de ressource')
            return redirect('export_data')
        
        try:
            # Exporter les données
            if resource_type in RESOURCES:
                resource = RESOURCES[resource_type]()
                queryset = resource.get_queryset()
                dataset = resource.export(queryset)
                
                # Générer le fichier
                if export_format == 'csv':
                    output = dataset.csv
                    filename = f'{resource_type}_export.csv'
                    content_type = 'text/csv'
                elif export_format == 'json':
                    output = dataset.json
                    filename = f'{resource_type}_export.json'
                    content_type = 'application/json'
                elif export_format == 'yaml':
                    output = dataset.yaml
                    filename = f'{resource_type}_export.yaml'
                    content_type = 'text/yaml'
                elif export_format == 'xlsx':
                    output = dataset.xlsx
                    filename = f'{resource_type}_export.xlsx'
                    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                else:
                    raise ValueError(f"Format non supporté: {export_format}")
                
                # Retourner le fichier
                if isinstance(output, str):
                    output = output.encode('utf-8')
                
                response = HttpResponse(output, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                messages.error(request, f'Type de ressource invalide: {resource_type}')
        
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'export: {str(e)}')
        
        return redirect('export_data')
    
    # GET - Afficher le formulaire
    context = {
        'page_title': 'Export de Données',
        'resources': list(RESOURCES.keys()),
        'formats': ['csv', 'json', 'yaml', 'xlsx'],
    }
    
    return render(request, 'admin/export_data.html', context)
