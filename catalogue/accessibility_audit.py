"""
Accessibility Audit Tools - WCAG 2.1 AA Compliance
Utilitaires pour tester et vérifier la conformité d'accessibilité
"""

from django.test import TestCase, Client
from django.urls import reverse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import re


class AccessibilityAudit:
    """
    Classe pour auditer l'accessibilité d'une page
    """
    
    def __init__(self, html_content, base_url='http://testserver'):
        self.html = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = base_url
        self.issues = []
        self.warnings = []
        self.passes = []
    
    def audit_all(self):
        """Exécuter tous les audits"""
        self.check_page_structure()
        self.check_headings()
        self.check_images()
        self.check_links()
        self.check_forms()
        self.check_color_contrast()
        self.check_focus_indicators()
        self.check_aria_labels()
        self.check_keyboard_navigation()
        self.check_language_attribute()
        self.check_page_title()
        
        return self.get_report()
    
    def check_page_structure(self):
        """Vérifier la structure sémantique"""
        # Au moins une main tag
        if not self.soup.find('main'):
            self.issues.append("Page missing <main> element")
        else:
            self.passes.append("Page has <main> element")
        
        # Au moins une h1
        h1_tags = self.soup.find_all('h1')
        if not h1_tags:
            self.issues.append("Page missing <h1> heading")
        elif len(h1_tags) > 1:
            self.warnings.append("Page has multiple <h1> headings (should have only one)")
        else:
            self.passes.append("Page has single <h1> heading")
        
        # Headings dans l'ordre
        heading_levels = []
        for heading in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            heading_levels.append(level)
        
        # Vérifier que les niveaux augmentent progressivement
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                self.warnings.append(
                    f"Heading jump detected: from h{heading_levels[i-1]} to h{heading_levels[i]}"
                )
        
        if not any(h > 1 for h in heading_levels):
            self.passes.append("Heading hierarchy is correct")
    
    def check_headings(self):
        """Vérifier les headings"""
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            text = heading.get_text(strip=True)
            
            if not text:
                self.issues.append(f"Empty {heading.name} tag found")
            
            # Vérifier que le texte du heading n'est pas trop long
            if len(text) > 100:
                self.warnings.append(f"Heading too long ({len(text)} chars): '{text[:50]}...'")
    
    def check_images(self):
        """Vérifier les images"""
        images = self.soup.find_all('img')
        
        if not images:
            self.passes.append("No images found")
            return
        
        for img in images:
            alt_text = img.get('alt')
            src = img.get('src', '')
            
            if alt_text is None:
                self.issues.append(f"Image missing alt text: {src}")
            elif alt_text == '':
                # Alt vide c'est ok si c'est decoratif
                if not img.get('role') == 'presentation':
                    self.warnings.append(f"Image has empty alt (decorative?): {src}")
            else:
                # Alt should not be too long
                if len(alt_text) > 150:
                    self.warnings.append(
                        f"Alt text too long ({len(alt_text)} chars): '{alt_text[:50]}...'"
                    )
        
        if all(img.get('alt') for img in images):
            self.passes.append("All images have alt text")
    
    def check_links(self):
        """Vérifier les liens"""
        links = self.soup.find_all('a')
        
        if not links:
            self.passes.append("No links found")
            return
        
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            aria_label = link.get('aria-label', '')
            
            # Lien sans texte
            if not text and not aria_label:
                self.issues.append(f"Link missing text and aria-label: {href}")
            
            # "Click here" ou similaire
            if text.lower() in ['click here', 'read more', 'link', 'click']:
                self.warnings.append(
                    f"Generic link text: '{text}' (use descriptive text)"
                )
            
            # Lien vide
            if not href:
                self.issues.append("Link with no href attribute")
    
    def check_forms(self):
        """Vérifier les formulaires"""
        forms = self.soup.find_all('form')
        
        if not forms:
            self.passes.append("No forms found")
            return
        
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_field in inputs:
                field_id = input_field.get('id')
                field_type = input_field.get('type', 'text')
                
                # Input hidden ne nécessite pas de label
                if field_type == 'hidden':
                    continue
                
                # Chercher le label
                label = form.find('label', {'for': field_id})
                aria_label = input_field.get('aria-label')
                aria_labelledby = input_field.get('aria-labelledby')
                
                if not (label or aria_label or aria_labelledby):
                    self.issues.append(
                        f"Form input ({field_id or field_type}) missing label"
                    )
            
            # Vérifier le csrf token
            csrf_token = form.find('input', {'name': 'csrfmiddlewaretoken'})
            if not csrf_token:
                self.warnings.append("Form possibly missing CSRF token")
        
        self.passes.append("Form structure verified")
    
    def check_color_contrast(self):
        """Vérifier le contraste des couleurs"""
        # Note: Ceci est une vérification basique
        # Pour une vraie vérification, utiliser axe-core ou similaire
        
        body = self.soup.find('body')
        if body:
            bg_color = body.get('style', '')
            if 'background' not in bg_color.lower():
                self.passes.append("Default background color (good contrast)")
            else:
                self.warnings.append("Custom background color - verify contrast manually")
    
    def check_focus_indicators(self):
        """Vérifier les indicateurs de focus"""
        css_content = ""
        for style_tag in self.soup.find_all('style'):
            css_content += style_tag.string or ""
        
        if ':focus' in css_content or 'focus' in css_content:
            if 'outline' in css_content or 'box-shadow' in css_content:
                self.passes.append("Focus indicators defined in CSS")
            else:
                self.warnings.append("Focus styles exist but may be insufficient")
        else:
            self.issues.append("No focus indicator styles found")
    
    def check_aria_labels(self):
        """Vérifier les labels ARIA"""
        # Icon buttons without text
        icon_buttons = self.soup.find_all(['button', 'a'], class_=['icon-only', 'btn-icon'])
        
        for btn in icon_buttons:
            text = btn.get_text(strip=True)
            aria_label = btn.get('aria-label')
            
            if not text and not aria_label:
                self.issues.append("Icon button missing aria-label and text")
        
        # ARIA live regions
        live_regions = self.soup.find_all(attrs={'aria-live': True})
        if live_regions:
            self.passes.append(f"ARIA live regions found: {len(live_regions)}")
    
    def check_keyboard_navigation(self):
        """Vérifier la navigation au clavier"""
        # Vérifier les tabindex
        tabindex = self.soup.find_all(attrs={'tabindex': True})
        
        for elem in tabindex:
            tabindex_val = elem.get('tabindex')
            try:
                if int(tabindex_val) > 0:
                    self.warnings.append(
                        f"Positive tabindex found ({tabindex_val}) - may break keyboard nav"
                    )
            except ValueError:
                pass
        
        # Vérifier les éléments interactive
        interactive = self.soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        if interactive:
            self.passes.append(f"Interactive elements found: {len(interactive)}")
    
    def check_language_attribute(self):
        """Vérifier l'attribut lang"""
        html_tag = self.soup.find('html')
        
        if html_tag and html_tag.get('lang'):
            self.passes.append(f"Language attribute set: {html_tag.get('lang')}")
        else:
            self.issues.append("HTML tag missing lang attribute")
    
    def check_page_title(self):
        """Vérifier le titre de la page"""
        title_tag = self.soup.find('title')
        
        if not title_tag:
            self.issues.append("Page missing <title> tag")
        elif not title_tag.string:
            self.issues.append("Page <title> is empty")
        elif len(title_tag.string) > 60:
            self.warnings.append(f"Page title too long: '{title_tag.string}'")
        else:
            self.passes.append(f"Page title: '{title_tag.string}'")
    
    def get_report(self):
        """Générer un rapport d'audit"""
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'passes': self.passes,
            'total_issues': len(self.issues),
            'total_warnings': len(self.warnings),
            'total_passes': len(self.passes),
            'score': self.calculate_score()
        }
    
    def calculate_score(self):
        """Calculer un score d'accessibilité"""
        total = len(self.issues) + len(self.warnings) + len(self.passes)
        if total == 0:
            return 0
        
        # Score: 100 - (issues*10) - (warnings*5)
        score = 100 - (len(self.issues) * 10) - (len(self.warnings) * 5)
        return max(0, min(100, score))


class AccessibilityTestCase(TestCase):
    """
    Classe de base pour les tests d'accessibilité
    """
    
    def audit_page(self, url_name, **kwargs):
        """
        Auditer une page
        
        Usage:
            report = self.audit_page('books:list')
            self.assertAccessible(report)
        """
        client = Client()
        response = client.get(reverse(url_name, kwargs=kwargs))
        
        audit = AccessibilityAudit(response.content.decode())
        return audit.audit_all()
    
    def assertAccessible(self, report):
        """Affirmer que la page est accessible"""
        self.assertEqual(
            report['total_issues'], 0,
            f"Accessibility issues found:\n" +
            "\n".join(f"- {issue}" for issue in report['issues'])
        )
    
    def assertAccessibilityScore(self, report, min_score=80):
        """Affirmer que le score d'accessibilité dépasse un minimum"""
        self.assertGreaterEqual(
            report['score'], min_score,
            f"Accessibility score {report['score']} below minimum {min_score}\n" +
            f"Issues: {report['total_issues']}, Warnings: {report['total_warnings']}"
        )


# Utility functions

def audit_url(url, base_url='http://testserver'):
    """
    Auditer une URL (pour usage manuel)
    """
    try:
        response = requests.get(url)
        audit = AccessibilityAudit(response.text, base_url)
        return audit.audit_all()
    except Exception as e:
        return {
            'error': str(e),
            'message': 'Could not audit URL'
        }


def generate_audit_report(html_content):
    """
    Générer un rapport d'audit formaté
    """
    audit = AccessibilityAudit(html_content)
    report = audit.audit_all()
    
    output = f"""
ACCESSIBILITY AUDIT REPORT
==========================

Score: {report['score']}/100

CRITICAL ISSUES ({report['total_issues']}):
{chr(10).join(f"  ✗ {issue}" for issue in report['issues']) or "  None"}

WARNINGS ({report['total_warnings']}):
{chr(10).join(f"  ⚠ {warning}" for warning in report['warnings']) or "  None"}

PASSES ({report['total_passes']}):
{chr(10).join(f"  ✓ {p}" for p in report['passes']) or "  None"}
"""
    
    return output

