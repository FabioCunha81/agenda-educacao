import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.schedules.models import Agenda

def main():
    today = timezone.localtime(timezone.now()).date()
    
    # Busca agendas antigas (antes de hoje) que NAO estejam canceladas ou concluidas
    agendas = Agenda.objects.filter(date__lt=today).exclude(status__in=[Agenda.Status.COMPLETED, Agenda.Status.CANCELLED])
    
    count = agendas.update(status=Agenda.Status.COMPLETED)
    
    print(f"Sucesso! {count} agendas antigas foram marcadas como CONCLUIDAS.")

if __name__ == "__main__":
    main()
