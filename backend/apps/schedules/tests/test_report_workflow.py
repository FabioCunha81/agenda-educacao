from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.schedules.models import EducationReport, Agenda

User = get_user_model()

class EducationReportWorkflowTests(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(username="admin@teste.com", password="pwd", role=User.Role.ADMIN)
        self.manager = User.objects.create_user(username="manager@teste.com", password="pwd", role=User.Role.MANAGER)
        self.chief = User.objects.create_user(username="chief@teste.com", password="pwd", role=User.Role.CHIEF)
        self.agent = User.objects.create_user(username="agent@teste.com", password="pwd", role=User.Role.AGENT)
        self.visitor = User.objects.create_user(username="visitor@teste.com", password="pwd", role=User.Role.VISITOR)

        # Create agenda
        self.agenda = Agenda.objects.create(
            title="Test Agenda",
            status=Agenda.Status.COMPLETED,
            chief_name="Chief Test",
            date="2026-07-01",
        )

        # Create report as draft
        self.report = EducationReport.objects.create(
            agenda=self.agenda,
            created_by=self.chief,
            status=EducationReport.ReportStatus.DRAFT,
            team="Team A",
        )

    def test_chief_cannot_approve_or_return(self):
        self.client.force_authenticate(user=self.chief)
        self.report.status = EducationReport.ReportStatus.PENDING_REVIEW
        self.report.save()

        response = self.client.post(f"/api/education-reports/{self.report.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(f"/api/education-reports/{self.report.id}/return-for-correction/", {"notes": "fix it"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_agent_and_visitor_cannot_approve(self):
        self.report.status = EducationReport.ReportStatus.PENDING_REVIEW
        self.report.save()

        for user in [self.agent, self.visitor]:
            self.client.force_authenticate(user=user)
            response = self.client.post(f"/api/education-reports/{self.report.id}/approve/")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_approve_and_return(self):
        self.client.force_authenticate(user=self.manager)
        self.report.status = EducationReport.ReportStatus.PENDING_REVIEW
        self.report.save()

        response = self.client.post(f"/api/education-reports/{self.report.id}/return-for-correction/", {"notes": "needs fix"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, EducationReport.ReportStatus.RETURNED)

        self.report.status = EducationReport.ReportStatus.PENDING_REVIEW
        self.report.save()
        
        response = self.client.post(f"/api/education-reports/{self.report.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, EducationReport.ReportStatus.APPROVED)

    def test_cannot_edit_approved_report_via_put_or_patch(self):
        self.client.force_authenticate(user=self.chief)
        self.report.status = EducationReport.ReportStatus.APPROVED
        self.report.save()

        # PUT
        response = self.client.put(f"/api/education-reports/{self.report.id}/", {
            "team": "Team B",
            "agenda": self.agenda.id,
            "actions": []
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # PATCH
        response = self.client.patch(f"/api/education-reports/{self.report.id}/", {
            "team": "Team C",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_cannot_be_changed_via_payload(self):
        self.client.force_authenticate(user=self.chief)
        
        # Try to create directly as APPROVED
        response = self.client.post("/api/education-reports/", {
            "agenda": self.agenda.id,
            "team": "Team D",
            "status": "APPROVED",
            "actions": []
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_report = EducationReport.objects.get(id=response.data["id"])
        self.assertEqual(new_report.status, EducationReport.ReportStatus.DRAFT)

        # Try to patch status to APPROVED
        response = self.client.patch(f"/api/education-reports/{new_report.id}/", {
            "status": "APPROVED"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_report.refresh_from_db()
        self.assertEqual(new_report.status, EducationReport.ReportStatus.DRAFT)
