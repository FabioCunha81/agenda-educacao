from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError

from config.email_delivery import send_email_message


class Command(BaseCommand):
    help = "Envia um e-mail de teste usando as configuracoes SMTP atuais."

    def add_arguments(self, parser):
        parser.add_argument("to", help="E-mail de destino para o teste.")

    def handle(self, *args, **options):
        recipient = options["to"].strip()
        if not recipient:
            raise CommandError("Informe um e-mail de destino.")

        self.stdout.write("Configuracao SMTP atual:")
        self.stdout.write(f"  EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  EMAIL_HOST_USER definido: {bool(settings.EMAIL_HOST_USER)}")
        self.stdout.write(f"  EMAIL_HOST_PASSWORD definido: {bool(settings.EMAIL_HOST_PASSWORD)}")
        self.stdout.write(f"  RESEND_API_KEY definido: {bool(settings.RESEND_API_KEY)}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"  AGENDA_REPLY_TO_EMAIL: {settings.AGENDA_REPLY_TO_EMAIL}")

        message = EmailMessage(
            subject="Teste de e-mail - Agenda Educacao",
            body=(
                "Este e um e-mail de teste do Agenda Educacao.\n\n"
                f"EMAIL_HOST: {settings.EMAIL_HOST}\n"
                f"EMAIL_PORT: {settings.EMAIL_PORT}\n"
                f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}\n"
                f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}\n"
                f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[settings.AGENDA_REPLY_TO_EMAIL] if settings.AGENDA_REPLY_TO_EMAIL else None,
        )
        sent, detail = send_email_message(message)
        if not sent:
            raise CommandError(f"Falha no envio do e-mail de teste: {detail}")
        self.stdout.write(self.style.SUCCESS("E-mail de teste enviado: 1"))
