# Validação MCP

- Data: 2026-07-11
- Servidor: `openshift-readonly`
- Transporte: STDIO
- Resultado local/offline: PASSOU
- Resultado consultivo no CRC: PASSOU
- Resultado E2E STDIO no CRC: PASSOU
- Resultado MCP nativo no Codex CLI: BLOQUEADO PELO CLIENTE CODEX em execução não interativa

## Validações sem cluster

| Item | Resultado | Evidência |
|----|----|----|
| importação de `mcp_server.server` | PASSOU | import local |
| importação do SDK MCP na `.venv` | PASSOU | pacote `mcp` instalado |
| inicialização STDIO com handshake MCP válido | PASSOU | `initialize` respondeu com `serverInfo` |
| listagem de ferramentas | PASSOU | 82 ferramentas |
| schemas específicos por ferramenta | PASSOU | `inputSchema` preservado, sem wrapper genérico `arguments` |
| parâmetros comuns read-only | PASSOU | `context`, `kubeconfig`, `timeout`, `output` e `verbose` publicados nos schemas |
| parâmetros opcionais de compatibilidade | PASSOU | `environment`, `cluster` e `confirm_production` aceitos como metadados opcionais, sem bloquear consultas read-only |
| chamadas sequenciais STDIO | PASSOU | múltiplas ferramentas chamadas no mesmo processo, aguardando resposta por chamada |
| E2E STDIO no CRC | PASSOU | 28 ferramentas consultivas, 28 aprovadas |
| ausência de ferramenta genérica de shell | PASSOU | testes unitários |
| validação de parâmetros | PASSOU | testes negativos |
| sanitização de saída | PASSOU | testes de sanitização |
| uso de `subprocess.run` com lista | PASSOU | testes unitários |
| ausência de `shell=True` | PASSOU | auditoria estática |

## Ferramentas MCP destacadas

- `current_context`;
- `validate_cluster_context`;
- `cluster_identity`;
- `cluster_version`;
- `cluster_health`;
- `cluster_operators`;
- `degraded_operators`;
- `list_nodes`;
- `unhealthy_nodes`;
- `unhealthy_pods`;
- `recent_warning_events`;
- `storage_health`;
- `network_health`;
- `ingress_health`;
- `dns_health`;
- `resource_usage`.

## Validação consultiva no CRC

Após aprovação explícita, as seguintes ferramentas podem ser chamadas contra o CRC usando STDIO e SDK MCP, sempre com o contexto atual do `oc`:

- `current_context`;
- `cluster_identity`;
- `cluster_version`;
- `cluster_health`;
- `cluster_operators`;
- `degraded_operators`;
- `list_nodes`;
- `unhealthy_nodes`;
- `unhealthy_pods`;
- `recent_warning_events`;
- `storage_health`;
- `network_health`;
- `ingress_health`;
- `dns_health`;
- `resource_usage`.

Resultado: todas responderam sem erro JSON-RPC e sem timeout.

Evidência: `relatorios/validacao-mcp-crc-20260711-143918.json`.

## Limitação remanescente

O servidor `openshift-readonly` está habilitado no Codex CLI e o `codex exec` carrega a ferramenta `openshift-readonly/current_context`. No modo não interativo, a chamada da ferramenta é cancelada pelo cliente Codex antes de retornar o contexto.

A validação equivalente por STDIO passa com o mesmo servidor `openshift-readonly`, mesmo Python e mesmas variáveis registradas no Codex CLI.
