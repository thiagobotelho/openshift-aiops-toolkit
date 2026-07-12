# Matriz de testes

| ID | Componente | Teste | Tipo | Ambiente | Resultado | Evidência |
|----|------------|-------|------|----------|-----------|-----------|
| TST-001 | Inventário | `pwd`, `git status`, `find` | Estático | Local | PASSOU | Fase 0 |
| TST-002 | Bash | `bash tests/test_scripts.sh` | Estático | Local | PASSOU | saída do comando |
| TST-003 | Python | `python3 -m compileall -q mcp_server` | Estático | Local | PASSOU | saída do comando |
| TST-004 | Unitários | `python3 -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | PASSOU | 36 testes |
| TST-005 | Unitários venv | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | PASSOU | 36 testes |
| TST-006 | Makefile | `make help` | Estático | Local | PASSOU | lista de targets |
| TST-007 | Preflight offline | `make check` | Funcional offline | Local | PASSOU | modo `offline` |
| TST-008 | MCP import | importação do servidor | MCP | Local | PASSOU | teste unitário |
| TST-009 | MCP STDIO | handshake + `tools/list` | MCP | Local | PASSOU | `tests/test_mcp_server.py` |
| TST-010 | Segurança | bloqueio de comandos proibidos | Unitário | Local | PASSOU | `tests/test_commands.py` |
| TST-011 | Sanitização | token/JWT/URL/base64 | Unitário | Local | PASSOU | `tests/test_sanitizers.py` |
| TST-012 | Paths | path traversal e absoluto fora da base | Unitário | Local | PASSOU | `tests/test_validators.py` |
| TST-013 | CRC identidade | confirmar CRC/local | Consultivo | CRC | PASSOU | `crc status`, API `api.crc.testing` |
| TST-014 | CRC coleta geral | coleta em `evidencias/<cluster>/<timestamp>` | Consultivo | CRC | PASSOU | `evidencias/crc-lab/20260711-143517/` |
| TST-015 | MCP consultivo CRC | 15 ferramentas MCP via STDIO | Integração | CRC | PASSOU | `relatorios/validacao-mcp-crc-20260711-143918.json` |
| TST-016 | Codex + MCP ponta a ponta | diagnóstico via ferramentas MCP carregadas na sessão Codex | Integração | Codex/CRC | BLOQUEADO | requer reinício da sessão Codex |
| TST-017 | MCP parâmetros comuns | schemas aceitam `environment`, `cluster`, `timeout` e bloqueiam produção sem confirmação | Unitário | Local | PASSOU | `tests/test_mcp_server.py` |
| TST-018 | MCP sequencial | múltiplas chamadas STDIO no mesmo processo, aguardando resposta por chamada | Integração | CRC | PASSOU | smoke interativo STDIO |
| TST-019 | MCP E2E STDIO | 28 ferramentas consultivas no CRC | Integração | CRC | PASSOU | `relatorios/validacao-e2e-codex-mcp-*.md` |
| TST-020 | Must-gather preflight | valida CRC, destino, help e flags | Consultivo | CRC | PASSOU | preflight de must-gather |
| TST-021 | Must-gather full | coleta padrão com `--all-images=false` | Integração | CRC | PASSOU | `evidencias/<cluster>/<timestamp>/must-gather/` |
| TST-022 | Must-gather checksums | `sha256sum -c` | Integridade | Local | PASSOU | `metadata/checksums.sha256` |
| TST-023 | Must-gather análise offline | índice técnico e scan de sensibilidade | Segurança | Local | PASSOU COM RESSALVA | bruto classificado como confidencial |
| TST-024 | MCP nativo da conversa Codex | tools do `openshift-readonly` injetadas na conversa | Integração | Codex | BLOQUEADO | ambiente não expôs ferramentas nativas |
