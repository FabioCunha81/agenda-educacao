# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato baseia-se no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere estritamente ao controle semântico humano e de IAs.

## [Unreleased]

## [2026-07-14] - Homologação de Infra e Consistência Documental
### Added
- Documentação central unificada (Árvore `docs/`).
- Criação de Constituição Global para regulação de Inteligências Artificiais (`AI_RULES.md`).
- Scripts e procedimentos operacionais seguros documentados (Backups estritos, Extrações sanitizadas).
- Rede fechada Docker (`sied_network`) adicionada ao arquivo de produção para ancorar comunicação dos 5 contêineres e evitar regressão de ponte bridge.

### Fixed
- Regressão crônica no Proxy Nginx que gerava o bloqueio da comunicação via porta 443 e impedia o Handshake do certificado Let's Encrypt (Corrigido injetando `- "443:443"` no Compose junto com a montagem `- /etc/letsencrypt:/etc/letsencrypt:ro`).
- Descolamento de escopo entre `root_default` (banco de dados real do sistema operante) e os mapeamentos tentados a partir da subpasta (Evitado garantindo a tag `external: true`).

### Removed
- Eliminação definitiva de alucinações legadas (PaaS cloud como Render/Heroku) do conhecimento de domínio operacional da API e da orquestração. O projeto agora é puramente gerido em VPS (IaaS).
