"""Vérifie l'envoi manuel des articles BNC vers les brouillons CALURES."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4
from io import StringIO

from django.test import SimpleTestCase, override_settings
from django.core.management import call_command, CommandError

from catalogue.calures_bridge import CaluresBridgeError, send_article_to_calures


class CaluresBridgeTests(SimpleTestCase):
    def setUp(self):
        self.article = SimpleNamespace(
            pk=uuid4(), title="Une voix nouvelle", excerpt="Présentation",
            content="<p>Un texte.</p>", author_name="CALURES",
            category="CULTURE", created_at=datetime(2026, 10, 10, tzinfo=timezone.utc),
            image=None,
        )

    @override_settings(
        CALURES_BRIDGE_URL="https://calures.org/integrations/bnc/articles/",
        CALURES_BRIDGE_TOKEN="test-token", DEBUG=False,
    )
    @patch("catalogue.calures_bridge.requests.post")
    def test_sends_article_to_calures_draft_receiver(self, post):
        post.return_value = Mock(status_code=201)
        post.return_value.json.return_value = {"status": "created", "page_id": 42}

        result = send_article_to_calures(self.article)

        self.assertEqual(result["status"], "created")
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-token")
        self.assertIn(str(self.article.pk), kwargs["data"]["payload"])
        self.assertFalse(kwargs["allow_redirects"])

    @override_settings(
        CALURES_BRIDGE_URL="http://calures.org/integrations/bnc/articles/",
        CALURES_BRIDGE_TOKEN="test-token", DEBUG=False,
    )
    @patch("catalogue.calures_bridge.requests.post")
    def test_refuses_unencrypted_remote_connection(self, post):
        with self.assertRaises(CaluresBridgeError):
            send_article_to_calures(self.article)
        post.assert_not_called()

    @override_settings(CALURES_BRIDGE_URL="https://calures-editions.vercel.app/integrations/bnc/articles/", CALURES_BRIDGE_TOKEN="test-token")
    @patch("catalogue.calures_bridge.requests.post")
    def test_rejects_large_image_before_upload(self, post):
        self.article.image = Mock(size=5 * 1024 * 1024)
        with self.assertRaisesMessage(CaluresBridgeError, "4 Mo maximum"):
            send_article_to_calures(self.article)
        post.assert_not_called()
        self.article.image.open.assert_not_called()

    @override_settings(CALURES_BRIDGE_URL="https://calures-editions.vercel.app/integrations/bnc/articles/", CALURES_BRIDGE_TOKEN="")
    @patch("catalogue.calures_bridge.requests.post")
    def test_requires_private_token(self, post):
        with self.assertRaises(CaluresBridgeError):
            send_article_to_calures(self.article)
        post.assert_not_called()

    @override_settings(CALURES_BRIDGE_URL="https://calures-editions.vercel.app/integrations/bnc/articles/", CALURES_BRIDGE_TOKEN="test-token")
    @patch("catalogue.management.commands.check_calures_bridge.requests.post")
    def test_connection_check_does_not_send_article(self, post):
        post.return_value = Mock(status_code=400)
        post.return_value.json.return_value = {"error": "Données absentes ou trop volumineuses."}
        output = StringIO()
        call_command('check_calures_bridge', stdout=output)
        self.assertIn('Aucun article créé', output.getvalue())
        self.assertEqual(post.call_args.kwargs['data'], {})
        self.assertFalse(post.call_args.kwargs['allow_redirects'])

    @override_settings(CALURES_BRIDGE_URL="https://calures-editions.vercel.app/integrations/bnc/articles/", CALURES_BRIDGE_TOKEN="test-token")
    @patch("catalogue.management.commands.check_calures_bridge.requests.post")
    def test_connection_check_rejects_wrong_token(self, post):
        post.return_value = Mock(status_code=403)
        with self.assertRaisesMessage(CommandError, 'Jeton CALURES refusé'):
            call_command('check_calures_bridge')
