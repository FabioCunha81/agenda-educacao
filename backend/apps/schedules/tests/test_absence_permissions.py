from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from apps.schedules.models import ShiftSchedule, Team, Chief, Agent, Support, Sector
import datetime

class ShiftScheduleAbsencePermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.sector = Sector.objects.create(name="Equipe 1")
        self.other_sector = Sector.objects.create(name="Equipe 2")
        
        # Admin / Manager
        self.admin = User.objects.create_user(email="admin@test.com", password="123", role=User.Role.ADMIN)
        self.manager = User.objects.create_user(email="manager@test.com", password="123", role=User.Role.MANAGER)
        
        # Team 1 Chiefs
        self.chief_titular = User.objects.create_user(email="chief1@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Joao", sector=self.sector, cpf="11122233344")
        self.chief_removido = User.objects.create_user(email="chief_rem@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Removido", sector=self.sector, cpf="00011122233")
        self.chief_mesmo_nome = User.objects.create_user(email="chief2@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Joao", sector=self.sector, cpf="99988877766")
        self.chief_sem_cpf = User.objects.create_user(email="chief_nocpf@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Sem CPF", sector=self.sector)
        self.chief_cpf_pontuado = User.objects.create_user(email="chief_pont@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Pontuado", sector=self.sector, cpf="22233344455")
        
        # Team 2 Chief (Extra)
        self.chief_extra = User.objects.create_user(email="chief_extra@test.com", password="123", role=User.Role.SUPERVISOR, full_name="Chefe Extra", sector=self.other_sector, cpf="33344455566")
        
        # Other roles
        self.agent = User.objects.create_user(email="agent@test.com", password="123", role=User.Role.USER, full_name="Agente", sector=self.sector)
        self.support = User.objects.create_user(email="support@test.com", password="123", role=User.Role.SUPPORT, full_name="Apoio", sector=self.sector)
        self.visitor = User.objects.create_user(email="visitor@test.com", password="123", role=User.Role.VISITOR, full_name="Visitante", sector=self.sector)
        
        # Models for users
        self.c_titular = Chief.objects.create(name="Chefe Joao (Titular)", source_id=f"user:{self.chief_titular.id}", cpf="11122233344")
        self.c_removido = Chief.objects.create(name="Chefe Removido", source_id=f"user:{self.chief_removido.id}", cpf="00011122233")
        self.c_mesmo_nome = Chief.objects.create(name="Chefe Joao (Falso)", source_id=f"user:{self.chief_mesmo_nome.id}", cpf="99988877766")
        self.c_sem_cpf = Chief.objects.create(name="Chefe Sem CPF", source_id=f"user:{self.chief_sem_cpf.id}")
        self.c_cpf_pontuado = Chief.objects.create(name="Chefe Pontuado", source_id=f"user:{self.chief_cpf_pontuado.id}", cpf="222.333.444-55") # Pontuado no cadastro
        
        self.c_extra = Chief.objects.create(name="Chefe Extra", source_id=f"user:{self.chief_extra.id}", cpf="33344455566")
        
        # Create Teams and link chiefs
        self.team = Team.objects.create(name="Equipe 1")
        self.c_titular.team = self.team
        self.c_titular.save()
        self.c_removido.team = self.team
        self.c_removido.save()
        self.c_mesmo_nome.team = self.team
        self.c_mesmo_nome.save()
        self.c_sem_cpf.team = self.team
        self.c_sem_cpf.save()
        self.c_cpf_pontuado.team = self.team
        self.c_cpf_pontuado.save()
        
        self.other_team = Team.objects.create(name="Equipe 2")
        self.c_extra.team = self.other_team
        self.c_extra.save()
        
        self.schedule = ShiftSchedule.objects.create(
            date=datetime.date(2026, 7, 10),
            team=self.team,
            created_by=self.admin
        )
        
        self.schedule.extra_chiefs.add(self.c_extra)
        self.schedule.removed_chiefs.add(self.c_removido)
        self.schedule.removed_chiefs.add(self.c_mesmo_nome)
        
        self.url = f"/api/shift-schedules/{self.schedule.id}/absence/"

    def do_post(self, user):
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, {"member_type": "CHIEF", "member_id": self.c_titular.id, "reason": "Faltou"})

    def do_delete(self, user):
        self.client.force_authenticate(user=user)
        return self.client.delete(self.url, {"member_type": "CHIEF", "member_id": self.c_titular.id})

    def test_admin_can_manage_absence(self):
        res = self.do_post(self.admin)
        if res.status_code != 200:
            print("ADMIN 404 INFO:", res.data if hasattr(res, 'data') else res.content)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_manager_can_manage_absence(self):
        res = self.do_post(self.manager)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_chief_titular_can_manage_absence(self):
        res = self.do_post(self.chief_titular)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_chief_extra_can_manage_absence(self):
        res = self.do_post(self.chief_extra)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_chief_removido_receives_403(self):
        res = self.do_post(self.chief_removido)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_chief_same_name_different_cpf_receives_403(self):
        res = self.do_post(self.chief_mesmo_nome)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_chief_cpf_pontuado_is_recognized(self):
        res = self.do_post(self.chief_cpf_pontuado)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_chief_sem_cpf_is_recognized_by_source_id(self):
        res = self.do_post(self.chief_sem_cpf)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_agent_and_support_receive_403(self):
        res = self.do_post(self.agent)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.do_post(self.support)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_chief_cannot_delete_schedule(self):
        self.client.force_authenticate(user=self.chief_titular)
        res = self.client.delete(f"/api/shift-schedules/{self.schedule.id}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_gets_403(self):
        res = self.do_post(self.agent)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_gets_403(self):
        res = self.do_post(self.support)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_visitor_gets_403(self):
        res = self.do_post(self.visitor)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_edition_actions_blocked_for_chief(self):
        self.client.force_authenticate(user=self.chief_titular)
        # Update schedule (patch)
        res = self.client.patch(f"/api/shift-schedules/{self.schedule.id}/", {"date": "2026-08-01"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_legacy_visibility(self):
        self.client.force_authenticate(user=self.agent)
        from apps.schedules.models import Agent
        a_legacy = Agent.objects.create(name="Agente", team=self.team)
        self.team.agents.add(a_legacy)
        
        # Agents might not have access to view a specific schedule unless they are in the team.
        # ShiftScheduleViewSet get_queryset handles this.
        # We need to test the /api/schedules/ endpoint but wait, this is a ModelViewSet for shift-schedules.
        res = self.client.get("/api/shift-schedules/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check if the schedule is in the results
        # Depending on pagination it might be inside results
        data = res.data.get('results', res.data) if isinstance(res.data, dict) else res.data
        self.assertTrue(len(data) > 0)
        
    def test_support_legacy_visibility(self):
        self.client.force_authenticate(user=self.support)
        from apps.schedules.models import Support
        s_legacy = Support.objects.create(name="Apoio", team=self.team)
        self.team.supports.add(s_legacy)
        
        res = self.client.get("/api/shift-schedules/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data.get('results', res.data) if isinstance(res.data, dict) else res.data
        self.assertTrue(len(data) > 0)
        
        # Delete schedule
        res2 = self.client.delete(f"/api/shift-schedules/{self.schedule.id}/")
        self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)
