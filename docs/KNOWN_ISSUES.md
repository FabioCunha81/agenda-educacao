# Known Issues (Problemas Conhecidos e Limitações Técnicas)

Este documento centraliza pendências técnicas, gargalos, ou problemas temporários que foram observados no sistema mas que ainda não exigem uma resolução urgente (ou foram mantidos intencionalmente para não impactar a estabilidade).

## 1. Conflito Geográfico de Diretórios na VPS
Existem pelo menos duas pastas na VPS competindo pela verdade do código fonte:
* `/root` (Que rodou código fonte legado do começo de Julho).
* `/root/agenda-educacao` (Para onde o script de upload SFTP antigo enviava os dados).
* E subpastas aninhadas como `/root/agenda-educacao/agenda-educacao`.

**Impacto Atual:** Exige extrema cautela de onde executar os builds e os downs no servidor de produção, além de exigir a fixação dos discos virtuais para não fragmentar o Postgresql. (Tratado no `docs/DEPLOY.md`).

## 2. Deploy Script via SFTP Não Trilha o Git
A injeção de arquivos alterados ocorria injetando diretamente o patch de arquivos (`.jsx` do React, por ex.) sobrescrevendo o arquivo do host.
**Impacto Atual:** Ficam existindo arquivos mortos e alterações que nunca foram "commitadas" num repositório Git, tornando o versionamento na VPS "sujo".

## 3. Firewall Bloqueando a Porta 22
IPs não declarados (como o de nós, agentes de desenvolvimento remoto) frequentemente caem na blacklist do Fail2Ban ou regras intrínsecas de UFW da Hostinger, impossibilitando conexões SSH cruas e comandos arbitrários de monitoramento sem o intermédio de um console KVM na web.
**Impacto Atual:** Diagnóstico depende da execução assíncrona humana colando os shell scripts de homologação.
