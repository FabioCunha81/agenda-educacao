from datetime import date, time

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.schedules.models import (
    Agenda,
    AgendaHistory,
    EducationAction,
    EducationReport,
    EventReport,
    SatisfactionSurvey,
    Sector,
)


class UserDeleteTests(APITestCase):
    def test_delete_user_removes_linked_operational_records(self):
        sector = Sector.objects.create(name="BRAVO")
        admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            full_name="Admin",
            role=User.Role.ADMIN,
        )
        user = User.objects.create_user(
            email="agente@example.com",
            password="password123",
            full_name="Agente",
            role=User.Role.USER,
            sector=sector,
        )
        agenda = Agenda.objects.create(
            title="Acao educativa",
            description="Atividade",
            date=date(2026, 6, 11),
            start_time=time(9, 0),
            end_time=time(10, 0),
            location="Escola",
            responsible=user,
            sector=sector,
            created_by=user,
        )
        AgendaHistory.objects.create(agenda=agenda, changed_by=user, action="Criacao")
        EventReport.objects.create(agenda=agenda, created_by=user, execution_summary="Executado")
        report = EducationReport.objects.create(
            agenda=agenda,
            operation_date=date(2026, 6, 11),
            team="BRAVO",
            created_by=user,
        )
        EducationAction.objects.create(report=report, agenda=agenda)
        SatisfactionSurvey.objects.create(agenda=agenda, report=report, token="survey-token")

        self.client.force_authenticate(admin)
        response = self.client.delete(reverse("users-detail", args=[user.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(id=user.id).exists())
        self.assertFalse(Agenda.objects.filter(id=agenda.id).exists())
        self.assertFalse(AgendaHistory.objects.exists())
        self.assertFalse(EventReport.objects.exists())
        self.assertFalse(EducationReport.objects.exists())
        self.assertFalse(EducationAction.objects.exists())
        self.assertFalse(SatisfactionSurvey.objects.exists())
