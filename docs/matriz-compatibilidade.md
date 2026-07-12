# Matriz de compatibilidade

| Componente | Versão/estado validado | Resultado | Observação |
|----|----|----|----|
| Bash | 5.3.15 | PASSOU | ambiente local |
| Python | 3.13.14 | PASSOU | acima do mínimo 3.10 |
| pip | 26.1.2 | PASSOU | ambiente local |
| SDK MCP | 1.28.1 na `.venv` | PASSOU | instalado pelo `scripts/install.sh` |
| Codex CLI | disponível | PASSOU | `codex --help` e `codex mcp --help` |
| `jq` | disponível | PASSOU | ferramenta local |
| `yq` | ausente | NÃO APLICÁVEL | opcional |
| `oc` | disponível via `flatpak-spawn --host` e cache CRC 4.22.1 | PASSOU | `OPENSHIFT_AIOPS_OC_BIN` |
| `crc` | disponível via `flatpak-spawn --host` | PASSOU | CRC Running |
| OpenShift Local/CRC | 4.22.1 | PASSOU | API `https://api.crc.testing:6443` |
| OpenShift remoto DEV/HML/PRD | fora de escopo | NÃO APLICÁVEL | não acessar nesta atividade |
