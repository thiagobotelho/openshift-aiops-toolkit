# Auditoria estática

- Data: 2026-07-11
- Escopo: Fases 0, 1 e 2 do repositório `openshift-aiops-toolkit`
- Ambiente: validação local/offline, sem acesso ao CRC ou a qualquer API OpenShift

## Inventário técnico

Componentes encontrados:

- scripts Bash em `scripts/` e bibliotecas em `scripts/lib/`;
- pacote Python `mcp_server/`;
- servidor MCP `openshift-readonly`;
- configurações em `config/`;
- inventários de exemplo em `inventories/`;
- prompts, templates, runbooks e documentação;
- testes unitários e estáticos em `tests/`.

Arquivos vazios esperados:

- `evidencias/.gitkeep`;
- `relatorios/.gitkeep`;
- `logs/.gitkeep`.

Artefatos locais ignorados:

- `__pycache__/`;
- `.venv/`.

## Verificações executadas

| Verificação | Resultado | Evidência |
|----|----|----|
| `pwd` | PASSOU | diretório do repo confirmado |
| `git status --short` | PASSOU | worktree inicialmente limpo |
| `git branch --show-current` | PASSOU | `main` |
| inventário com `find` | PASSOU | estrutura identificada |
| leitura de README/AGENTS/Makefile/config/scripts/tests | PASSOU | arquivos revisados |
| `bash tests/test_scripts.sh` | PASSOU | sintaxe Bash e permissões |
| `python3 -m compileall -q mcp_server` | PASSOU | Python compila |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | PASSOU | suíte unitária |
| validação TOML/YAML/JSON | PASSOU | sem erros reportados |
| busca por padrões inseguros | PASSOU COM RESSALVAS | ocorrências restantes são denylist/testes |
| servidor MCP com SDK real | PASSOU | handshake e `tools/list` válidos |

## Falhas encontradas e correções

| ID | Severidade | Problema | Arquivos | Status |
|----|----|----|----|----|
| AUD-001 | P1 | `make help` falhava com `missing separator` por heredoc malformado no target `clean`. | `Makefile` | Corrigido |
| AUD-002 | P1 | `make check`/preflight não possuíam modo offline seguro para validação local sem consultar cluster. | `Makefile`, `mcp_server/commands.py` | Corrigido |
| AUD-003 | P1 | Servidor MCP com SDK real expunha schemas achatados em `arguments`, perdendo schemas específicos. | `mcp_server/server.py`, `tests/test_mcp_server.py` | Corrigido |
| AUD-004 | P1 | Bloqueio de Secrets cobria `secrets`, mas não `secret/foo` ou listas combinadas como `pods,secrets`. | `mcp_server/commands.py`, `tests/test_commands.py` | Corrigido |
| AUD-005 | P2 | `install.sh` exigia `oc` e `jq`, bloqueando instalação local/offline. | `scripts/install.sh` | Corrigido |
| AUD-006 | P2 | Scripts usavam `python3` mesmo quando `.venv` existia, reportando SDK MCP ausente. | `scripts/lib/common.sh` | Corrigido |
| AUD-007 | P2 | Paths locais eram aceitos sem restrição consistente ao diretório do projeto. | `mcp_server/commands.py`, `mcp_server/validators.py` | Corrigido |
| AUD-008 | P2 | Script de configuração Codex MCP alterava configuração sem confirmação explícita. | `scripts/configurar-codex-mcp.sh` | Corrigido |
| AUD-009 | P1 | Ferramentas MCP read-only não aceitavam parâmetros comuns (`environment`, `cluster`, `timeout`) no schema publicado pelo SDK. | `mcp_server/tools/base.py`, `mcp_server/tools/__init__.py`, `tests/test_mcp_server.py` | Corrigido |

## Riscos residuais

- O teste ponta a ponta dentro da própria sessão Codex requer reinício para carregar o MCP recém-configurado.
- `oc` e `crc` não estão no PATH do ambiente atual do Codex; a validação contra CRC usa `flatpak-spawn --host` e o `oc` do cache do CRC.
- `oc adm must-gather` permanece não executado; deve ser tratado como operação controlada e separada.

## Recomendações

1. Reiniciar a sessão Codex para validar o MCP carregado pelo próprio Codex.
2. Manter `make check` offline como verificação padrão local e usar `make check-cluster` apenas após confirmar que o contexto é CRC/OpenShift Local.
3. Manter os testes negativos como barreira para mudanças futuras no MCP/CLI.
