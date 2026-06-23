"""Autoriser plusieurs auteurs sans email (NULL au lieu de chaîne vide)."""

from django.db import migrations, models


def empty_email_to_null(apps, schema_editor):
    Author = apps.get_model("catalogue", "Author")
    Author.objects.filter(email="").update(email=None)


def null_email_to_empty(apps, schema_editor):
    Author = apps.get_model("catalogue", "Author")
    Author.objects.filter(email__isnull=True).update(email="")


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0037_client_feedback_june2026"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                null=True,
                unique=True,
                verbose_name="Email",
            ),
        ),
        migrations.RunPython(empty_email_to_null, null_email_to_empty),
    ]
