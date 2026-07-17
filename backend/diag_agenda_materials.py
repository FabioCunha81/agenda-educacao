import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.schedules.models import Agenda, ActionType, Kit, Material, Dynamic, AgendaMaterial, Sector
from apps.schedules.serializers import AgendaSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Limpar db para o teste
Agenda.objects.all().delete()
AgendaMaterial.objects.all().delete()
User.objects.all().delete()
Sector.objects.all().delete()

admin = User.objects.create(email="admin@test.com", role=User.Role.ADMIN, full_name="Admin Test")
sector = Sector.objects.create(name="Sector Test")

agenda = Agenda.objects.create(
    title="Teste Materiais",
    date="2026-07-08",
    start_time="08:00",
    end_time="12:00",
    responsible=admin,
    sector=sector,
    created_by=admin,
    # Material de distribuição (via kit)
    kit_1="CRI-CRI CARNAVAL",
    kit_1_quantity=10,
    # Material de apoio
    material_1="ETILOMETRO",
)

# Criando AgendaMaterial para representar a Dinamica
dyn = Dynamic.objects.create(name="KIT BLITZ EDUCATIVA")
AgendaMaterial.objects.create(
    agenda=agenda,
    dynamic=dyn,
    quantity=1
)

# Renderizando com Serializer
serializer = AgendaSerializer(agenda)
data = serializer.data

print("--- PAYLOAD RETORNADO PELA API (AGENDA) ---")
import json
print(json.dumps(data, indent=2, ensure_ascii=False))

