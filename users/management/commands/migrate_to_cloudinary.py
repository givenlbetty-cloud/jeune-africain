"""
Commande de migration : uploade tous les fichiers media locaux vers Cloudinary
en conservant les mêmes chemins (public_id) pour que les URLs en DB restent valides.

Usage:
    python manage.py migrate_to_cloudinary
    python manage.py migrate_to_cloudinary --dry-run   (affiche sans uploader)
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary
import cloudinary.uploader


class Command(BaseCommand):
    help = "Migre les fichiers media locaux vers Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Liste les fichiers sans les uploader",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = Path(settings.MEDIA_ROOT)

        if not media_root.exists():
            self.stdout.write(self.style.ERROR(f"MEDIA_ROOT introuvable : {media_root}"))
            return

        # Vérifier config Cloudinary
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME') or cloudinary.config().cloud_name
        if not cloud_name:
            self.stdout.write(self.style.ERROR(
                "CLOUDINARY_CLOUD_NAME non configuré. Ajoutez les variables d'environnement."
            ))
            return

        self.stdout.write(f"Cloud Cloudinary : {cloud_name}")

        files = list(media_root.rglob('*'))
        files = [f for f in files if f.is_file()]
        total = len(files)
        self.stdout.write(f"Fichiers trouvés : {total}")

        success, skipped, errors = 0, 0, 0

        for i, filepath in enumerate(files, 1):
            # Chemin relatif = public_id Cloudinary (sans extension pour les images)
            rel_path = filepath.relative_to(media_root)
            public_id = str(rel_path.with_suffix(''))  # Cloudinary stocke sans extension
            
            # Déterminer le type de ressource
            suffix = filepath.suffix.lower()
            if suffix in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                resource_type = 'image'
            elif suffix == '.pdf':
                resource_type = 'raw'
            elif suffix in ('.epub', '.mp3', '.mp4'):
                resource_type = 'raw'
            else:
                resource_type = 'raw'

            self.stdout.write(f"[{i}/{total}] {rel_path}", ending='')

            if dry_run:
                self.stdout.write(self.style.WARNING(' → DRY RUN'))
                continue

            try:
                result = cloudinary.uploader.upload(
                    str(filepath),
                    public_id=public_id,
                    resource_type=resource_type,
                    overwrite=False,  # Ne pas écraser si déjà présent
                    use_filename=True,
                    unique_filename=False,
                )
                self.stdout.write(self.style.SUCCESS(f' → OK ({result["secure_url"][:60]}...)'))
                success += 1
            except Exception as e:
                err_msg = str(e)
                if 'already exists' in err_msg or 'overwrite' in err_msg.lower():
                    self.stdout.write(self.style.WARNING(' → déjà présent, ignoré'))
                    skipped += 1
                else:
                    self.stdout.write(self.style.ERROR(f' → ERREUR: {err_msg}'))
                    errors += 1

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN terminé. {total} fichiers à migrer."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Migration terminée : {success} uploadés, {skipped} déjà présents, {errors} erreurs."
            ))
