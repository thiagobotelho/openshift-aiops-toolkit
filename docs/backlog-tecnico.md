# Backlog técnico

## Obrigatórias antes de uso operacional amplo

| Prioridade | Item | Status |
|----|----|----|
| P1 | Validar CRC com aprovação explícita | Concluído |
| P1 | Testar ferramentas MCP consultivas contra CRC | Concluído |
| P1 | Gerar relatório real de validação CRC | Concluído |
| P1 | Confirmar localização dos binários `oc` e `crc` no host | Concluído |
| P1 | Teste ponta a ponta via MCP STDIO | Concluído |
| P1 | Must-gather controlado no CRC | Concluído |
| P1 | Teste MCP nativo dentro da conversa Codex | Bloqueado pelo ambiente |

## Recomendadas

| Prioridade | Item | Status |
|----|----|----|
| P2 | Adicionar fixtures JSON mais ricas para ClusterVersion/ClusterOperators | Futuro curto |
| P2 | Melhorar comparação semântica de coletas | Futuro curto |
| P2 | Adicionar detecção explícita de recursos opcionais por versão OpenShift | Futuro curto |
| P2 | Criar exemplos de relatórios preenchidos com dados sanitizados | Futuro curto |
| P2 | Criar parsers profundos do must-gather por domínio | Futuro curto |
| P2 | Reduzir falsos positivos do scanner de sensibilidade | Futuro curto |

## Futuras

- portal web;
- RAG;
- integração com Grafana/Prometheus/Zabbix;
- integração ACM/ACS/AAP;
- abertura automática de chamados;
- remediação automática.

Esses itens não devem ser implementados nesta rodada porque ampliam escopo e risco.
