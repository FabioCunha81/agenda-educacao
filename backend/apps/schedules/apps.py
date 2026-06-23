import os
import threading
import time
from django.apps import AppConfig

def run_accessibility_processor():
    from .accessibility import process_due_accessibility_rejections
    while True:
        try:
            process_due_accessibility_rejections()
        except Exception:
            pass
        time.sleep(60)

class SchedulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.schedules"

    def ready(self):
        # Prevent running in migrations or collectstatic
        if os.environ.get("RUN_MAIN", None) != "false":
            t = threading.Thread(target=run_accessibility_processor, daemon=True)
            t.start()
