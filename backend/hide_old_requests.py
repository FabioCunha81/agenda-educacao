import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.schedules.models import Agenda
from django.db.models import Q

def main():
    # Encontra solicitacoes pendentes que vieram de importacao de formularios
    # e estao com a instituicao ou solicitante em branco (os tracinhos na tela)
    ghost_requests = Agenda.objects.filter(
        status=Agenda.Status.PENDING,
        origin=Agenda.Origin.PUBLIC_FORM
    ).filter(
        Q(institution_location="") | Q(institution_location__isnull=True) |
        Q(external_responsible="") | Q(external_responsible__isnull=True)
    )
    
    count = ghost_requests.update(status=Agenda.Status.CANCELLED)
    
    # Tambem ocultamos qualquer coisa do AppSheet antigo que esteja pendente
    old_appsheet = Agenda.objects.filter(
        status=Agenda.Status.PENDING,
        source_id__startswith="appsheet:"
    )
    count_appsheet = old_appsheet.update(status=Agenda.Status.CANCELLED)
    
    print(f"Sucesso! {count} solicitacoes sem dados do Forms foram Ocultadas.")
    print(f"Sucesso! {count_appsheet} solicitacoes do AppSheet antigo foram Ocultadas.")

if __name__ == "__main__":
    main()
