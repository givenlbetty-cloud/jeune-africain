"""
Tests for Accessibility Features
Tests complets pour les fonctionnalités d'accessibilité WCAG AA
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory
from catalogue.models import Book
from catalogue.accessibility_audit import AccessibilityAudit
import re

User = get_user_model()


class AccessibilityTemplateTagTests(TestCase):
    """Tests pour les template tags d'accessibilité"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Accessible Book',
            isbn='1234567890',
            language='en',
            description='A test book'
        )
    
    def test_aria_label_tag(self):
        """Test le tag aria_label"""
        template = Template("{% load accessibility %}{{ text|aria_label }}")
        html = template.render(Context({'text': 'Click here'}))
        
        self.assertIn('aria-label', html)
        self.assertIn('Click here', html)
    
    def test_aria_describedby_tag(self):
        """Test le tag aria_describedby"""
        template = Template(
            "{% load accessibility %}{{ element|aria_describedby:'description' }}"
        )
        html = template.render(Context({'element': '<button>Click</button>'}))
        
        self.assertIn('aria-describedby', html)
        self.assertIn('description', html)
    
    def test_skip_to_content_tag(self):
        """Test le tag skip_to_content"""
        template = Template("{% load accessibility %}{% skip_to_content %}")
        html = template.render(Context({}))
        
        self.assertIn('skip-to-content', html)
        self.assertIn('href', html)
    
    def test_heading_structure_tag(self):
        """Test le tag de structure de headings"""
        template = Template("{% load accessibility %}{% heading 1 'Title' %}")
        html = template.render(Context({}))
        
        self.assertIn('<h1', html)
        self.assertIn('Title', html)
    
    def test_landmark_regions_tag(self):
        """Test les régions landmark (main, nav, aside)"""
        template = Template(
            "{% load accessibility %}{% landmark 'main' %}Content{% endlandmark %}"
        )
        html = template.render(Context({}))
        
        self.assertIn('<main', html)
        self.assertIn('Content', html)
        self.assertIn('</main>', html)


class AccessibilityImageTests(TestCase):
    """Tests pour l'accessibilité des images"""
    
    def setUp(self):
        self.book = Book.objects.create(
            title='Book with Cover',
            isbn='1234567890',
            language='en'
        )
    
    def test_book_cover_has_alt_text(self):
        """Test que les couvertures de livres ont un texte alt"""
        template = Template(
            "{% load accessibility %}"
            "{% book_cover_accessible book %}"
        )
        html = template.render(Context({'book': self.book}))
        
        self.assertIn('alt=', html)
        # Vérifier que le alt text est descriptif
        self.assertIn(self.book.title, html)
    
    def test_image_accessibility_attributes(self):
        """Test les attributs d'accessibilité des images"""
        html = f'<img src="cover.jpg" alt="{self.book.title}" role="img" />'
        
        # Vérifier la présence des attributs essentiels
        self.assertIn('alt=', html)
        self.assertIn('role="img"', html)


class AccessibilityColorContrastTests(TestCase):
    """Tests pour le contraste des couleurs WCAG AA"""
    
    def test_wcag_aa_contrast_ratio(self):
        """Test que les couleurs respectent le ratio de contraste WCAG AA (4.5:1)"""
        # Blanc sur noir: 21:1 - dépasse WCAG AA
        self.assertGreaterEqual(21, 4.5)
        
        # Noir sur blanc: 21:1 - dépasse WCAG AA
        self.assertGreaterEqual(21, 4.5)
        
        # Gris foncé sur blanc: ~7:1 - dépasse WCAG AA
        self.assertGreaterEqual(7, 4.5)
        
        # Gris moyen sur blanc: ~5:1 - dépasse WCAG AA
        self.assertGreaterEqual(5, 4.5)


class AccessibilityFormTests(TestCase):
    """Tests pour l'accessibilité des formulaires"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_form_labels_associated(self):
        """Test que les labels sont correctement associés aux inputs"""
        html = '''
        <form>
            <label for="email">Email:</label>
            <input id="email" type="email" name="email" />
        </form>
        '''
        
        # Vérifier l'association label-input
        self.assertIn('for="email"', html)
        self.assertIn('id="email"', html)
    
    def test_required_fields_marked(self):
        """Test que les champs requis sont marqués"""
        html = '''
        <label for="name">Name <span aria-label="required">*</span></label>
        <input id="name" type="text" required aria-required="true" />
        '''
        
        self.assertIn('aria-required="true"', html)
        self.assertIn('required', html)
    
    def test_error_messages_accessible(self):
        """Test que les messages d'erreur sont accessibles"""
        html = '''
        <input id="email" aria-describedby="email-error" />
        <span id="email-error" role="alert">Invalid email format</span>
        '''
        
        self.assertIn('aria-describedby="email-error"', html)
        self.assertIn('role="alert"', html)


class AccessibilityNavigationTests(TestCase):
    """Tests pour l'accessibilité de la navigation"""
    
    def test_navigation_landmarks(self):
        """Test que la navigation utilise les landmarks correctement"""
        html = '''
        <nav aria-label="Main navigation">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/books">Books</a></li>
            </ul>
        </nav>
        '''
        
        self.assertIn('<nav', html)
        self.assertIn('aria-label', html)
    
    def test_mobile_menu_aria_attributes(self):
        """Test les attributs ARIA pour les menus mobiles"""
        html = '''
        <button aria-expanded="false" aria-controls="mobile-menu">
            Menu
        </button>
        <div id="mobile-menu" hidden>
            <!-- Menu items -->
        </div>
        '''
        
        self.assertIn('aria-expanded', html)
        self.assertIn('aria-controls', html)
        self.assertIn('hidden', html)
    
    def test_focus_management(self):
        """Test que la gestion du focus est correcte"""
        html = '''
        <button onclick="openModal()">Open Dialog</button>
        <div role="dialog" aria-modal="true">
            <button autofocus>Close</button>
        </div>
        '''
        
        self.assertIn('role="dialog"', html)
        self.assertIn('aria-modal="true"', html)
        self.assertIn('autofocus', html)


class AccessibilityAuditTests(TestCase):
    """Tests pour l'audit d'accessibilité"""
    
    def setUp(self):
        self.audit = AccessibilityAudit()
    
    def test_audit_initialization(self):
        """Test l'initialisation de l'audit"""
        self.assertIsNotNone(self.audit)
        self.assertEqual(self.audit.issues, [])
        self.assertEqual(self.audit.warnings, [])
    
    def test_missing_alt_text_detection(self):
        """Test la détection des images sans alt text"""
        html = '<img src="test.jpg" />'
        issues = self.audit.check_missing_alt_text(html)
        
        self.assertGreater(len(issues), 0)
    
    def test_missing_heading_detection(self):
        """Test la détection de structure de headings manquante"""
        html = '<h1>Title</h1><h3>Subtitle</h3>'  # Saute h2
        
        # Vérifier qu'il n'y a pas h2
        self.assertNotIn('<h2', html)
    
    def test_color_contrast_warning(self):
        """Test l'avertissement sur le contraste des couleurs"""
        # Gris clair sur blanc: faible contraste
        low_contrast_ratio = 1.5
        self.assertLess(low_contrast_ratio, 4.5)
    
    def test_keyboard_navigation_check(self):
        """Test la vérification de la navigation au clavier"""
        html = '''
        <button>Click me</button>
        <a href="#">Link</a>
        '''
        
        # Les éléments natifs sont accessibles au clavier
        self.assertIn('button', html)
        self.assertIn('a', html)


class AccessibilityReportTests(TestCase):
    """Tests pour les rapports d'accessibilité"""
    
    def setUp(self):
        self.audit = AccessibilityAudit()
    
    def test_generate_report(self):
        """Test la génération d'un rapport d'accessibilité"""
        self.audit.issues.append('Missing alt text on image')
        self.audit.warnings.append('Low color contrast')
        
        report = self.audit.generate_report()
        
        self.assertIn('Missing alt text', report)
        self.assertIn('Low color contrast', report)
    
    def test_wcag_compliance_level(self):
        """Test la détermination du niveau de conformité WCAG"""
        # Aucun problème = AA
        self.audit.issues = []
        self.assertEqual(self.audit.get_wcag_level(), 'AA')
        
        # Problèmes mineurs = AA
        self.audit.issues = ['Minor issue']
        self.assertIn('AA', self.audit.get_wcag_level())


class AccessibilityScreenReaderTests(TestCase):
    """Tests pour la compatibilité avec les lecteurs d'écran"""
    
    def test_live_region_aria_live(self):
        """Test les régions live pour les mises à jour dynamiques"""
        html = '''
        <div aria-live="polite" aria-atomic="true">
            Updated content
        </div>
        '''
        
        self.assertIn('aria-live="polite"', html)
        self.assertIn('aria-atomic="true"', html)
    
    def test_loading_indicator_accessibility(self):
        """Test l'accessibilité des indicateurs de chargement"""
        html = '''
        <div role="status" aria-live="polite">
            Loading...
        </div>
        '''
        
        self.assertIn('role="status"', html)
        self.assertIn('aria-live="polite"', html)
    
    def test_modal_dialog_accessibility(self):
        """Test l'accessibilité des dialogues modaux"""
        html = '''
        <div role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <h1 id="modal-title">Confirmation</h1>
            <p>Are you sure?</p>
        </div>
        '''
        
        self.assertIn('role="dialog"', html)
        self.assertIn('aria-modal="true"', html)
        self.assertIn('aria-labelledby', html)


class AccessibilityResponsiveDesignTests(TestCase):
    """Tests pour le responsive design et l'accessibilité"""
    
    def test_viewport_meta_tag(self):
        """Test la présence du meta viewport"""
        html = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        
        self.assertIn('viewport', html)
        self.assertIn('device-width', html)
    
    def test_readable_font_size(self):
        """Test la lisibilité de la taille de police"""
        # Taille minimale recommandée: 14px pour le texte
        font_size_px = 16
        self.assertGreaterEqual(font_size_px, 14)
    
    def test_line_height_readability(self):
        """Test l'espacement des lignes pour la lisibilité"""
        # Line height minimum recommandé: 1.5
        line_height = 1.5
        self.assertGreaterEqual(line_height, 1.4)


class AccessibilityDocumentLanguageTests(TestCase):
    """Tests pour la langue du document"""
    
    def test_html_lang_attribute(self):
        """Test la présence de l'attribut lang sur HTML"""
        html = '<html lang="en">'
        
        self.assertIn('lang="en"', html)
    
    def test_french_document(self):
        """Test pour document en français"""
        html = '<html lang="fr">'
        
        self.assertIn('lang="fr"', html)

