# Generated manually for client feedback (June 2026)

from django.db import migrations, models
import django.core.validators
import uuid


def rename_magasin_to_magazine(apps, schema_editor):
    Book = apps.get_model("catalogue", "Book")
    Book.objects.filter(genre="magasin").update(genre="magazine")


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0036_siteconfiguration_pwa_logo"),
    ]

    operations = [
        migrations.RunPython(rename_magasin_to_magazine, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="author",
            name="nationality",
            field=models.CharField(
                choices=[
                    ("RDC", "République Démocratique du Congo"),
                    ("CG", "Congo-Brazzaville"),
                    ("CM", "Cameroun"),
                    ("GA", "Gabon"),
                    ("CF", "République Centrafricaine"),
                    ("TD", "Tchad"),
                    ("AO", "Angola"),
                    ("SN", "Sénégal"),
                    ("ML", "Mali"),
                    ("CI", "Côte d'Ivoire"),
                    ("BJ", "Bénin"),
                    ("BF", "Burkina Faso"),
                    ("GH", "Ghana"),
                    ("KE", "Kenya"),
                    ("ZA", "Afrique du Sud"),
                    ("NG", "Nigéria"),
                    ("FR", "France"),
                    ("BE", "Belgique"),
                    ("CA", "Canada"),
                    ("US", "États-Unis"),
                    ("OTHER", "Autre"),
                ],
                default="RDC",
                max_length=50,
                verbose_name="Nationalité",
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="genre",
            field=models.CharField(
                choices=[
                    ("articles", "Articles"),
                    ("magazine", "Magazine"),
                    ("revues_scientifiques", "Revues Scientifiques"),
                    ("geographie_histoires", "Géographie et Histoires"),
                    ("theories_litteraires", "Théories Littéraires"),
                    ("roman", "Roman"),
                    ("nouvelle", "Nouvelle"),
                    ("essai", "Essai"),
                    ("jeunesse", "Littérature jeunesse"),
                    ("theatre", "Théâtre"),
                    ("conte", "Conte"),
                    ("memoires", "Mémoires"),
                    ("bande_dessinee", "Bande dessinée"),
                    ("documentaire", "Documentaire"),
                    ("philosophie", "Philosophie"),
                    ("religion", "Religion"),
                    ("pedagogie", "Pédagogie"),
                    ("tourisme", "Tourisme"),
                    ("hotellerie", "Hôtellerie"),
                    ("sport", "Sport"),
                    ("loisir", "Loisir"),
                    ("dev_personnel", "Développement Personnel"),
                    ("fiction", "Fiction"),
                    ("non_fiction", "Non-fiction"),
                    ("science", "Science"),
                    ("biography", "Biographie"),
                    ("poetry", "Poésie"),
                    ("other", "Autre"),
                ],
                default="other",
                max_length=50,
                verbose_name="Genre",
            ),
        ),
        migrations.AddField(
            model_name="audiobookmetadata",
            name="price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Laisser vide pour appliquer la règle automatique (prix du livre × coefficient).",
                max_digits=8,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Prix audio (FCFA)",
            ),
        ),
        migrations.CreateModel(
            name="NewsletterSubscription",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="E-mail")),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                ("subscribed_at", models.DateTimeField(auto_now_add=True, verbose_name="Inscrit le")),
                ("unsubscribed_at", models.DateTimeField(blank=True, null=True, verbose_name="Désinscrit le")),
            ],
            options={
                "verbose_name": "Abonnement newsletter",
                "verbose_name_plural": "Abonnements newsletter",
                "ordering": ["-subscribed_at"],
            },
        ),
    ]
