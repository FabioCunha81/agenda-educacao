from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0038_sync_operational_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="agenda",
            name="accessibility_access",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="agenda",
            name="participant_range",
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
