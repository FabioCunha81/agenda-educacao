from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.schedules.models import ShiftSchedule, Team, Agent, Chief

class ShiftSchedulePermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.team1, _ = Team.objects.get_or_create(name="ALFA")
        self.team2, _ = Team.objects.get_or_create(name="BRAVO")

        self.admin = User.objects.create_user(
            email="admin@test.com", password="pwd", role="ADMIN", full_name="Admin User"
        )
        self.no_link_user = User.objects.create_user(
            email="none@test.com", password="pwd", role="USER", full_name="John Doe", cpf="111.111.111-11"
        )
        
        self.agent1_user = User.objects.create_user(
            email="agent1@test.com", password="pwd", role="USER", full_name="Carlos Silva", cpf="222.222.222-22"
        )
        self.agent2_user_same_name = User.objects.create_user(
            email="agent2@test.com", password="pwd", role="USER", full_name="Carlos Silva", cpf="333.333.333-33"
        )
        self.agent_empty_cpf = User.objects.create_user(
            email="empty_cpf@test.com", password="pwd", role="USER", full_name="Pedro Paulo", cpf=""
        )

        self.agent_record = Agent.objects.create(
            name="Carlos Silva", cpf="22222222222", source_id="user:9999"  # Simulando source_id diferente ou legado
        )
        self.agent_record2 = Agent.objects.create(
            name="Pedro Paulo", cpf="44444444444", source_id="user:8888" # CPF diferente, source diferente, mesmo nome de agent_empty_cpf
        )

        self.schedule_alfa = ShiftSchedule.objects.create(
            date=date(2026, 7, 10), team=self.team1, created_by=self.admin
        )
        self.schedule_alfa.extra_agents.add(self.agent_record)
        
        self.schedule_bravo = ShiftSchedule.objects.create(
            date=date(2026, 7, 11), team=self.team2, created_by=self.admin
        )
        self.schedule_bravo.extra_agents.add(self.agent_record2)

        self.url = reverse('shift-schedules-list')

    def test_admin_sees_all(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_no_link_user_sees_none(self):
        self.client.force_authenticate(user=self.no_link_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Deve ser None e não vazar escalas!
        self.assertEqual(len(res.data['results']), 0)

    def test_fallback_cpf_matches_properly(self):
        # Carlos Silva com CPF 222 tem que ver a escala ALFA pelo fallback de CPF
        self.client.force_authenticate(user=self.agent1_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['team_name'], "ALFA")

    def test_same_name_different_cpf_does_not_share_schedule(self):
        # Carlos Silva com CPF 333 (não cadastrado como Agent com esse CPF) 
        # NÃO pode ver a escala do Carlos Silva do CPF 222
        self.client.force_authenticate(user=self.agent2_user_same_name)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_empty_cpf_does_not_match_by_name_alone(self):
        # Pedro Paulo não tem CPF e não tem setor associado. 
        # Mesmo existindo um Agent "Pedro Paulo" com CPF 444, ele não deve cruzar dados
        self.client.force_authenticate(user=self.agent_empty_cpf)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_empty_cpf_matches_by_name_and_sector(self):
        # Se Pedro Paulo não tem CPF, ele só cruza se o nome for idêntico e a equipe for idêntica
        from apps.schedules.models import Sector
        sector, _ = Sector.objects.get_or_create(name="BRAVO")
        self.agent_empty_cpf.sector = sector
        self.agent_empty_cpf.save()
        self.client.force_authenticate(user=self.agent_empty_cpf)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ele bate por team_id de qualquer jeito (porque q_filter |= team_id=user.sector_id)
        # Mas o fallback do agent_ids também vai rolar porque name e team_id batem
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['team_name'], "BRAVO")
