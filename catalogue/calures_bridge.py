"""Envoi manuel d'un article BNC vers les brouillons du site CALURES."""

import json
from urllib.parse import urlparse

import requests
from django.conf import settings

MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_REQUEST_BYTES = 4_400_000  # Reserve room for multipart headers under Vercel's limit.


class CaluresBridgeError(Exception):
    pass


def send_article_to_calures(article):
    url = getattr(settings, "CALURES_BRIDGE_URL", "")
    token = getattr(settings, "CALURES_BRIDGE_TOKEN", "")
    if not url or not token:
        raise CaluresBridgeError("Configurer CALURES_BRIDGE_URL et CALURES_BRIDGE_TOKEN.")
    parsed = urlparse(url)
    local_debug = settings.DEBUG and parsed.scheme == "http" and parsed.hostname in {
        "localhost", "127.0.0.1",
    }
    if parsed.scheme != "https" and not local_debug:
        raise CaluresBridgeError("Le pont CALURES exige HTTPS.")

    payload = {
        "id": str(article.pk),
        "title": article.title,
        "excerpt": article.excerpt,
        "content": article.content,
        "author_name": article.author_name,
        "category": article.category,
        "publication_date": article.created_at.date().isoformat(),
    }
    encoded_payload = json.dumps(payload, ensure_ascii=False)
    payload_size = len(encoded_payload.encode('utf-8'))
    if payload_size > MAX_REQUEST_BYTES:
        raise CaluresBridgeError("Le texte est trop volumineux pour CALURES.")
    files = None
    if article.image:
        try:
            image_size = article.image.size
            if image_size > MAX_IMAGE_BYTES or image_size + payload_size > MAX_REQUEST_BYTES:
                raise CaluresBridgeError("L'image ou l'article est trop volumineux. Réduisez l'image (4 Mo maximum).")
            article.image.open("rb")
        except OSError as exc:
            raise CaluresBridgeError("Impossible de lire l'image de l'article.") from exc
        files = {"image": (article.image.name.rsplit("/", 1)[-1], article.image.file)}
    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            data={"payload": encoded_payload},
            files=files,
            timeout=(10, 45),
            allow_redirects=False,
        )
        if response.status_code not in (200, 201):
            raise CaluresBridgeError(
                f"CALURES a refusé l'article (HTTP {response.status_code})."
            )
        try:
            return response.json()
        except ValueError as exc:
            raise CaluresBridgeError("Réponse invalide de CALURES.") from exc
    except requests.RequestException as exc:
        raise CaluresBridgeError(f"Échec de connexion à CALURES : {exc}") from exc
    finally:
        if article.image:
            article.image.close()
