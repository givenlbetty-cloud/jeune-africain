#!/usr/bin/env python
"""
🧪 Script de Validation du Lecteur eBook Amélioré
Vérifie que toutes les améliorations sont en place
"""

import os
import sys
import json

class ReaderValidation:
    """Validateur des améliorations du lecteur."""
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.results = {
            'files': {},
            'urls': {},
            'views': {},
            'models': {},
            'warnings': []
        }
    
    def check_files(self):
        """Vérifier que tous les fichiers existent."""
        files_to_check = {
            'Template': 'templates/catalogue/book_reader.html',
            'CSS Reader': 'static/css/reader.css',
            'JS Reader': 'static/js/ebook-reader.js',
            'Tests': 'catalogue/test_ebook_reader.py',
            'Guide': 'EBOOK_READER_GUIDE.md',
            'Installation': 'READER_INSTALLATION_GUIDE.md',
            'Improvements': 'READER_IMPROVEMENTS_COMPLETE.md',
        }
        
        print("📁 Vérification des fichiers...")
        for name, path in files_to_check.items():
            full_path = os.path.join(self.base_path, path)
            exists = os.path.exists(full_path)
            self.results['files'][name] = {
                'path': path,
                'exists': exists,
                'size': os.path.getsize(full_path) if exists else 0
            }
            
            status = "✅" if exists else "❌"
            size_str = f" ({os.path.getsize(full_path)} bytes)" if exists else ""
            print(f"  {status} {name}: {path}{size_str}")
    
    def check_template_content(self):
        """Vérifier le contenu du template."""
        print("\n📄 Vérification du template...")
        template_path = os.path.join(self.base_path, 'templates/catalogue/book_reader.html')
        
        if not os.path.exists(template_path):
            print("  ❌ Template non trouvé")
            return
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        checks = {
            'Load static tag': '{% load static %}',
            'Reader CSS': "{% static 'css/reader.css' %}",
            'Reader JS': "{% static 'js/ebook-reader.js' %}",
            'EBookReader class': 'new EBookReader({',
            'Progress bar': 'progress-bar-fill',
            'Highlight support': 'class="highlight"',
            'Toast notifications': 'showToast(',
            'Keyboard shortcuts': 'keydown',
        }
        
        for name, check_string in checks.items():
            found = check_string in content
            status = "✅" if found else "❌"
            print(f"  {status} {name}")
    
    def check_urls(self):
        """Vérifier les URLs."""
        print("\n🔗 Vérification des URLs...")
        urls_path = os.path.join(self.base_path, 'catalogue/urls.py')
        
        if not os.path.exists(urls_path):
            print("  ❌ urls.py non trouvé")
            return
        
        with open(urls_path, 'r') as f:
            content = f.read()
        
        urls_to_check = {
            'save_highlight': 'save_highlight_view',
            'save_note': 'save_note_view',
            'delete_highlight': 'delete_highlight_view',
            'delete_note': 'delete_note_view',
            'export_annotations': 'export_annotations_view',
            'get_annotations': 'get_annotations_view',
        }
        
        for name, func in urls_to_check.items():
            found = func in content
            status = "✅" if found else "❌"
            print(f"  {status} {name} ({func})")
    
    def check_views(self):
        """Vérifier les vues."""
        print("\n🎯 Vérification des vues...")
        views_path = os.path.join(self.base_path, 'catalogue/frontend_views.py')
        
        if not os.path.exists(views_path):
            print("  ❌ frontend_views.py non trouvé")
            return
        
        with open(views_path, 'r') as f:
            content = f.read()
        
        views_to_check = {
            'save_highlight_view': 'def save_highlight_view',
            'save_note_view': 'def save_note_view',
            'delete_highlight_view': 'def delete_highlight_view',
            'delete_note_view': 'def delete_note_view',
            'export_annotations_view': 'def export_annotations_view',
            'timezone import': 'from django.utils import timezone',
        }
        
        for name, check_string in views_to_check.items():
            found = check_string in content
            status = "✅" if found else "❌"
            print(f"  {status} {name}")
            if not found:
                self.results['warnings'].append(f"Vue manquante: {name}")
    
    def check_css_features(self):
        """Vérifier les features CSS."""
        print("\n🎨 Vérification des styles...")
        css_path = os.path.join(self.base_path, 'static/css/reader.css')
        
        if not os.path.exists(css_path):
            print("  ❌ CSS non trouvé")
            return
        
        with open(css_path, 'r') as f:
            content = f.read()
        
        features = {
            'Progress bar sensuel': 'progress-bar-container',
            'Highlight animations': 'highlightBorder',
            'Dark mode support': '[data-bs-theme="dark"]',
            'Touch optimization': '@media (hover: none)',
            'GPU acceleration': 'will-change',
        }
        
        for name, feature in features.items():
            found = feature in content
            status = "✅" if found else "❌"
            print(f"  {status} {name}")
    
    def check_js_features(self):
        """Vérifier les features JavaScript."""
        print("\n⚙️ Vérification du JavaScript...")
        js_path = os.path.join(self.base_path, 'static/js/ebook-reader.js')
        
        if not os.path.exists(js_path):
            print("  ❌ JS non trouvé")
            return
        
        with open(js_path, 'r') as f:
            content = f.read()
        
        features = {
            'Classe EBookReader': 'class EBookReader',
            'Scroll tracking': 'setupScrollTracking',
            'Highlighting': 'setupHighlighting',
            'Keyboard shortcuts': 'setupKeyboardShortcuts',
            'Toast notifications': 'showToast',
            'Save progress': 'saveProgress',
            'Notes dialog': 'showNoteDialog',
        }
        
        for name, feature in features.items():
            found = feature in content
            status = "✅" if found else "❌"
            print(f"  {status} {name}")
    
    def check_models(self):
        """Vérifier les modèles."""
        print("\n📊 Vérification des modèles...")
        models_path = os.path.join(self.base_path, 'catalogue/models.py')
        
        if not os.path.exists(models_path):
            print("  ❌ models.py non trouvé")
            return
        
        with open(models_path, 'r') as f:
            content = f.read()
        
        fields = {
            'Highlight.page_number': ('class Highlight', 'page_number'),
            'Note.page_number': ('class Note', 'page_number'),
            'ReadingSession.progress_percent': ('class ReadingSession', 'progress_percent'),
            'ReadingSession.is_completed': ('class ReadingSession', 'is_completed'),
        }
        
        for name, (class_check, field_check) in fields.items():
            found = field_check in content
            status = "✅" if found else "⚠️"
            print(f"  {status} {name}")
            if not found:
                self.results['warnings'].append(f"Champ manquant dans le modèle: {name}")
    
    def generate_report(self):
        """Générer un rapport."""
        print("\n" + "="*60)
        print("📋 RAPPORT DE VALIDATION")
        print("="*60)
        
        # Résumé des fichiers
        files_ok = sum(1 for f in self.results['files'].values() if f['exists'])
        total_files = len(self.results['files'])
        print(f"\n📁 Fichiers: {files_ok}/{total_files} ✅")
        
        # Taille totale
        total_size = sum(f['size'] for f in self.results['files'].values())
        print(f"   Taille totale: {total_size:,} bytes")
        
        # Avertissements
        if self.results['warnings']:
            print(f"\n⚠️ Avertissements ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   - {warning}")
        else:
            print("\n✅ Aucun avertissement!")
        
        print("\n" + "="*60)
        print("✨ VALIDATION COMPLÈTE ✨")
        print("="*60)
    
    def run(self):
        """Lancer la validation complète."""
        print("🧪 Validation du Lecteur eBook Amélioré\n")
        
        self.check_files()
        self.check_template_content()
        self.check_urls()
        self.check_views()
        self.check_css_features()
        self.check_js_features()
        self.check_models()
        self.generate_report()
        
        return len(self.results['warnings']) == 0


if __name__ == '__main__':
    # Déterminer le chemin de base
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = '/workspaces/bnc'
    
    if not os.path.exists(base_path):
        print(f"❌ Chemin invalide: {base_path}")
        sys.exit(1)
    
    validator = ReaderValidation(base_path)
    success = validator.run()
    
    sys.exit(0 if success else 1)
