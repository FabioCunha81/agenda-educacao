import sys

with open('backend/apps/schedules/views.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'pending_moderation_count = SatisfactionSurvey.objects.filter(agenda__in=base_qs, answered_at__isnull=False, is_approved=False).exclude(suggestion="").count()',
    'pending_moderation_count = SatisfactionSurvey.objects.filter(agenda__in=base_qs, answered_at__isnull=False, is_approved=False).exclude(suggestion="").count()\n        now_dt = timezone.localtime(timezone.now())\n        if now_dt.hour >= 18:\n            reportable_agendas = base_qs.filter(date__lte=now_dt.date())\n        else:\n            reportable_agendas = base_qs.filter(date__lt=now_dt.date())\n        pending_technical_reports_count = reportable_agendas.exclude(status__in=[Agenda.Status.COMPLETED, Agenda.Status.CANCELLED]).filter(technical_reports__isnull=True).count()'
)

c = c.replace(
    '"pending_moderation_count": pending_moderation_count,',
    '"pending_moderation_count": pending_moderation_count,\n            "pending_technical_reports_count": pending_technical_reports_count,'
)

with open('backend/apps/schedules/views.py', 'w', encoding='utf-8') as f:
    f.write(c)
