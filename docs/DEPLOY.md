# Estratégia de Deploy

Este documento detalha o procedimento oficial de deploy (entrega) adotado atualmente pela plataforma, rodando puramente na infraestrutura Hostinger VPS + Docker.

## 1. Contexto do Deploy Atual
Diferente de sistemas hospedados em plataformas automatizadas de PaaS, o nosso sistema atualiza seu código subindo as modificações direto para a VPS. O histórico do projeto aponta que o upload pode ocorrer de três formas:
1. Puxando as atualizações do Git via `git pull` internamente na VPS (`/root/agenda-educacao`).
2. Script de upload automatizado (`deploy.py` local).

## 2. Passo a Passo do Deploy Oficial

**Passo 1: Entrar no diretório base e baixar as alterações**
A aplicação ativa deve ser atualizada e compilada no diretório oficial que hospeda o `docker-compose.yml`:
```bash
cd /root/agenda-educacao
git pull origin main
```

**Passo 2: Buildar Imagens (Zero-Downtime parcial)**
Forçar a criação de novas imagens docker a partir dos novos sources, sem desligar a aplicação que está rodando.
```bash
docker compose build
```

**Passo 3: Swap (Troca dos contêineres)**
Assim que o build acabar (O React for transpilado e os pacotes Python instalados na imagem nova), levantamos os containers, o que forçará a recriação apenas daqueles cujas imagens mudaram:
```bash
docker compose up -d
```

**Passo 4: Validações (Post-Deploy)**
* Imediatamente verificar se o banco subiu sem crash (caso alguma migration do Django tenha sido conflitante) através de: `docker logs sied_backend --tail 50`.
* Realizar os checks documentados em `docs/HEALTHCHECK.md`.

## 3. O que NUNCA fazer em um Deploy

* NUNCA execute `docker compose down -v`. A flag `-v` extermina os discos rígidos, acarretando perda instantânea do banco de dados de produção inteiro (Volume `root_postgres_data`).
* NUNCA troque o nome dos volumes na seção `volumes:` do `docker-compose.yml` sem uma estratégia de importação (via `external: true`), sob pena de subir um banco de dados limpo e zerado.
