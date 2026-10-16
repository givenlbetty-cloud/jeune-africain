from django.test import SimpleTestCase

from catalogue.article_content import content_for_editor, render_article_content


class ArticleContentTests(SimpleTestCase):
    def test_plain_text_keeps_paragraphs_and_escapes_markup(self):
        html = render_article_content("Bonjour\n\n<script>alert(1)</script>")
        self.assertIn("<p>Bonjour</p>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_editor_html_keeps_formatting_and_links(self):
        source = (
            '<h2>Titre</h2>'
            '<p><strong>Gras</strong> <u>souligné</u> '
            '<span class="text-big" style="color:#E63946">rouge</span> '
            '<a href="https://calures.org" target="_blank" rel="noopener noreferrer">site</a></p>'
        )
        html = render_article_content(source)
        self.assertIn("<h2>Titre</h2>", html)
        self.assertIn("<strong>Gras</strong>", html)
        self.assertIn("<u>souligné</u>", html)
        self.assertIn("text-big", html)
        self.assertIn("color:#E63946", html.replace(" ", ""))
        self.assertIn('href="https://calures.org"', html)

    def test_editor_html_drops_scripts_and_unsafe_links(self):
        source = (
            '<p onclick="alert(1)">Texte</p>'
            '<script>alert(1)</script>'
            '<a href="javascript:alert(1)">mauvais</a>'
            '<span class="evil text-huge">grand</span>'
        )
        html = render_article_content(source)
        self.assertNotIn("<script>", html)
        self.assertNotIn("onclick", html)
        self.assertNotIn("javascript:", html)
        self.assertNotIn("evil", html)
        self.assertIn("text-huge", html)
        self.assertIn("Texte", html)

    def test_already_published_plain_text_gets_clickable_links(self):
        html = render_article_content("Article déjà publié.\n\nLire https://calures.org/livres.")
        self.assertIn("<p>Article déjà publié.</p>", html)
        self.assertIn('href="https://calures.org/livres"', html)
        self.assertIn(">https://calures.org/livres</a>", html)

    def test_editor_can_format_an_already_published_article(self):
        prepared = content_for_editor("Texte publié\n\nSuite sur https://calures.org")
        self.assertIn("<p>Texte publié</p>", prepared)
        self.assertIn('href="https://calures.org"', prepared)
        self.assertEqual(content_for_editor("<p><strong>Déjà en HTML</strong></p>"), "<p><strong>Déjà en HTML</strong></p>")
