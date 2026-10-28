# Plano de validação

Execute conforme [VALIDACAO.md](VALIDACAO.md). A tabela identifica cenários; não declara execução, cobertura atual ou compatibilidade de um cluster específico. Confirme os nomes de comandos e testes na referência Git selecionada.

| ID | Componente | Teste | Tipo | Ambiente | Critério de registro |
|---|---|---|---|---|---|
| TST-001 | Inventário | `pwd`, `git status`, `find` | Estático | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-002 | Bash | `bash tests/test_scripts.sh` | Estático | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-003 | Python | `python3 -m compileall -q mcp_server` | Estático | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-004 | Unitários | `python3 -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-005 | Unitários venv | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-006 | Makefile | `make help` | Estático | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-007 | Preflight offline | `make check` | Funcional offline | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-008 | MCP import | importação do servidor | MCP | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-009 | MCP STDIO | handshake + `tools/list` | MCP | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-010 | Segurança | bloqueio de comandos proibidos | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-011 | Sanitização | token/JWT/URL/base64 | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-012 | Paths | path traversal e absoluto fora da base | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-013 | CRC identidade | confirmar CRC/local | Consultivo | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-014 | CRC coleta geral | coleta em `evidencias/<cluster>/<timestamp>` | Consultivo | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-015 | MCP consultivo CRC | 15 ferramentas MCP via STDIO | Integração | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-016 | Codex + MCP ponta a ponta | diagnóstico via ferramenta MCP carregada pelo Codex CLI | Integração | Codex/CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-017 | MCP parâmetros comuns | schemas aceitam `context`, `kubeconfig`, `timeout`, `output`, `verbose` e parâmetros opcionais de compatibilidade | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-018 | MCP sequencial | múltiplas chamadas STDIO no mesmo processo, aguardando resposta por chamada | Integração | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-019 | MCP E2E STDIO | 28 ferramentas consultivas no CRC | Integração | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-020 | Must-gather preflight | valida CRC, destino, help e flags | Consultivo | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-021 | Must-gather full | coleta padrão com `--all-images=false` | Integração | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-022 | Must-gather checksums | `sha256sum -c` | Integridade | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-023 | Must-gather análise offline | índice técnico e scan de sensibilidade | Segurança | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-024 | MCP nativo da conversa Codex | tools do `openshift-readonly` injetadas na conversa | Integração | Codex | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-025 | CLI central | `./openshift-aiops --help` não acessa cluster e comandos usam contexto atual | Unitário/CLI | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-026 | Saída padronizada | status, JSON, Markdown, tabela e fallback ASCII | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-027 | Segurança estática | ausência de `shell=True`, `os.system`, `os.popen` e `eval` no código executável | Unitário | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-028 | CLI consultiva CRC | comandos `./openshift-aiops health/cluster/operators/nodes/pods/storage/network/ingress/dns/monitoring/olm/certificates/capacity/events` | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-029 | Formatos CLI CRC | human, JSON, Markdown, `NO_COLOR`, ASCII, quiet, verbose e debug sanitizado | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-030 | Descoberta de capacidades | Metrics API, MachineConfigPools, IngressControllers, Routes, PrometheusRules, CSVs e API versions | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-031 | Makefile CRC | targets `make health/cluster/operators/nodes/pods/storage/network/ingress/dns/monitoring/olm/certificates/capacity/events` | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-032 | Scripts CRC | `scripts/preflight.sh`, `scripts/validar-contexto.sh`, `scripts/resumo-saude.sh` | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-033 | MCP CRC | ferramentas solicitadas com `schema_version=1.0` e `execution_status=success` | Integração consultiva | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-034 | Segurança debug CRC | modo debug sem token, senha, kubeconfig, Secret, chave, cookie ou credencial | Segurança | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-035 | Contexto imutável | Comparar contexto antes e depois; preservar o contexto inicial | Segurança | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-036 | Must-gather preflight CRC | destino, suporte a `--dest-dir`, `--all-images=false`, espaço livre e gitignore | Consultivo | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-037 | Must-gather completo CRC | execução com confirmação `crc-tg922`, manifesto e dados brutos locais | Integração | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-038 | Must-gather checksums | `sha256sum -c metadata/checksums.sha256` | Integridade | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-039 | Must-gather análise offline | índice técnico e scan de sensibilidade sem modificar `raw/` | Segurança | Local | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
| TST-040 | Must-gather residual | validação pós-coleta sem pods/namespaces `must-gather` residuais | Consultivo | CRC | Confirmar o contrato descrito na coluna Teste; registrar resultado e evidência fora do Git. |
