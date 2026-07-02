import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.schedules.models import Agenda
from django.db.models import Q

def main():
    # Define a rule for what a request is
    request_source_filter = (
        Q(origin=Agenda.Origin.PUBLIC_FORM)
        | Q(source_id__startswith="internal-request:")
        | Q(source_id__startswith="appsheet:")
        | Q(sector__name__in=["Solicitacoes externas", "Solicitacoes internas"])
        | Q(created_by__email="solicitacao.publica@agenda.local")
        | Q(responsible__email="solicitacao.publica@agenda.local")
    )
    
    # Busca solicitacoes pendentes enviadas (created_at) antes de 01/07/2026
    old_requests = Agenda.objects.filter(
        request_source_filter,
        status=Agenda.Status.PENDING,
        created_at__lt='2026-07-01'
    )
    
    count = old_requests.update(status=Agenda.Status.CANCELLED)
    
    print(f"Sucesso! {count} solicitacoes enviadas antes de 01/07 foram Ocultadas (Canceladas).")

if __name__ == "__main__":
    main()
