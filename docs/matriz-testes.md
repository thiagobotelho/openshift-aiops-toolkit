# Matriz de testes

| ID | Componente | Teste | Tipo | Ambiente | Resultado | Evidência |
|----|------------|-------|------|----------|-----------|-----------|
| TST-001 | Inventário | `pwd`, `git status`, `find` | Estático | Local | PASSOU | Fase 0 |
| TST-002 | Bash | `bash tests/test_scripts.sh` | Estático | Local | PASSOU | saída do comando |
| TST-003 | Python | `python3 -m compileall -q mcp_server` | Estático | Local | PASSOU | saída do comando |
| TST-004 | Unitários | `python3 -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | PASSOU | 49 testes |
| TST-005 | Unitários venv | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | PASSOU | 49 testes via `tests/run.sh` |
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
| TST-016 | Codex + MCP ponta a ponta | diagnóstico via ferramenta MCP carregada pelo Codex CLI | Integração | Codex/CRC | PASSOU | `codex exec --sandbox read-only` chamou `current_context`, `cluster_identity` e `cluster_health` via MCP nativo |
| TST-017 | MCP parâmetros comuns | schemas aceitam `context`, `kubeconfig`, `timeout`, `output`, `verbose` e parâmetros opcionais de compatibilidade | Unitário | Local | PASSOU | `tests/test_mcp_server.py` |
| TST-018 | MCP sequencial | múltiplas chamadas STDIO no mesmo processo, aguardando resposta por chamada | Integração | CRC | PASSOU | smoke interativo STDIO |
| TST-019 | MCP E2E STDIO | 28 ferramentas consultivas no CRC | Integração | CRC | PASSOU | `relatorios/validacao-e2e-codex-mcp-*.md` |
| TST-020 | Must-gather preflight | valida CRC, destino, help e flags | Consultivo | CRC | PASSOU | preflight de must-gather |
| TST-021 | Must-gather full | coleta padrão com `--all-images=false` | Integração | CRC | PASSOU | `evidencias/<cluster>/<timestamp>/must-gather/` |
| TST-022 | Must-gather checksums | `sha256sum -c` | Integridade | Local | PASSOU | `metadata/checksums.sha256` |
| TST-023 | Must-gather análise offline | índice técnico e scan de sensibilidade | Segurança | Local | PASSOU | bruto classificado como confidencial e não versionado |
| TST-024 | MCP nativo da conversa Codex | tools do `openshift-readonly` injetadas na conversa | Integração | Codex | PASSOU | tool `openshift-readonly/current_context` carregada e concluída pelo Codex CLI |
| TST-025 | CLI central | `./openshift-aiops --help` não acessa cluster e comandos usam contexto atual | Unitário/CLI | Local | PASSOU | `tests/test_formatters_cli.py` |
| TST-026 | Saída padronizada | status, JSON, Markdown, tabela e fallback ASCII | Unitário | Local | PASSOU | `tests/test_formatters_cli.py` |
| TST-027 | Segurança estática | ausência de `shell=True`, `os.system`, `os.popen` e `eval` no código executável | Unitário | Local | PASSOU | `tests/test_commands.py` |
| TST-028 | CLI consultiva CRC | comandos `./openshift-aiops health/cluster/operators/nodes/pods/storage/network/ingress/dns/monitoring/olm/certificates/capacity/events` | Integração consultiva | CRC | PASSOU | `relatorios/validacao-consultiva-crc-20260712.md` |
| TST-029 | Formatos CLI CRC | human, JSON, Markdown, `NO_COLOR`, ASCII, quiet, verbose e debug sanitizado | Integração consultiva | CRC | PASSOU | `relatorios/validacao-consultiva-crc-20260712.md` |
| TST-030 | Descoberta de capacidades | Metrics API, MachineConfigPools, IngressControllers, Routes, PrometheusRules, CSVs e API versions | Integração consultiva | CRC | PASSOU | `relatorios/validacao-consultiva-crc-20260712.md` |
| TST-031 | Makefile CRC | targets `make health/cluster/operators/nodes/pods/storage/network/ingress/dns/monitoring/olm/certificates/capacity/events` | Integração consultiva | CRC | PASSOU | `relatorios/validacao-consultiva-crc-20260712.md` |
| TST-032 | Scripts CRC | `scripts/preflight.sh`, `scripts/validar-contexto.sh`, `scripts/resumo-saude.sh` | Integração consultiva | CRC | PASSOU | `resumo-saude.sh --quiet` retorna saúde sem criar coleta local |
| TST-033 | MCP CRC | ferramentas solicitadas com `schema_version=1.0` e `execution_status=success` | Integração consultiva | CRC | PASSOU | payload de compatibilidade preservado em `result` |
| TST-034 | Segurança debug CRC | modo debug sem token, senha, kubeconfig, Secret, chave, cookie ou credencial | Segurança | CRC | PASSOU | scan de saída debug |
| TST-035 | Contexto imutável | contexto antes e depois da validação permaneceu `crc-admin` | Segurança | CRC | PASSOU | `oc config current-context` |
| TST-036 | Must-gather preflight CRC | destino, suporte a `--dest-dir`, `--all-images=false`, espaço livre e gitignore | Consultivo | CRC | PASSOU | `docs/validacao-must-gather-crc-20260712.md` |
| TST-037 | Must-gather completo CRC | execução com confirmação `crc-tg922`, manifesto e dados brutos locais | Integração | CRC | PASSOU | `docs/validacao-must-gather-crc-20260712.md` |
| TST-038 | Must-gather checksums | `sha256sum -c metadata/checksums.sha256` | Integridade | Local | PASSOU | `docs/validacao-must-gather-crc-20260712.md` |
| TST-039 | Must-gather análise offline | índice técnico e scan de sensibilidade sem modificar `raw/` | Segurança | Local | PASSOU | 1294 indicadores potenciais classificados para revisão antes de compartilhamento |
| TST-040 | Must-gather residual | validação pós-coleta sem pods/namespaces `must-gather` residuais | Consultivo | CRC | PASSOU | `docs/validacao-must-gather-crc-20260712.md` |
