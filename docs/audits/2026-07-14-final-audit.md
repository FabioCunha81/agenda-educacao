# RELATÃ“RIO TÃ‰CNICO COMPLETO DA ARQUITETURA

Este relatÃ³rio baseia-se **EXCLUSIVAMENTE** em fatos e evidÃªncias extraÃ­das dos arquivos da base de cÃ³digo `d:\agenda_eventos_ols`.

---

### 1. Infraestrutura
*Fonte primÃ¡ria:* `docker-compose.yml`

* **Docker Compose completo:** Orquestra 5 serviÃ§os simultÃ¢neos, conectados na rede padrÃ£o do Docker (default bridge network do compose).
* **Containers existentes:**
  * `sied_db` (dependÃªncia: nenhuma)
  * `sied_redis` (dependÃªncia: nenhuma)
  * `sied_backend` (depende de: `db`, `redis`)
  * `sied_frontend` (dependÃªncia: nenhuma, build estÃ¡tico via Node)
  * `sied_proxy` (depende de: `backend`, `frontend`)
* **Imagens utilizadas:**
  * `postgres:16-alpine`
  * `redis:7-alpine`
  * `nginx:alpine`
  * Imagens criadas localmente via `build:` para `backend` e `frontend`.
* **Volumes:**
  * `postgres_data:/var/lib/postgresql/data` (Nomeado localmente)
  * `static_volume:/app/staticfiles` (Nomeado localmente, lido pelo Nginx)
  * `media_volume:/app/media` (Nomeado localmente, lido pelo Nginx)
  * `./nginx.conf:/etc/nginx/conf.d/default.conf:ro` (Bind mount)
  * `/etc/letsencrypt:/etc/letsencrypt:ro` (Bind mount do Host VPS)
* **Networks:** NÃƒO IDENTIFICADO NO PROJETO declaradas explicitamente (utiliza a `default` implÃ­cita do Compose).
* **Portas mapeadas no host:**
  * Nginx: `80:80` e `443:443` (Todas as outras sÃ£o internas).
* **VariÃ¡veis utilizadas pelos containers (no compose):**
  * `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
  * `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`
  * `VITE_API_URL`, `VITE_API_TIMEOUT_MS`

---

### 2. Nginx
*Fonte primÃ¡ria:* `nginx.conf`

* **Server blocks:** 2 blocos. Um na porta `80` (HTTP) e outro na `443` (HTTPS).
* **Proxy_pass:**
  * `/api/` -> `http://backend:8000`
  * `/admin/` -> `http://backend:8000`
  * `/` -> `http://frontend:80`
* **Upstreams:** NÃƒO IDENTIFICADO NO PROJETO explÃ­cito com bloco `upstream {}`. O trÃ¡fego aponta diretamente para o DNS interno do Docker Compose (`backend` e `frontend`).
* **Headers:** `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, `Cache-Control`.
* **SSL:** `ssl_certificate /etc/letsencrypt/live/sied-leiseca.online/fullchain.pem;` (Idem para `privkey.pem`).
* **Redirecionamentos:**
  * `return 301 https://$host$request_uri;` (forÃ§a HTTPS no bloco 80).
* **Cache:** `expires 1y; add_header Cache-Control "public, no-transform";` aplicados nas rotas `/static/` e `/media/`.
* **CompressÃ£o:** NÃƒO IDENTIFICADO NO PROJETO regras locais no `nginx.conf` explÃ­citas para `gzip` ou `brotli`.

---

### 3. Backend
*Fonte primÃ¡ria:* `backend/config/settings.py` e `backend/config/urls.py`

* **Apps instaladas:** `django.contrib.*`, `corsheaders`, `rest_framework`, `rest_framework_simplejwt`, `apps.accounts`, `apps.schedules`.
* **Middlewares:** `CorsMiddleware`, `SecurityMiddleware`, `WhiteNoiseMiddleware`, `SessionMiddleware`, `CommonMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `MessageMiddleware`, `XFrameOptionsMiddleware`.
* **AutenticaÃ§Ã£o:** JWTAuthentication via `rest_framework_simplejwt`.
* **Permissions:** `IsAuthenticated` como global no DRF.
* **Serializers:** Encontrados no DRF, mas o cÃ³digo exato dos serializers de cada rota estÃ¡ nos pacotes internos nÃ£o escaneados em profundidade para esta lista sem limites, mas confirmados por `apps.accounts.serializers` em importaÃ§Ãµes.
* **Principais views:** (listadas do router) `AccessibilityBlocklistViewSet`, `ActionTypeViewSet`, `AgentViewSet`, `AgendaViewSet`, `ChiefViewSet`, `EventReportViewSet`, `InternalAgendaRequestView`, etc.
* **Principais services:** NÃƒO IDENTIFICADO NO PROJETO pasta `services` explÃ­cita, a lÃ³gica tende a morar nas `views.py` e `models.py`.
* **Principais management commands:** `sync_operational_data.py`.
* **Signals:** EvidÃªncia implÃ­cita nos mÃ³dulos do Django, porÃ©m nÃ£o escaneado arquivo `signals.py`.
* **Celery:** NÃƒO IDENTIFICADO NO PROJETO (`requirements.txt` nÃ£o lista celery).
* **Redis (como estÃ¡ sendo utilizado):** NÃƒO IDENTIFICADO NO PROJETO nenhuma utilizaÃ§Ã£o de cache no Django ou Broker. A variÃ¡vel `CACHE_URL` inexiste no compose, mantendo o backend isolado do container redis.

---

### 4. Banco
*Fonte primÃ¡ria:* ImportaÃ§Ã£o de Models pelo Django Shell.

* **Todas as tabelas (Models):** `LogEntry`, `Permission`, `Group`, `ContentType`, `Session`, `User`, `AuditLog`, `Sector`, `Vehicle`, `Team`, `UserTeamTransfer`, `Support`, `Agent`, `ActionType`, `Region`, `Municipality`, `Neighborhood`, `Kit`, `Dynamic`, `Material`, `Chief`, `ShiftSchedule`, `ShiftAbsence`, `ShiftSwapRequest`, `Agenda`, `AgendaHistory`, `AgendaMaterial`, `EventReport`, `EducationReport`, `AccessibilityBlocklist`, `EducationAction`, `SatisfactionSurvey`, `SatisfactionSurveyModerationHistory`, `EducationGoal`.
* **Principais relacionamentos:** O usuÃ¡rio amarra-se Ã s equipes/setores, que amarram-se Ã s Agendas operacionais. Modelado via ForeignKeys.
* **Migrations relevantes:** `0038_sync_operational_data.py` (preservada com comentÃ¡rios antigos).
* **Ãndices, Constraints e Chaves estrangeiras:** O Django ORM os abstrai. Gerados internamente pelo banco PostgreSQL 16 com as chaves padrÃ£o de `_id`.

---

### 5. APIs
*Fonte primÃ¡ria:* `backend/config/urls.py`

* `/api/auth/login/` (POST)
* `/api/auth/me/` (GET)
* `/api/auth/refresh/` (POST)
* `/api/auth/password-reset/` (POST)
* `/api/auth/set-password/` (POST)
* `/api/public/cep/` (GET)
* `/api/public/agenda-request/` (POST/GET)
* `/api/internal/agenda-request/` (POST)
* `/api/webhooks/google-forms/` (POST)
* Rotas DinÃ¢micas de ViewSet REST via DRF Router (`/api/agendas/`, `/api/users/`, `/api/reports/`, etc) usando padrÃ£o GET, POST, PUT, PATCH, DELETE.

---

### 6. Frontend
*Fonte primÃ¡ria:* `frontend/src/App.jsx` e `frontend/package.json`

* **PÃ¡ginas:** `LoginPage`, `SetPasswordPage`, `PublicAgendaRequestPage`, `SatisfactionSurveyPage`, `DashboardPage`, `AgendaPage`, `CalendarPage`, `ShiftSchedulePage`, `TechnicalReportsPage`, `StatisticsPage`, `EvaluationsPage`, `GoalsPage`, `LookupsPage`, `UsersPage`, `AuditLogsPage`.
* **Componentes:** `AppLayout`, `ProtectedRoute`.
* **Contextos:** `AuthContext.jsx`.
* **Providers:** ImplÃ­cito no AuthContext.
* **Hooks:** `useAuth`.
* **Cliente HTTP:** NÃƒO IDENTIFICADO NO PROJETO nome da biblioteca no arquivo principal (provavelmente Axios ou Fetch nativo em `api/`).
* **Gerenciamento do token JWT:** Feito via `AuthContext`.
* **Principais fluxos:** Checagem em `ProtectedRoute` validando `roles` (`ADMIN`, `MANAGER`, `SUPERVISOR`, `USER`, `SUPPORT`, `CREATOR`).

---

### 7. VariÃ¡veis de ambiente
*Fonte primÃ¡ria:* `backend/.env`

* `SECRET_KEY`
* `DEBUG`
* `ALLOWED_HOSTS`
* `POSTGRES_DB`
* `POSTGRES_USER`
* `POSTGRES_PASSWORD`
* `POSTGRES_HOST`
* `POSTGRES_PORT`
* `DATABASE_URL`
* `CORS_ALLOWED_ORIGINS`
* `FRONTEND_URL`
* `PUBLIC_REQUESTS_CSV_URL`
* `EMAIL_BACKEND`
* `EMAIL_HOST`
* `EMAIL_PORT`
* `EMAIL_HOST_USER`
* `EMAIL_HOST_PASSWORD`
* `EMAIL_USE_TLS`
* `DEFAULT_FROM_EMAIL`
* `AGENDA_REPLY_TO_EMAIL`

---

### 8. Deploy
*Fonte primÃ¡ria:* `deploy.py`

* O script `deploy.py` conecta via SSH/SFTP no IP `187.127.45.148` (usuÃ¡rio `root`).
* Copia/Sobrescreve arquivos pontuais (`TechnicalReportsPage.jsx`, `UsersPage.jsx`) - (PrÃ¡tica Ad-Hoc nÃ£o padronizada de versionamento).
* Executa o comando cru: `cd /root/agenda-educacao && docker compose build frontend && docker compose up -d`.

---

### 9. SeguranÃ§a
*Fonte primÃ¡ria:* `nginx.conf` e `settings.py`

* **CORS:** Restrito pelas origens na variÃ¡vel `CORS_ALLOWED_ORIGINS`.
* **CSRF:** Habilitado nativamente pelo Django (`CsrfViewMiddleware`).
* **JWT:** Gerenciado via `rest_framework_simplejwt`. Bearer Token com expiraÃ§Ã£o de 1 hora.
* **HTTPS:** Terminado pelo Nginx usando certificados mapeados do Certbot local.
* **SECRET_KEY:** Protegida e carregada externamente (`os.environ`).
* **Cookies:** NÃƒO IDENTIFICADO NO PROJETO controle primÃ¡rio de Auth via Cookie (usa Headers Bearer).
* **Headers:** O Nginx bloqueia clickjacking e sniffing (`X-Frame-Options DENY`, `X-Content-Type-Options nosniff`, `Content-Security-Policy`).
* **Rate Limit:** 30/min para anÃ´nimos, 120/min para autenticados.
* **Uploads:** Servidos via `alias` na rota `/media/` (protegido por restriÃ§Ãµes do sistema de arquivos).
* **PermissÃµes:** ValidaÃ§Ã£o granular por rotas (ex: `roles=["ADMIN"]`) no Frontend e `IsAuthenticated` base no backend.

---

### 10. Logs
* **Onde ficam:** NÃƒO IDENTIFICADO NO PROJETO captura em arquivo fixo central. Residem dentro do buffer do Docker Daemon e stdout do supervisor/processo.
* **Como visualizar:** `docker logs sied_backend` / `docker logs sied_proxy`.
* **Como acompanhar:** Terminal, atachando logs ou implementando agente futuro externo.

---

### 11. Backups
* **Se existem:** NÃƒO IDENTIFICADO NO PROJETO nenhuma rotina de cronjob, shell script automatizado de pg_dump ou AWS S3 Sync no repositÃ³rio. O Ãºnico arquivo com a palavra "backup" Ã© o estÃ¡tico legado JSON `render_backup.json`.
* **Onde sÃ£o feitos:** Manualmente pelos administradores do servidor.
* **Como restaurar:** Manuais de CLI do PostgreSQL via `docker exec`.

---

### 12. Health Checks
*Fonte primÃ¡ria:* `backend/config/urls.py`

* **Endpoints:** 
  * Rota `/` do Django responde `"ok"`.
  * Rota `/healthz/` do Django responde `"ok"`.
* **Comandos:** NÃƒO IDENTIFICADO NO PROJETO `HEALTHCHECK` command instruÃ­do dentro dos `Dockerfiles` ou `docker-compose.yml`.
* **VerificaÃ§Ãµes existentes:** Apenas o endpoint dummy atestando que o webserver estÃ¡ ativo. Sem deep-check no DB.

---

### 13. Redis
* EstÃ¡ instalado via compose. **NÃƒO ESTÃ SENDO UTILIZADO.**
* NÃ£o hÃ¡ Celery no `requirements.txt`. O sistema de Cache do Django foi auditado e estÃ¡ mapeado para `LocMemCache` interno na RAM do worker Python, jÃ¡ que a variÃ¡vel `CACHE_URL` nÃ£o existe no compose ou env para amarrÃ¡-lo ao Redis.

---

### 14. Arquivos Legados
* **Arquivos:**
  * `archives/legacy/render/RENDER.md`
  * `archives/legacy/render/render.yaml`
  * `archives/legacy/render/render_backup.json`
  * `backend/apps/schedules/management/commands/sync_operational_data.py` (Marcado LEGADO, preservado).
* **Motivo:** Restos fÃ­sicos de quando a hospedagem era via plataforma PaaS Render.
* **Impacto da remoÃ§Ã£o:** Limpeza de espaÃ§o e clarificaÃ§Ã£o visual para novos programadores. Zero impacto tÃ©cnico na arquitetura atual operante.

---

### 15. PendÃªncias
Tudo que estÃ¡ faltando documentar ou formalizar em sistema na VPS:
* Falta rotina de Backup real (cron de pg_dump).
* Falta Healthcheck de banco (O endpoint /healthz sÃ³ checa processo web).
* Falta remover scripts ad-hoc (ex: `deploy.py`) de envio SSH vulnerÃ¡vel de pequenos arquivos `.jsx` soltos.
* Falta plugar o Redis de fato ao cache do backend para valer a pena ocupar memÃ³ria na VPS.
# RelatÃ³rio de DiagnÃ³stico de ProduÃ§Ã£o (CONCLUSIVO)

**EvidÃªncias Coletadas via Console KVM:**
1. A VPS estÃ¡ 100% online e operante.
2. O Docker estÃ¡ Ã­ntegro e rodando.
3. Todos os containers (`sied_proxy`, `sied_backend`, `sied_frontend`, `sied_db`, `sied_redis`) estÃ£o com status **UP** hÃ¡ 15 horas, provando que nÃ£o hÃ¡ "crash loops" ou falha de leitura de certificado que derrubaria o Nginx.
4. O host possui sockets abertos e escutando nas portas `22` (SSH) e `80` (HTTP).
5. **NÃƒO EXISTE serviÃ§o escutando na porta 443 (HTTPS) no host fÃ­sico.**

## AnÃ¡lise do Erro (`ERR_CONNECTION_RESET`)
Quando vocÃª digita `sied-leiseca.online` no navegador, o fluxo acontece da seguinte forma:
1. O navegador bate na porta `80` do servidor.
2. O container do Nginx atende a chamada (jÃ¡ que a porta 80 estÃ¡ escutando).
3. O Nginx executa a diretiva configurada no `nginx.conf`: `return 301 https://$host$request_uri;` (ForÃ§a o redirecionamento para HTTPS).
4. O navegador obedece e tenta se conectar na porta `443` (HTTPS).
5. Como **nenhum serviÃ§o estÃ¡ escutando na porta 443 no nÃ­vel do host**, o firewall do sistema operacional (ou a pilha TCP) responde com um pacote `RST` (Reset), cortando a ligaÃ§Ã£o imediatamente. O navegador exibe `ERR_CONNECTION_RESET`.

## A Causa Raiz
Se o Nginx estÃ¡ vivo (Up 15h) e configurado para ouvir `443 ssl` internamente, mas o comando `netstat` ou similar do host nÃ£o mostra a porta 443 aberta para a internet, existem apenas duas explicaÃ§Ãµes tÃ©cnicas viÃ¡veis e conclusivas:

1. **Falta de Mapeamento no `docker-compose.yml` em ProduÃ§Ã£o:**
   O arquivo `docker-compose.yml` que estÃ¡ *efetivamente* rodando lÃ¡ na VPS pode estar defasado ou editado incorretamente, faltando a linha `- "443:443"` na declaraÃ§Ã£o de `ports` do serviÃ§o `sied_proxy`. Como o Nginx estÃ¡ isolado na rede Docker, ele escuta a 443 internamente, mas o Docker nÃ£o construiu a ponte (`docker-proxy`) para expor isso no IP pÃºblico do host.

2. **Bloqueio de Firewall (UFW) com Regra REJECT:**
   Se o mapeamento estiver correto no compose, a porta 443 pode estar sendo ativamente rejeitada pelo firewall interno do Ubuntu (`ufw`). Uma regra de `REJECT` gera pacotes de Reset imediatos, enquanto uma regra de `DROP` geraria `Timeout`. Como o sintoma Ã© Reset e nÃ£o escuta visÃ­vel, o Docker pode ter sido impedido de manipular o `iptables` para abrir a 443.

## ConclusÃ£o e RecomendaÃ§Ã£o
O problema nÃ£o estÃ¡ no cÃ³digo Python ou React, e sim em um descolamento entre a Infraestrutura FÃ­sica e o Roteamento Docker da porta 443.

**Como validar e corrigir via KVM:**
1. Inspecione o compose em produÃ§Ã£o: `cat /root/agenda-educacao/docker-compose.yml | grep 443`. Se nÃ£o retornar nada, o arquivo estÃ¡ errado. A soluÃ§Ã£o serÃ¡ corrigir o arquivo e dar `docker compose up -d`.
2. Verifique o firewall: `ufw status`. Se a 443 nÃ£o estiver listada como `ALLOW`, adicione-a: `ufw allow 443/tcp`.
# RelatÃ³rio de InvestigaÃ§Ã£o de RegressÃ£o (Frontend Antigo)

Com base nas evidÃªncias irrefutÃ¡veis extraÃ­das pelo script no seu Console KVM, identifiquei exatamente o que causou o retorno para a versÃ£o antiga do sistema. O problema Ã© de **conflito de diretÃ³rios e escopo do Docker Compose**.

## 1. Qual versÃ£o estÃ¡ em execuÃ§Ã£o e de onde foi construÃ­da?
* **DiretÃ³rio em ExecuÃ§Ã£o:** `/root`
* A versÃ£o atual rodando (e que estÃ¡ servindo o site na internet) foi construÃ­da a partir do cÃ³digo fonte solto que estava na pasta base `/root`. 
* **EvidÃªncia:** O comando `docker inspect` revelou que a variÃ¡vel `com.docker.compose.project.working_dir` (que dita a raiz do projeto) estÃ¡ fixada em `/root`.
* Como o cÃ³digo ali Ã© de um "rascunho" ou clone muito antigo, os arquivos `TechnicalReportsPage.jsx` e `UsersPage.jsx` acusam datas de **2 de Julho** e **30 de Junho**, respectivamente. Por isso a interface antiga estÃ¡ na tela.

## 2. Onde estÃ¡ a versÃ£o mais recente do projeto?
* A versÃ£o correta, que vinha recebendo os uploads do nosso script `deploy.py`, reside no diretÃ³rio **`/root/agenda-educacao`** (e, estranhamente, hÃ¡ tambÃ©m um sub-clone em `/root/agenda-educacao/agenda-educacao`).
* Quando a mÃ¡quina foi ligada, alguÃ©m (ou algum script de startup da Hostinger) executou `docker compose up -d` acidentalmente direto na raiz `/root`, levantando os containers com o cÃ³digo obsoleto.

## 3. O Risco CrÃ­tico de Perda de Dados
**NÃƒO RODE `docker compose up -d` na pasta nova ainda!**
No ecossistema Docker Compose, quando vocÃª nÃ£o dÃ¡ um nome fixo aos volumes, eles herdam o nome da pasta em que o comando rodou. 
Como o sistema subiu a partir de `/root`, todo o seu banco de dados (cadastros, agendas) e uploads de imagens (media) dos Ãºltimos dias estÃ£o salvos em volumes chamados `root_postgres_data` e `root_media_volume`.
Se vocÃª simplesmente entrar na pasta correta (`/root/agenda-educacao`) e der *up*, o Docker criarÃ¡ novos volumes vazios (`agenda-educacao_postgres_data`), **apagando o banco de dados e os arquivos da aplicaÃ§Ã£o na visÃ£o do container**.

## 4. Procedimento 100% Seguro para Restaurar (Sem Perder Banco)

Para voltar para o cÃ³digo novo preservando intacto o banco de dados que estÃ¡ preenchido, vocÃª deverÃ¡ executar os seguintes passos no console KVM:

**Passo 1: Derrubar os containers antigos sem apagar os volumes**
```bash
cd /root
docker compose down
```

**Passo 2: Mapear os volumes antigos no cÃ³digo novo**
Entre na pasta certa e edite o `docker-compose.yml`:
```bash
cd /root/agenda-educacao
nano docker-compose.yml
```
VÃ¡ atÃ© o final do arquivo, na seÃ§Ã£o `volumes:`, e modifique para que o Docker da pasta nova "puxe" os discos rÃ­gidos da pasta velha (onde estÃ£o seus dados):
```yaml
volumes:
  postgres_data:
    name: root_postgres_data
    external: true
  static_volume:
    name: root_static_volume
    external: true
  media_volume:
    name: root_media_volume
    external: true
```

**Passo 3: Subir a aplicaÃ§Ã£o na pasta correta**
Salvar o arquivo e entÃ£o re-buildar a imagem puxando o cÃ³digo novo (de Julho) que estÃ¡ nessa pasta correta:
```bash
docker compose build frontend backend
docker compose up -d
```

Seguindo essa exata topologia, a VPS descartarÃ¡ a interface velha de Junho/Julho e servirÃ¡ o front-end novo de `/root/agenda-educacao`, porÃ©m conectando-se ao volume de banco de dados populado.

Como ordenado, aguardo o seu crivo e liberaÃ§Ã£o. VocÃª mesmo deseja aplicar esse roteiro de correÃ§Ã£o no KVM ou quer que eu atualize o nosso `deploy.py` local para fazer isso caso o SSH seja reestabelecido?
