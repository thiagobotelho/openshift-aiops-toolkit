# Changelog

## Unreleased

- Simplificado o modelo operacional para utilizar o contexto atual do `oc` por padrão.
- Adicionada CLI central `./openshift-aiops` para diagnósticos consultivos com saída humana, JSON, YAML, Markdown e raw sanitizado.
- Adicionados schemas e formatadores comuns para status padronizados, fallback ASCII, respeito a `NO_COLOR` e diferenciação entre status de execução e saúde do cluster.
- Adicionada descoberta inicial de capacidades via `oc api-resources` e `oc api-versions`.
- `environment`, `cluster` e `confirm_production` deixaram de ser obrigatórios para consultas read-only e permanecem apenas como compatibilidade obsoleta.
- Must-gather passou a usar confirmação própria por identificador do cluster, independente de classificação de ambiente.
- Atualizada documentação principal para instalação e operação baseadas em `oc whoami` e `./openshift-aiops health`.
- Validado must-gather completo em CRC/OpenShift Local com manifesto, checksums e análise offline segura.

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
- Ferramentas MCP passaram a publicar parâmetros comuns (`environment`, `cluster`, `timeout`, `confirm_production`) na primeira versão do fluxo multicluster.
- Implementado fluxo controlado de must-gather com preflight, execução, manifesto, checksums, marcador confidencial e análise offline.
- Adicionadas matriz MCP/scripts/must-gather e comparação arquitetural com o MCP Server oficial da Red Hat/OpenShift.
