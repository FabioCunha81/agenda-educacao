# Regras para IAs e LLMs (Constituição do Projeto)

Bem-vindo(a) ao projeto SIED (Operação Lei Seca). Se você é uma Inteligência Artificial, LLM ou Agente Autônomo, **você deve seguir rigorosamente as regras abaixo antes de realizar qualquer alteração neste repositório**. 

O descumprimento destas diretrizes pode causar a perda de dados em produção e comprometer a estabilidade do sistema.

## 1. Regras Gerais de Atuação

1. **Leia o Contexto:** Antes de qualquer alteração, leia o `docs/PROJECT_CONTEXT.md` para entender as regras de negócio.
2. **Prevenção de Regressões:** Leia o `docs/REGRESSION_CHECKLIST.md` antes de gerar qualquer código.
3. **Mínimo Impacto:** Faça alterações mínimas. Nunca faça grandes refatorações a menos que explicitamente ordenado pelo usuário humano.
4. **Planejamento Obrigatório:** Liste os arquivos exatos que pretende modificar e aguarde a aprovação antes de alterá-los.

## 2. Regras Estritas de Arquitetura e Infraestrutura

1. **Nunca altere a arquitetura base:** O projeto utiliza VPS (Hostinger), Docker Compose, Nginx, PostgreSQL, Redis, Django e React. 
2. **Nunca altere a infraestrutura:** Não modifique `docker-compose.yml`, `nginx.conf`, Dockerfiles ou mapeamento de volumes sem aprovação expressa do Tech Lead humano.
3. **Contexto de Deploy:** Nunca assuma que o projeto roda no Render, Heroku ou similares. Qualquer menção a essas plataformas em códigos antigos é legado morto e deve ser ignorado.
4. **Não altere arquivos de Banco de Dados:** Nunca altere `migrations` já aplicadas. 

## 3. Regras de Desenvolvimento e Validação

1. **Nunca remova funcionalidades existentes.** Se precisar atualizar algo, estenda a funcionalidade atual e garanta compatibilidade retroativa.
2. **Sempre atualize a documentação:** Se a sua alteração afetou a forma como o projeto roda ou como as rotas operam, atualize os respectivos arquivos na pasta `docs/`.
3. **Validação Rigorosa:** Após escrever ou modificar código, você é OBRIGADO a sugerir e/ou executar os testes de validação:
   - `python manage.py check`
   - `python manage.py test`
   - `npm run build` (para testar a compilação do frontend)

## 4. Consciência de Agente
Se você estiver executando ferramentas de bash no terminal da VPS de produção, **NUNCA** execute `docker compose down -v` ou remova volumes (`root_postgres_data`, `root_media_volume`). Todos os dados são críticos e persistentes.

Qualquer dúvida ou limite sobre seu acesso, pergunte ao humano antes de adivinhar.
