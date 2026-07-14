# Checklist Anti-Regressão

Este documento contém o checklist obrigatório que deve ser cruzado antes de enviarmos novos códigos ou infraestruturas para a branch `main` e para a produção. 
O SIED é uma aplicação com interdependências sensíveis. O cumprimento destas verificações reduz drasticamente o risco de queda silenciosa.

## 1. Verificações de Código (Pré-Deploy)

- [ ] As variáveis de ambiente injetadas em `.env` (ex: `VITE_API_URL`, `DATABASE_URL`) foram checadas na documentação oficial ou com a equipe, evitando quebra da SPA React no Frontend ou crash do ORM no Backend?
- [ ] Foram rodados localmente os testes automatizados da bateria oficial do projeto (`python manage.py check`, `python manage.py test`, `npm run build`) sem acréscimo de falhas?
- [ ] O código introduzido no ORM (Backend) altera dados passados de migrations irreversíveis que precisariam de dump reverso em caso de falha? Se sim, **o Tech Lead deve aprovar explicitamente**.

## 2. Verificações de Infraestrutura (Pré-Deploy)

- [ ] Algum arquivo de Dockerfile, `docker-compose.yml`, ou `.conf` foi alterado?
- [ ] Foram propostas deleções de labels (`depends_on`), variáveis, ou portas? Caso sim, foi garantido que os mapeamentos base (`80:80`, `443:443` e rede `sied_network`) não foram acidentalmente omitidos?
- [ ] Não há comandos `down -v`, `system prune`, ou comandos voláteis ativados em scripts de deploy que apagarão os volumes `root_postgres_data` e `root_media_volume`?

## 3. Conformidade Documental (Pós-Modificação)
- [ ] A alteração adicionou um novo fluxo lógico? As regras foram estendidas em `PROJECT_CONTEXT.md`?
- [ ] Novas rotas REST? Elas foram indexadas de forma geral em `API_REFERENCE.md`?

*Lembrete para IAs:* A prioridade absoluta não é acelerar o deploy, mas blindar a produção contra falhas decorrentes de simplificação excessiva de código e exclusão acidental de variáveis.
