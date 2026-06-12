from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0027_shiftschedule_shiftswaprequest_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shiftswaprequest",
            name="attachment",
            field=models.FileField(blank=True, null=True, upload_to="shift_swaps/"),
        ),
    ]
