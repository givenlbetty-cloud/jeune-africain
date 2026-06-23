"""Utilitaires pour extraire et normaliser les noms d'auteurs depuis les métadonnées des livres."""

from __future__ import annotations

import os
import re

from django.db import IntegrityError

IGNORED_AUTHOR_NAMES = frozenset(
    {
        "",
        "inconnu",
        "auteur inconnu",
        "auteur",
        "unknown",
        "n/a",
        "na",
    }
)

EXTENSIONS_PATTERN = re.compile(r"\.(docx|pdf|epub|doc)$", re.IGNORECASE)
UPLOAD_SUFFIX_PATTERN = re.compile(r"_[A-Za-z0-9]{6,10}$")
MULTISPACE_AUTHOR_PATTERN = re.compile(r"\s{2,}(.+)$")


def title_case_name(name: str) -> str:
    """Met en forme un nom d'auteur (prénom NOM possible)."""
    parts = [p for p in name.split() if p]
    if not parts:
        return ""
    return " ".join(p[:1].upper() + p[1:].lower() if len(p) > 1 else p.upper() for p in parts)


def split_full_name(full_name: str) -> tuple[str, str]:
    """Découpe un nom complet en prénom et nom."""
    parts = [p for p in (full_name or "").strip().split() if p]
    if not parts:
        return "Auteur", "Non renseigné"
    if len(parts) == 1:
        return title_case_name(parts[0]), "-"
    return title_case_name(parts[0]), title_case_name(" ".join(parts[1:]))


def _clean_author_candidate(raw: str | None) -> str | None:
    if not raw:
        return None
    candidate = raw.strip()
    candidate = EXTENSIONS_PATTERN.sub("", candidate).strip()
    candidate = re.sub(r"[_]+", " ", candidate)
    candidate = re.sub(r"\s+", " ", candidate).strip()
    if candidate.lower() in IGNORED_AUTHOR_NAMES:
        return None
    if len(candidate) < 2 or len(candidate.split()) > 8:
        return None
    return title_case_name(candidate)


def extract_author_from_filename(filename: str | None) -> str | None:
    """Extrait l'auteur depuis un nom de fichier (ex. Titre_-_Auteur.pdf)."""
    if not filename:
        return None

    stem = os.path.splitext(os.path.basename(filename))[0]
    stem = UPLOAD_SUFFIX_PATTERN.sub("", stem)

    normalized = stem.replace("_-_", "|||").replace(" - ", "|||").replace(" — ", "|||")
    if "|||" in normalized:
        author_part = normalized.rsplit("|||", 1)[-1]
        return _clean_author_candidate(author_part)

    return None


def extract_author_from_title(title: str | None) -> str | None:
    """Extrait l'auteur depuis le titre (ex. « Mon livre   Alice Dupont »)."""
    if not title:
        return None

    cleaned = title.strip()

    if " - " in cleaned:
        author_part = cleaned.rsplit(" - ", 1)[-1]
        found = _clean_author_candidate(author_part)
        if found:
            return found

    match = MULTISPACE_AUTHOR_PATTERN.search(cleaned)
    if match:
        return _clean_author_candidate(match.group(1))

    return None


def extract_author_from_book_metadata(*, title: str | None = None, pdf_file_name: str | None = None) -> str | None:
    """Déduit le nom d'auteur à partir du fichier PDF puis du titre."""
    for source in (pdf_file_name, title):
        if not source:
            continue
        from_file = extract_author_from_filename(source)
        if from_file:
            return from_file

    return extract_author_from_title(title)


def get_or_create_author_by_name(first_name: str, last_name: str):
    """
    Retourne ou crée un Author sans email (NULL) pour éviter les conflits
    d'unicité PostgreSQL sur email=''.
    """
    from catalogue.models import Author

    author = Author.objects.filter(first_name=first_name, last_name=last_name).first()
    if author:
        return author, False

    try:
        author = Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=None,
            is_verified=False,
        )
        return author, True
    except IntegrityError:
        author = Author.objects.filter(first_name=first_name, last_name=last_name).first()
        if author:
            return author, False
        raise
