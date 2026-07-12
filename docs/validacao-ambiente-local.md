# Validação do ambiente local

- Data: 2026-07-11
- Escopo: Fase 3 — validação local sem acesso ao CRC
- Resultado: PASSOU COM RESSALVAS

## Comandos executados

| Comando | Resultado | Observação |
|----|----|----|
| `bash --version` | PASSOU | Bash 5.3.15 |
| `python3 --version` | PASSOU | Python 3.13.14 |
| `python3 -m pip --version` | PASSOU | pip 26.1.2 |
| `oc version --client` | BLOQUEADO | `oc` não está no PATH do ambiente atual |
| `crc version` | BLOQUEADO | `crc` não está no PATH do ambiente atual |
| `jq --version` | PASSOU | `jq` disponível |
| `yq --version` | BLOQUEADO | `yq` não está no PATH |
| `codex --help` | PASSOU | Codex CLI disponível |
| `codex mcp --help` | PASSOU | subcomando MCP disponível |
| `codex mcp list` | PASSOU | estado inicial conferido antes da configuração |
| `make help` | PASSOU | Makefile corrigido |
| `scripts/install.sh` | PASSOU | criou `.venv` e instalou dependências Python |
| `make check` | PASSOU | preflight offline sem cluster |
| `tests/run.sh` | PASSOU | 32 testes |
| `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | PASSOU | 32 testes com SDK MCP instalado |

## Dependências

Obrigatórias locais:

- Bash: disponível;
- Python 3.10+: disponível;
- `tar`, `gzip`, `sha256sum`: disponíveis;
- dependências Python: instaladas em `.venv`.

Opcionais ausentes no ambiente atual:

- `oc`;
- `crc`;
- `yq`;
- Podman.

## Observação importante

Esta validação não acessou API OpenShift, não executou `crc status`, não executou `oc whoami` e não leu kubeconfig. A validação de cluster foi adiada para a fase com autorização explícita.
