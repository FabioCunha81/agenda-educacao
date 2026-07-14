# Homologação e Healthchecks

Para confirmar que a aplicação não sofreu quebras silenciosas após um deploy na Hostinger, a execução do checklist abaixo é **obrigatória**. Não baseie o sucesso de um deploy apenas no fato do comando `docker compose up` não ter travado.

## 1. Monitoramento Básico (IsAlive)

Os contêineres devem estar estabilizados (com `Uptime` considerável) sem evidência de `Restarting` ou `Crash Loop Back-off`.

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep sied_
```

## 2. Inspeção de Roteamento Nativo e Portas (TCP Level)

O Proxy obrigatoriamente tem que se ancorar e abrir as portas físicas do host na 80 e na 443. A ausência da 443 exposta resulta no erro fatal `ERR_CONNECTION_RESET` aos visitantes.

```bash
# Deve retornar: 0.0.0.0:80, 0.0.0.0:443
docker port sied_proxy
```

Testes de conectividade crua via KVM (sem depender de DNS externo):
```bash
# Confirma se o Nginx entrega HTTP localmente
curl -I http://127.0.0.1

# Confirma se o Nginx engata certificado SSL
curl -vkI https://127.0.0.1
```

## 3. Checagem Lógica de Aplicação (API)

Mesmo com a rede de pé, o Backend Django (Gunicorn) pode ter "capotado" (Crashado por falta de conexões de banco de dados ou erro de sintaxe) escondido atrás do Nginx, retornando "502 Bad Gateway". 
Sempre analise as últimas linhas de log procurando falhas de Migrations, tracebacks ou quedas bruscas de `workers`:

```bash
docker logs sied_backend --tail 50
```

Se um endpoint nativo de `/healthz` estiver embutido no Backend, invoque-o para checar a saúde integral das integrações (exemplo: Redis/PG vivos e respondendo a ping de aplicação):
```bash
curl -fsS http://127.0.0.1/healthz
```
