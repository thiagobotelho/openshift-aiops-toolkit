# Changelog

## 0.1.0 - 2026-07-11

- Estrutura inicial do OpenShift AIOps Toolkit.
- Scripts Bash idempotentes para diagnóstico e coleta somente leitura.
- Pacote Python com validação, sanitização, coleta, relatórios e servidor MCP.
- Inventários, configurações, prompts, templates, runbooks e testes locais.
- Corrigido `Makefile` e adicionado `make check` offline por padrão.
- Adicionado `make check-cluster` para preflight consultivo após autorização.
- `install.sh` passou a tratar `oc`, `crc`, `yq`, `codex` e Podman como dependências opcionais para instalação local.
- Scripts agora preferem `.venv/bin/python` quando o ambiente virtual existe.
- Servidor MCP passou a usar o SDK oficial em baixo nível preservando schemas específicos das ferramentas.
- Reforçado bloqueio de Secrets (`secret/foo` e combinações como `pods,secrets`).
- Adicionados testes negativos para produção, paths, sanitização e handshake MCP.
- Criada documentação de auditoria, validação local, validação MCP, CRC pendente, integração Codex, backlog e matrizes.
- Adicionado suporte a `OPENSHIFT_AIOPS_COMMAND_PREFIX` e `OPENSHIFT_AIOPS_OC_BIN` para validação em ambientes isolados usando o `oc` do host.
- Corrigida colisão de diretórios de evidências direcionadas com timestamp em microssegundos.
- Adicionados coletores direcionados para storage, network, ingress, DNS, OLM, monitoring, capacidade e certificados.
- Validação consultiva realizada em CRC/OpenShift Local 4.22.1 sem alterar recursos.
- Ferramentas MCP passaram a publicar parâmetros comuns (`environment`, `cluster`, `timeout`, `confirm_production`), respeitar variáveis de ambiente e bloquear `production` sem confirmação explícita.
- Implementado fluxo controlado de must-gather com preflight, execução, manifesto, checksums, marcador confidencial e análise offline.
- Adicionadas matriz MCP/scripts/must-gather e comparação arquitetural com o MCP Server oficial da Red Hat/OpenShift.
