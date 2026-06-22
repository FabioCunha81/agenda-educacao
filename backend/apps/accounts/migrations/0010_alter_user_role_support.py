from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Administrador"),
                    ("MANAGER", "Gestor"),
                    ("SUPERVISOR", "Supervisor"),
                    ("VISITOR", "Visitante"),
                    ("USER", "Usuário comum"),
                    ("SUPPORT", "Apoio"),
                ],
                default="USER",
                max_length=20,
            ),
        ),
    ]
