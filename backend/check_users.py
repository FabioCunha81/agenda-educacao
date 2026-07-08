import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.accounts.models import User

print("Total users:", User.objects.count())
print("Operational users:", User.objects.exclude(role__in=["ADMIN", "MANAGER", "VISITOR"]).count())
