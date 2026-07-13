# Matriz MCP, scripts e must-gather

Esta matriz compara as fontes de diagnóstico validadas no CRC/OpenShift Local.

| Domínio | MCP | Scripts | Must-gather | Lacuna | Recomendação |
|---------|-----|---------|-------------|--------|---------------|
| identidade | Forte: contexto, usuário, API e versão | Forte no preflight/coleta geral | Forte, com snapshot amplo | Sem lacuna crítica validada | Manter STDIO e Codex nativo como testes complementares |
| versão | Forte: ClusterVersion | Forte | Forte | Sem parser semântico profundo | Criar parser de condições e histórico |
| Operators | Forte: lista e JSON | Forte: ClusterOperators e OLM | Forte: objetos e logs relacionados | Correlação automática limitada | Implementar análise por condição `Degraded/Progressing/Available` |
| nodes | Forte | Forte | Forte | Pouca interpretação de capacidade | Gerar resumo de allocatable/usage |
| MachineConfig | Parcial | Parcial | Forte | Coletor dedicado ainda raso | Adicionar diagnóstico MCP/script para MCPools/MCO |
| workloads | Médio: foco em pods problemáticos | Médio/forte por alvo | Forte | Must-gather traz volume alto | Criar filtros por namespace/workload |
| eventos | Forte para Warning | Forte | Forte histórico | Risco de confundir histórico com atual | Separar atual, histórico e recorrente |
| storage | Forte: SC/PV/PVC/VA/CSI | Forte | Forte | Falta correlação PVC → Pod → StorageClass | Criar correlacionador |
| networking | Médio/forte | Forte | Forte | Fluxos e políticas precisam interpretação | Criar parser de Services, Endpoints, Routes e NetworkPolicies |
| ingress | Forte | Forte | Forte | Falta análise de certificado/rota | Adicionar resumo por domínio/route |
| DNS | Forte | Forte | Forte | Falta teste ativo, propositalmente não criado | Manter sem pod temporário; usar somente evidências existentes |
| authentication | Forte | Forte | Forte | Falta detalhamento OAuth/console | Adicionar parser seguro sem Secrets |
| API | Médio | Médio | Forte | Logs e condições mais ricos no must-gather | Melhorar domínio API nos coletores |
| etcd | Médio | Médio | Forte | CRC single node limita interpretação | Documentar limitações CRC |
| monitoring | Forte quando CRDs existem | Forte | Forte | Alertas não interpretados semanticamente | Parser de PrometheusRule/Alertmanager opcional |
| OLM | Forte | Forte | Forte | Falta causa provável de CSV/InstallPlan | Criar análise OLM dedicada |
| certificados | Médio | Médio | Parcial | Certificados sensíveis exigem cuidado | Manter somente metadados e CSR |
| CSRs | Forte | Forte | Forte | Sem ação automática | Apenas recomendar aprovação externa |
| alertas | Parcial | Parcial | Forte se monitoring coletado | Alertas ativos não consultados via API Prometheus | Futuro: integração Prometheus read-only |
| capacidade | Médio | Médio | Forte | Metrics API pode estar indisponível | Tratar como recurso opcional |
| logs | Baixo por padrão | Limitado e direcionado | Forte | Alto risco de dados sensíveis | Não publicar bruto; usar sanitização e revisão |

## Conclusão

O MCP e os scripts são melhores para triagem rápida e reproduzível. O must-gather é melhor para análise profunda e suporte, mas deve ser tratado como confidencial. A estratégia recomendada é usar MCP/scripts primeiro e must-gather apenas quando necessário.
