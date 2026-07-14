# Estratégia de Backup, Restauração e Rollback

Devido à arquitetura fechada em contêineres e ao isolamento dos bancos de dados, o processo de backup e rollback do SIED é altamente específico. Siga as instruções homologadas abaixo para lidar com os dados críticos de produção.

## 1. Regras Fundamentais

* **Isolamento de Estado:** Jamais baseie-se no nome "padrão" dos volumes. O Docker Composer, caso executado fora do seu diretório raiz (`/root/agenda-educacao`), prefixará os discos com o nome do outro diretório (ex: `root_postgres_data`), cindindo a base de dados.
* Sempre recupere as credenciais *dinamicamente* lendo a variável de ambiente viva do container, impedindo falhas de interpolação caso o `.env` esteja ausente.

## 2. Roteiro Oficial de Backup (Snapshot Completo)

Execute o bloco abaixo em caso de migrações estruturais. Ele não causa downtime, congela o estado via `pg_dump`, faz um backup legível do Media Volume (uploads de usuários) e guarda cópias do YAML de orquestração:

```bash
set -euo pipefail

BACKUP_DIR="/root/backups/migracao-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 1. Obter credenciais do Postgresql via runtime seguro
POSTGRES_USER=$(docker inspect sied_db --format '{{range .Config.Env}}{{println .}}{{end}}' | sed -n 's/^POSTGRES_USER=//p')
POSTGRES_DB=$(docker inspect sied_db --format '{{range .Config.Env}}{{println .}}{{end}}' | sed -n 's/^POSTGRES_DB=//p')

# 2. Gerar Snapshot Lógico (-Fc compressão custom do pg)
docker exec sied_db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$BACKUP_DIR/postgres.dump"

# 3. Empacotar Media Volume
docker run --rm -v root_media_volume:/data:ro -v "$BACKUP_DIR":/backup alpine sh -c 'tar -czf /backup/media_volume.tar.gz -C /data .'

# 4. Clonar Orquestrador
cp /root/agenda-educacao/docker-compose.yml "$BACKUP_DIR/"
cp /root/agenda-educacao/.env "$BACKUP_DIR/" 2>/dev/null || true

echo "Backup gravado em: $BACKUP_DIR"
```

## 3. Estratégia de Rollback

Caso um Deploy ou Migration tenha corrompido o ecossistema e seja impossível avançar (fix-forward), os seguintes passos garantem o retorno absoluto à estabilidade.

**Passo 1:** Parar imediatamente a malha corrompida:
```bash
cd /root/agenda-educacao
docker compose down
```

**Passo 2:** Restaurar os arquivos do `docker-compose.yml` a partir de uma data segura de `$BACKUP_DIR` de volta para a pasta de operação `/root/agenda-educacao`.

**Passo 3:** Subir a malha antiga:
```bash
docker compose up -d
```

**Observação em Rollbacks da Rede:** Se por acaso os containers antigos ressuscitarem sem rotas expostas (ex: Proxy voltando sem 443 porque dependia de scripts defasados), force uma conexão à rede unificada ou verifique manualmente os links de rede com `docker network inspect sied_network`.
