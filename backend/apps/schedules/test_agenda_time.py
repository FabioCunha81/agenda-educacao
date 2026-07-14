from datetime import date, time
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User
from apps.schedules.models import Agenda, Sector
from apps.schedules.serializers import AgendaSerializer

class AgendaTimeValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", cpf="11111111111")
        self.sector = Sector.objects.create(name="Test Sector")

    def test_acao_de_rua_4_hours_duration(self):
        # 08:00 → 12:00
        serializer = AgendaSerializer(data={
            "title": "Ação",
            "date": "2026-08-01",
            "start_time": "08:00:00",
            "end_time": "10:00:00", # Should be ignored and recalculated
            "requester_entity_type": "6",
            "description": "Test",
            "location": "Local",
            "responsible": self.user.id,
            "sector": self.sector.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["end_time"], time(12, 0))

    def test_acao_de_rua_cross_midnight(self):
        # 22:00 → 02:00
        serializer = AgendaSerializer(data={
            "title": "Ação Noturna",
            "date": "2026-08-01",
            "start_time": "22:00:00",
            "end_time": "00:00:00",
            "requester_entity_type": "6",
            "description": "Test",
            "location": "Local",
            "responsible": self.user.id,
            "sector": self.sector.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["end_time"], time(2, 0))
        
    def test_acao_de_rua_cross_midnight_2345(self):
        # 23:45 → 03:45
        serializer = AgendaSerializer(data={
            "title": "Ação Madrugada",
            "date": "2026-08-01",
            "start_time": "23:45:00",
            "end_time": "00:00:00",
            "requester_entity_type": "6",
            "description": "Test",
            "location": "Local",
            "responsible": self.user.id,
            "sector": self.sector.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["end_time"], time(3, 45))

    def test_normal_agenda_rejects_same_time(self):
        serializer = AgendaSerializer(data={
            "title": "Ação",
            "date": "2026-08-01",
            "start_time": "08:00:00",
            "end_time": "08:00:00",
            "requester_entity_type": "Outro",
            "description": "Test",
            "location": "Local",
            "responsible": self.user.id,
            "sector": self.sector.id,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_time", serializer.errors)

    def test_invalid_time_format_handled_by_drf(self):
        serializer = AgendaSerializer(data={
            "title": "Ação",
            "date": "2026-08-01",
            "start_time": "18:30 PM", # Invalid DRF time format, DRF will reject
            "end_time": "10:00:00",
            "requester_entity_type": "Outro",
            "description": "Test",
            "location": "Local",
            "responsible": self.user.id,
            "sector": self.sector.id,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("start_time", serializer.errors)
