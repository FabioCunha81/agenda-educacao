# SIED - Sistema de Informação de Educação (Operação Lei Seca)

O SIED é o sistema de gestão central da Operação Lei Seca para o controle, agendamento e emissão de relatórios de ações educativas. 

## Como o Projeto Funciona
A aplicação possui um backend em **Django (Python)** fornecendo uma API RESTful, um banco de dados **PostgreSQL**, filas e cache gerenciados pelo **Redis**, e um frontend reativo em **React (Vite)**. O tráfego e o roteamento de borda (incluindo SSL) são centralizados via **Nginx**.

Toda a arquitetura roda perfeitamente orquestrada e em contêineres gerenciados pelo **Docker Compose**.

## Onde Está a Documentação?
Para evitar poluição na raiz e manter a organização profissional, **toda a documentação técnica oficial reside na pasta `docs/`**.
Antes de atuar no projeto, leia os arquivos abaixo na seguinte ordem:

1. `AI_RULES.md` e `CONTRIBUTING.md` (Para conhecer os limites e regras de contribuição)
2. `docs/PROJECT_CONTEXT.md` (Para entender o domínio de negócio da Operação Lei Seca)
3. `docs/ARCHITECTURE.md` (Para entender como a malha de containers e o fluxo se comportam)
4. `docs/DEPLOY.md` (Para entender como o projeto deve ir ao ar)

## Como Rodar e Testar Localmente
O sistema é encapsulado via Docker.
1. Garanta que o `.env` esteja configurado na raiz (com `DEBUG=True` para dev, ou `DEBUG=False` para produção).
2. Construa a malha e levante a orquestração:
```bash
docker compose up -d --build
```
3. Teste se as portas e a estrutura estão íntegras utilizando as ferramentas e comandos prescritos em `docs/HEALTHCHECK.md`.
4. Os testes unitários oficiais do Django podem ser executados via:
```bash
docker exec sied_backend python manage.py check
docker exec sied_backend python manage.py test
```
