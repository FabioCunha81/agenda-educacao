from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0039_agenda_public_request_ranges"),
    ]

    operations = [
        migrations.AlterField(
            model_name="educationreport",
            name="breathalyzers",
            field=models.TextField(blank=True),
        ),
    ]
