# Deploy no Render

O repositorio inclui `render.yaml` para criar:

- `agenda-educacao-api`: backend Django.
- `agenda-educacao-web`: frontend estatico Vite.
- `agenda-educacao-db`: PostgreSQL.

No Render, use **New > Blueprint**, selecione este repositorio e confirme a criacao dos servicos.

Depois que os servicos forem criados, ajuste as variaveis:

- No backend `agenda-educacao-api`:
  - `FRONTEND_URL`: URL publica do static site, por exemplo `https://agenda-educacao-web.onrender.com`.
  - `CORS_ALLOWED_ORIGINS`: mesma URL do frontend.
  - `DJANGO_SUPERUSER_EMAIL`: e-mail inicial, por padrao `admin@agenda.local`.
  - `DJANGO_SUPERUSER_PASSWORD`: senha inicial. Se nao for definida, o padrao e `Admin@12345`.
  - `DJANGO_SUPERUSER_FULL_NAME`: nome exibido, por padrao `Admin Agenda`.
  - variaveis `EMAIL_*`, se houver SMTP real.
- No frontend `agenda-educacao-web`:
  - `VITE_API_URL`: URL da API com `/api`, por exemplo `https://agenda-educacao-api.onrender.com/api`.

O backend roda automaticamente `python manage.py bootstrap_admin` depois das migracoes. O comando e idempotente: ele cria o administrador se nao existir e garante que ele continue ativo, staff e superuser.

Por seguranca, depois do primeiro acesso em producao troque a senha ou defina `DJANGO_SUPERUSER_PASSWORD` no Render antes do deploy.
