# Prompts

Esta pasta contém prompts para orientar análises com Codex ou outro assistente de IA.

Os prompts não executam nada sozinhos. Eles servem para dar contexto, regras de segurança, formato de saída e foco técnico.

## Estado atual

- `continuar-validacao-mcp.md`: fluxo mais completo para validar Codex + MCP `openshift-readonly`.
- `diagnostico-*.md`: prompts base por domínio OpenShift.
- `analise-must-gather.md`: prompt base para analisar saída de must-gather.
- `relatorio-*.md`, `plano-remediacao.md` e `validacao-pos-mudanca.md`: prompts para estruturar documentação.

Os prompts de domínio são intencionalmente genéricos. Use junto com evidências reais, runbooks e contexto do cluster.

## Como usar

Exemplo com evidências já coletadas:

```text
Use o prompt prompts/diagnostico-cluster.md.
Analise as evidências em evidencias/crc-lab/<timestamp>.
Não execute remediação.
Separe fatos, hipóteses e recomendações.
```

Exemplo com MCP:

```text
Continue a validação Codex + MCP usando o prompt prompts/continuar-validacao-mcp.md.
Tenho autorização para executar as fases até o preflight do must-gather.
```

## Regras esperadas

- Não inventar evidências.
- Não acessar Secrets.
- Não executar escrita.
- Não trocar contexto sem confirmação.
- Declarar nível de confiança.
- Separar fato, hipótese, risco e recomendação.
