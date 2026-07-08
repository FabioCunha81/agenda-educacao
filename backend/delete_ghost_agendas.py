import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.schedules.models import Agenda
from django.db.models import Q

def clean_ghost_agendas():
    # Looking for agendas that are cancelled AND have no meaningful institution/requester
    ghosts = Agenda.objects.filter(
        status=Agenda.Status.CANCELLED
    ).filter(
        Q(institution_location__in=["", "-", None]) &
        Q(external_responsible__in=["", "-", None])
    )
    
    count = ghosts.count()
    if count > 0:
        print(f"Encontradas {count} solicitações 'fantasmas' (sem dados e canceladas).")
        # We must first delete related objects that protect the Agenda
        from apps.schedules.models import EducationReport, SatisfactionSurvey
        reports = EducationReport.objects.filter(agenda__in=ghosts)
        surveys = SatisfactionSurvey.objects.filter(agenda__in=ghosts)
        
        rcount, _ = reports.delete()
        scount, _ = surveys.delete()
        
        print(f"Apagados {rcount} relatórios técnicos e {scount} avaliações associadas.")
        
        # Now we can safely delete the agendas
        deleted_count, _ = ghosts.delete()
        print(f"Limpeza concluída! Foram apagados {deleted_count} registros de agenda do banco.")
    else:
        print("Nenhuma solicitação 'fantasma' foi encontrada.")

if __name__ == "__main__":
    clean_ghost_agendas()
