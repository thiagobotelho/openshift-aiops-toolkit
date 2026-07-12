# Integração com Codex CLI

- Data: 2026-07-11
- Status local: VALIDADO E CONFIGURADO

## Verificações executadas

| Comando | Resultado |
|----|----|
| `codex --help` | PASSOU |
| `codex mcp --help` | PASSOU |
| `codex mcp list` | PASSOU |

## Script de configuração

O script `scripts/configurar-codex-mcp.sh` foi ajustado para:

- localizar o caminho absoluto do projeto;
- usar `.venv/bin/python`;
- validar importação de `mcp_server.server`;
- mostrar o comando antes de executar;
- pedir confirmação antes de alterar a configuração;
- aceitar `--yes` para execução não interativa;
- aceitar `--replace` para remover e recriar somente `openshift-readonly`;
- registrar `PYTHONPATH` para permitir import do pacote fora do diretório do repo;
- registrar `OPENSHIFT_AIOPS_COMMAND_PREFIX` e `OPENSHIFT_AIOPS_OC_BIN` quando definidos;
- não sobrescrever servidor já existente.

## Configuração aplicada

O servidor global `openshift-readonly` foi configurado no Codex CLI com:

- comando: `.venv/bin/python -m mcp_server.server`;
- env: `PYTHONPATH`, `OPENSHIFT_AIOPS_COMMAND_PREFIX`, `OPENSHIFT_AIOPS_OC_BIN`;
- status: `enabled`.

## Configuração manual

```toml
[mcp_servers.openshift-readonly]
command = "/CAMINHO/ABSOLUTO/openshift-aiops-toolkit/.venv/bin/python"
args = ["-m", "mcp_server.server"]
cwd = "/CAMINHO/ABSOLUTO/openshift-aiops-toolkit"
startup_timeout_sec = 20
tool_timeout_sec = 120
enabled = true
```

## Próximo passo

Reiniciar a sessão Codex para carregar a nova ferramenta MCP e continuar com `prompts/continuar-validacao-mcp.md`. Não abrir uma segunda sessão Codex dentro da sessão atual.
