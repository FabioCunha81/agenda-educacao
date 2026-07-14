# Registro de Decisões Arquiteturais (ADRs)

Este documento guarda o histórico de decisões estruturais críticas para a sustentação e arquitetura do projeto.
Agentes IAs e programadores estão expressamente **proibidos de reverter estas escolhas** sem um debate prévio documentado.

## Decisão 1: Abandono Definitivo de Plataformas PaaS (Ex: Render)
**Contexto:** O projeto rodava parcialmente com traços de PaaS, o que gerava comandos conflitantes (como scripts esperando injetar arquivos onde a nuvem fechava os acessos).
**Decisão:** O projeto será, para todo o sempre, hospedado sobre IaaS (VPS) próprio. Todo o tráfego HTTP, escalonamento e persistência de dados estão contidos estritamente na malha local do Docker Compose.
**Consequência:** Impede scripts baseados no Heroku/Render de "alucinarem" rotas de deploy falhas. O deploy é puramente `docker compose down && docker compose up -d --build`.

## Decisão 2: Persistência de Dados Baseada na Raiz (root_)
**Contexto:** Ao tentar rodar a malha de containers em diretórios diferentes (`/root` vs `/root/agenda-educacao`), o Docker instanciou bases de dados isoladas e vazias, desconectando os usuários dos seus cadastros.
**Decisão:** Os volumes de dados e mídia do projeto (Postgres e Media) são tratados como discos rígidos incorruptíveis (volumes `external: true`). As chaves reais de referência deles são `root_postgres_data`, `root_media_volume` e `root_static_volume`.
**Consequência:** Qualquer reformulação ou refatoração no `docker-compose.yml` deve obrigatoriamente acoplar esses mesmos discos, senão o sistema sofrerá regressão irreversível.

## Decisão 3: Rede Única Explícita
**Contexto:** Contêineres de pastas diferentes isolavam-se (proxy não encontrava backend, e backend não encontrava postgres) devido ao uso da ponte Default do diretório.
**Decisão:** Toda a comunicação inter-container é governada pela rede `sied_network`.
**Consequência:** Protege as passagens de Nginx e os túneis do DB de falhas de DNS Docker interno.
