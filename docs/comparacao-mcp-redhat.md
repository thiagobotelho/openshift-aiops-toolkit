# Comparação com o MCP Server oficial da Red Hat/OpenShift

Referência oficial consultada: documentação Red Hat OpenShift Container Platform 4.22, capítulo **MCP server** em `docs.redhat.com`.

## Objetivo

| Item | Toolkit customizado | MCP oficial Red Hat/OpenShift |
|------|---------------------|-------------------------------|
| Objetivo | Diagnóstico local, coleta de evidências, relatórios e integração Codex em modo read-only | Expor ferramentas MCP para interação com o OpenShift por clientes compatíveis |
| Local de execução | Máquina do operador, usando `oc` autenticado | Componentes instalados no cluster via Helm e gateway |
| Transporte | STDIO local | HTTP/MCP via rota/gateway |
| Escopo | Diagnóstico e evidências, com scripts e relatórios | Ferramentas MCP para recursos do cluster |
| Segurança | Allowlist local, bloqueio de escrita, sanitização e proteção de produção | RBAC, gateway, autenticação/autorização e recomendações de guardrails |

## Segurança

O toolkit customizado bloqueia comandos de escrita por implementação local e não expõe shell genérico. A documentação oficial da Red Hat recomenda controles como RBAC enforcement, autenticação via gateway e cuidado com privacidade/redação de dados.

## Operação

| Aspecto | Toolkit customizado | MCP oficial |
|---------|---------------------|-------------|
| Instalação no cluster | Não necessária | Necessária |
| Impacto no CRC | Baixo, exceto must-gather autorizado | Requer componentes adicionais |
| Adequado para laboratório local | Sim | Possível, mas mais pesado |
| Adequado para operação corporativa | Parcial, com hardening | Mais alinhado para operação integrada |
| Evidências e relatórios | Sim | Não é o foco principal |

## Sobreposições

- Consulta de estado do cluster.
- Uso por clientes compatíveis com MCP.
- Dependência de RBAC e contexto autorizado.
- Necessidade de proteção contra exposição de dados sensíveis.

## Vantagens do toolkit customizado

- Não exige instalação no cluster.
- Produz evidências, checksums e relatórios.
- Permite fluxo offline com must-gather.
- Mantém escopo estritamente assistivo/read-only.
- Facilita laboratório CRC e troubleshooting local.

## Pontos que podem ser adotados futuramente

- Modelo de autenticação/autorização com gateway.
- Separação formal de toolsets.
- User-agent/audit trail específico para chamadas de IA.
- Controles de acesso refinados por CRD/recurso.
- Integração com políticas corporativas de AI safety.

## Conclusão

O MCP oficial da Red Hat é mais adequado quando a organização deseja um serviço MCP operacional dentro do OpenShift com gateway e RBAC. O toolkit customizado continua útil como ferramenta local de diagnóstico, coleta, análise e preparação de evidências, especialmente para CRC/laboratório e para ambientes onde instalar componentes no cluster não é desejado.

