from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_user_last_activity"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_on_vacation",
            field=models.BooleanField(default=False),
        ),
    ]