from django.db import migrations


DEFAULT_SECTORS = [
    "Educacao",
    "Alfa",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
    "Golf",
    "Hotel",
]


def seed_default_user_sectors(apps, schema_editor):
    Sector = apps.get_model("schedules", "Sector")
    for name in DEFAULT_SECTORS:
        Sector.objects.get_or_create(
            name=name,
            defaults={"description": "Equipe para vinculo de usuarios", "is_active": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0022_satisfactionsurvey"),
    ]

    operations = [
        migrations.RunPython(seed_default_user_sectors, migrations.RunPython.noop),
    ]
