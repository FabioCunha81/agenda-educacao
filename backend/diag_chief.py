import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.accounts.models import User
from apps.schedules.models import Agenda
from apps.schedules.views import chief_agenda_filter
from django.db.models import Q

# Encontrar o chefe teste
test_chiefs = User.objects.filter(email="fabiocunha26@gmail.com")
print("Test chiefs found:", [(u.id, u.full_name, u.cpf, getattr(u.sector, 'name', None) if getattr(u, 'sector_id', None) else None) for u in test_chiefs])

if test_chiefs.exists():
    for user in test_chiefs:
        print(f"\nEvaluating for Chief: {user.full_name}")
        # Agendas associadas a ele
        agendas = Agenda.objects.filter(date="2026-07-05")
        print(f"Total agendas on 05/07: {agendas.count()}")
        for a in agendas:
            print(f"- Agenda {a.id} ({a.date}): OS {a.service_order_number}, chief_name='{a.chief_name}', chief_ref={a.chief_ref_id}, status={a.status}")
        
        # O filtro que a view usa
        filter_q = chief_agenda_filter(user)
        matched = agendas.filter(filter_q)
        print(f"Matched by filter: {matched.count()}")
        for m in matched:
            print(f"   -> {m.id}")

