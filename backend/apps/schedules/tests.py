from datetime import date, time

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.schedules.models import Agenda, Agent, Sector


class AgendaAccessTests(APITestCase):
    def test_agent_user_can_list_agenda_where_they_are_scheduled(self):
        sector = Sector.objects.create(name="ALFA")
        manager = User.objects.create_user(
            email="gestor@example.com",
            password="password123",
            full_name="Gestor OLS",
            role=User.Role.MANAGER,
            sector=sector,
        )
        agent_user = User.objects.create_user(
            email="agente@example.com",
            password="password123",
            full_name="Agente Escalado",
            cpf="12345678901",
            role=User.Role.USER,
        )
        agent = Agent.objects.create(name="Agente Escalado", cpf="12345678901", is_active=True)
        agenda = Agenda.objects.create(
            title="Palestra educativa",
            description="Atividade agendada",
            date=date(2026, 6, 10),
            start_time=time(9, 0),
            end_time=time(10, 0),
            location="Escola Municipal",
            responsible=manager,
            sector=sector,
            created_by=manager,
        )
        agenda.agents_ref.add(agent)

        self.client.force_authenticate(agent_user)
        response = self.client.get(
            reverse("agendas-list"),
            {"date_from": "2026-06-01", "date_to": "2026-06-30"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        rows = payload["results"] if "results" in payload else payload
        self.assertEqual([row["id"] for row in rows], [agenda.id])
