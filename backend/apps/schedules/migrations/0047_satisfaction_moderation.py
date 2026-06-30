from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_moderation_status(apps, schema_editor):
    SatisfactionSurvey = apps.get_model("schedules", "SatisfactionSurvey")
    for survey in SatisfactionSurvey.objects.all().iterator():
        if not survey.suggestion:
            status = "APPROVED"
        elif survey.is_approved:
            status = "APPROVED"
        else:
            status = "PENDING"
        SatisfactionSurvey.objects.filter(pk=survey.pk).update(moderation_status=status)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("schedules", "0046_dynamic_materials"),
    ]

    operations = [
        migrations.AddField(
            model_name="satisfactionsurvey",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pendente"),
                    ("APPROVED", "Aprovado"),
                    ("REJECTED", "Reprovado"),
                    ("HIDDEN", "Oculto"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="satisfactionsurvey",
            name="moderated_comment",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="satisfactionsurvey",
            name="moderated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="satisfactionsurvey",
            name="moderated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="moderated_satisfaction_surveys",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="SatisfactionSurveyModerationHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("previous_status", models.CharField(blank=True, max_length=20)),
                ("new_status", models.CharField(
                    choices=[
                        ("PENDING", "Pendente"),
                        ("APPROVED", "Aprovado"),
                        ("REJECTED", "Reprovado"),
                        ("HIDDEN", "Oculto"),
                    ],
                    max_length=20,
                )),
                ("comment_snapshot", models.TextField(blank=True)),
                ("decided_at", models.DateTimeField(auto_now_add=True)),
                ("decided_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="satisfaction_moderation_decisions",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("survey", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="moderation_history",
                    to="schedules.satisfactionsurvey",
                )),
            ],
            options={"ordering": ["-decided_at", "-id"]},
        ),
        migrations.RunPython(seed_moderation_status, migrations.RunPython.noop),
    ]