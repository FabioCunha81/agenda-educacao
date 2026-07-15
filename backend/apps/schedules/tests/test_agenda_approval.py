from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.schedules.models import Agenda, Sector

User = get_user_model()

class AgendaApprovalTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@teste.com", password="pwd", role=User.Role.ADMIN)
        self.sector = Sector.objects.create(name="Test Sector")

        self.agenda_with_desc = Agenda.objects.create(
            title="Agenda Com Descrição",
            description="Descrição válida que não deve ser perdida.",
            status=Agenda.Status.PENDING,
            date="2026-07-15",
            start_time="08:00:00",
            end_time="12:00:00",
            created_by=self.admin,
            responsible=self.admin,
            sector=self.sector,
        )

        self.agenda_without_desc = Agenda.objects.create(
            title="Agenda Sem Descrição",
            description="",  # Simulated legacy or incomplete record
            status=Agenda.Status.PENDING,
            date="2026-07-16",
            start_time="09:00:00",
            end_time="13:00:00",
            created_by=self.admin,
            responsible=self.admin,
            sector=self.sector,
        )

    def test_patch_approval_preserves_description(self):
        """ PATCH sem enviar o campo description preserva a descrição existente """
        self.client.force_authenticate(user=self.admin)
        
        url = f"/api/agendas/{self.agenda_with_desc.id}/"
        payload = {
            "status": Agenda.Status.APPROVED
        }
        
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.agenda_with_desc.refresh_from_db()
        self.assertEqual(self.agenda_with_desc.status, Agenda.Status.APPROVED)
        self.assertEqual(self.agenda_with_desc.description, "Descrição válida que não deve ser perdida.")

    def test_put_approval_fails_if_description_is_empty(self):
        """ PUT enviando description vazia deve falhar """
        self.client.force_authenticate(user=self.admin)
        
        url = f"/api/agendas/{self.agenda_with_desc.id}/"
        payload = {
            "title": self.agenda_with_desc.title,
            "description": "",
            "status": Agenda.Status.APPROVED,
            "date": "2026-07-15",
            "start_time": "08:00:00",
            "end_time": "12:00:00",
            "responsible": self.admin.id,
            "sector": self.sector.id
        }
        
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    def test_patch_approval_allows_empty_description_if_omitted(self):
        """ PATCH omitindo a descrição permite aprovar, mesmo se banco estava vazio. 
            O Frontend agora exige preenchimento e enviará no PATCH se o usuário preencher. """
        self.client.force_authenticate(user=self.admin)
        
        url = f"/api/agendas/{self.agenda_without_desc.id}/"
        payload = {
            "status": Agenda.Status.APPROVED
        }
        
        # In DRF, PATCH skips validation of omitted fields.
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.agenda_without_desc.refresh_from_db()
        self.assertEqual(self.agenda_without_desc.status, Agenda.Status.APPROVED)
