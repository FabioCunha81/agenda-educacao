import os

from django.core.management import call_command
from django.db import migrations


SYNC_VERSION = "2026-06-19-1"


def sync_operational_data(apps, schema_editor):
    if os.environ.get("RENDER", "").lower() in {"1", "true", "yes"}:
        call_command("sync_operational_data", sync_version=SYNC_VERSION)


class Migration(migrations.Migration):
    dependencies = [
        ("schedules", "0037_shiftabsence_and_more"),
    ]

    operations = [
        migrations.RunPython(sync_operational_data, migrations.RunPython.noop),
    ]
