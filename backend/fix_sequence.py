import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management.color import no_style
from django.db import connection
from apps.schedules.models import Agenda, EducationReport, EducationAction

def main():
    print("Corrigindo sequencias do banco de dados...")
    models = [Agenda, EducationReport, EducationAction]
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            print(f"Executando: {sql}")
            cursor.execute(sql)
    print("Sucesso! As sequencias foram atualizadas.")

if __name__ == "__main__":
    main()
