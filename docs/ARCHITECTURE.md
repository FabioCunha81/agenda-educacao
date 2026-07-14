# Arquitetura e Infraestrutura do Projeto

Este documento define a arquitetura oficial e validada que compõe o SIED. Qualquer menção a provedores de nuvem PaaS (Render, Heroku, etc.) no histórico do projeto deve ser sumariamente ignorada. O ambiente oficial é estruturado sobre IaaS puro (VPS Hostinger).

## 1. Topologia de Servidor

O sistema está implantado em uma única **VPS Linux (Ubuntu)** na infraestrutura da Hostinger. 
Não existe load balancer em nuvem e não há bancos de dados gerenciados fora da máquina. Toda a orquestração e roteamento de tráfego ocorrem internamente via Docker.

## 2. Orquestração e Contêineres (Docker Compose)

A aplicação inteira sobe a partir de um único manifesto `docker-compose.yml` que provisiona e conecta 5 contêineres vitais na rede explícita fechada `sied_network` (driver: bridge).

1. **sied_proxy (Nginx):** 
   - **Papel:** Ingress controller e terminação SSL.
   - **Portas Expostas no Host:** `80:80` (redirecionamento HTTP->HTTPS) e `443:443` (HTTPS nativo).
   - **Dependências de montagem:** Certificados do `/etc/letsencrypt/` e volumes estáticos do backend.
2. **sied_frontend (React/Vite):** 
   - **Papel:** Servir a Single Page Application (SPA).
   - **Tráfego:** Recebe roteamento do `sied_proxy` via conexão interna no Docker (`http://frontend:80`).
3. **sied_backend (Django Rest Framework + Gunicorn):**
   - **Papel:** API central da operação.
   - **Boot:** Executa `python manage.py migrate` e levanta o gunicorn via WSGI.
4. **sied_db (PostgreSQL 16):**
   - **Papel:** Banco de dados relacional (Single Source of Truth).
   - **Isolamento:** A porta `5432` NÃO está publicada para o Host externo, restringindo acesso a invasores. O backend se comunica por DNS interno do Docker (`db:5432`).
5. **sied_redis (Redis 7):**
   - **Papel:** Fila assíncrona (Celery, se aplicável) e Cache. Também 100% isolado na rede.

## 3. Discos Rígidos Virtuais (Volumes Persistentes)

O Docker Compose está configurado de modo explícito (`external: true`) para utilizar as seguintes chaves de volume que contêm as persistências:

* `root_postgres_data`: (Imutável) Contém todos os dados transacionais e de negócio do banco. Se desconectado, o sistema volta "vazio".
* `root_media_volume`: Contém os anexos, avatares, fotos e PDFs enviados pelos usuários através das rotas de upload do Django.
* `root_static_volume`: Arquivos transpilados e assets estáticos (`collectstatic`) que o Nginx entrega para alívio do Gunicorn.

**Qualquer modificação nessa anatomia exige revisão severa e testes de integridade prévios (staging).**
