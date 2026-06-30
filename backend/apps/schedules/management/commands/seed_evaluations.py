import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
import uuid

from apps.schedules.models import Agenda, SatisfactionSurvey

class Command(BaseCommand):
    help = "Popula o banco com dados fictícios de Avaliações (SatisfactionSurvey)."

    def handle(self, *args, **options):
        from apps.schedules.models import Team, SatisfactionSurvey
        from apps.accounts.models import User
        
        # Corrige codificação e deixa tudo em caixa alta no banco existente
        surveys_to_update = SatisfactionSurvey.objects.exclude(team="")
        for survey in surveys_to_update:
            original = survey.team
            new_team = original.replace("ÃƒÂ§ÃƒÂµes", "ÇÕES").replace("ÃƒÂ§ÃƒÂ£o", "ÇÃO").replace("ÃƒÂ©", "É").replace("ÃƒÂ", "Í")
            new_team = new_team.upper()
            if original != new_team:
                survey.team = new_team
                survey.save(update_fields=["team"])
        
        agendas = list(Agenda.objects.all()[:20])
        
        if not agendas:
            self.stdout.write(self.style.ERROR("Nenhuma agenda encontrada para vincular avaliações. Crie agendas primeiro."))
            return

        teams = list(Team.objects.values_list("name", flat=True))
        teams = [t.upper() for t in teams if t]
        if not teams:
            teams = ["ALFA", "BETA", "GAMA", "DELTA"]
            
        users = list(User.objects.values_list("full_name", flat=True))
        if not users:
            users = ["João Silva", "Maria Oliveira"]

        suggestions = [
            "Excelente palestra, muito informativa.",
            "Poderia ter mais interação com o público.",
            "O material de apoio estava ótimo.",
            "Gostei muito da dinâmica, equipe nota 10!",
            "O tempo foi um pouco curto para tanto conteúdo.",
            "",
            "Tudo perfeito, parabéns a todos."
        ]

        created_count = 0

        for i, agenda in enumerate(agendas):
            # Generate random scores between 3 and 5 for a realistic "good" distribution, with some 1s and 2s
            token = str(uuid.uuid4())
            answered = random.choice([True, False])
            
            survey, created = SatisfactionSurvey.objects.get_or_create(
                agenda=agenda,
                defaults={
                    "token": token,
                    "requester_email": f"participante{i}@exemplo.com",
                    "team": random.choice(teams),
                    "chief_name": random.choice(users),
                    "audiovisual_resources": random.randint(3, 5) if answered else None,
                    "speaker_knowledge": random.randint(4, 5) if answered else None,
                    "wheelchair_testimony": random.randint(3, 5) if answered else None,
                    "workshops": random.randint(3, 5) if answered else None,
                    "support_material": random.randint(3, 5) if answered else None,
                    "punctuality": random.randint(2, 5) if answered else None,
                    "team_enthusiasm": random.randint(4, 5) if answered else None,
                    "overall_rating": random.randint(3, 5) if answered else None,
                    "suggestion": random.choice(suggestions) if answered else "",
                    "sent_at": now() - timedelta(days=random.randint(1, 10)),
                    "answered_at": now() - timedelta(days=random.randint(0, 5)) if answered else None,
                    "is_approved": answered and random.choice([True, True, False]),
                    "moderation_status": SatisfactionSurvey.ModerationStatus.APPROVED if answered else SatisfactionSurvey.ModerationStatus.PENDING,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"{created_count} avaliações fictícias criadas com sucesso."))
