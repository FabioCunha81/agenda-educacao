# Contribuindo com o SIED (Operação Lei Seca)

Este documento estabelece as regras oficiais de colaboração para desenvolvedores humanos e Agentes IA.

## 1. Fluxo de Trabalho (Git Flow)

* Utilize `feature/nome-da-feature` para novas funcionalidades.
* Utilize `bugfix/nome-do-bug` para correções.
* Somente faça merge para a branch principal após aprovação ou conclusão e validação local.
* Commits devem ser claros, atômicos e seguir as boas práticas de versionamento.

## 2. Padrões de Desenvolvimento

1. **Nunca altere migrations já aplicadas.** Modificações de banco de dados devem sempre ser feitas através de novas migrations gerenciadas pelo Django.
2. **Sempre execute testes locais.** Não envie código sem antes validar o funcionamento através das suítes e comandos oficiais de healthcheck.
3. **Nunca altere a infraestrutura.** Mudanças no `docker-compose.yml`, `nginx.conf` ou mapeamento de portas requerem aprovação explícita e passagem por esteira de homologação.
4. **Sem refatorações drásticas.** Alterações devem ser contidas, específicas e manter o menor escopo possível para evitar regressões silentes.

## 3. Padrões de Documentação

* **Sempre atualize a documentação.** Caso haja inclusão de novos endpoints, variáveis de ambiente ou dependências, os arquivos correspondentes na pasta `docs/` devem ser imediatamente revisados no mesmo commit.
* Não mantenha relatórios temporários ou fotografias soltas no diretório raiz. Encaminhe-os para `docs/audits/`.
