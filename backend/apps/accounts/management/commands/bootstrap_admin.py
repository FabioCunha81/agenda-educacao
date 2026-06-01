import os

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Cria ou atualiza o administrador inicial da aplicacao."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@agenda.local"),
            help="E-mail do administrador inicial.",
        )
        parser.add_argument(
            "--password",
            default=os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin@12345"),
            help="Senha do administrador inicial.",
        )
        parser.add_argument(
            "--name",
            default=os.environ.get("DJANGO_SUPERUSER_FULL_NAME", "Admin Agenda"),
            help="Nome completo do administrador inicial.",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        name = options["name"].strip()

        if not email:
            raise CommandError("Informe um e-mail para o administrador inicial.")
        if not password:
            raise CommandError("Informe uma senha para o administrador inicial.")
        if len(password) < 8:
            raise CommandError("A senha do administrador inicial deve ter pelo menos 8 caracteres.")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "full_name": name or email,
                "role": User.Role.ADMIN,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed_fields = []
        desired_values = {
            "username": email,
            "full_name": name or user.full_name or email,
            "role": User.Role.ADMIN,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        }
        for field, value in desired_values.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed_fields.append(field)

        if created or not user.has_usable_password():
            user.set_password(password)
            changed_fields.append("password")

        if changed_fields:
            user.save(update_fields=sorted(set(changed_fields)))

        action = "criado" if created else "verificado"
        self.stdout.write(self.style.SUCCESS(f"Administrador inicial {action}: {email}"))
