from django.db import migrations


SYNC_VERSION = "2026-06-19-1"


def sync_operational_data(apps, schema_editor):
    # The Render start command runs this after bootstrap_admin creates the admin user.
    return


class Migration(migrations.Migration):
    dependencies = [
        ("schedules", "0037_shiftabsence_and_more"),
    ]

    operations = [
        migrations.RunPython(sync_operational_data, migrations.RunPython.noop),
    ]