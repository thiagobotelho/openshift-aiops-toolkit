# Prompts

Prompts em `prompts/` impõem restrições de leitura, uso de evidências, declaração de confiança e formato de saída esperado.

Consulte também `prompts/README.md`.

## Papel no processo

Prompts não coletam dados e não executam remediação. Eles orientam a análise feita por Codex ou outro assistente, usando evidências já coletadas pelos scripts ou consultas consultivas via MCP.

## Fluxo recomendado

1. Coletar evidências com `scripts/coletar-cluster.sh`.
2. Escolher o prompt do domínio investigado.
3. Informar o caminho das evidências.
4. Exigir separação entre fato, hipótese e recomendação.
5. Registrar achados em `templates/achado.md`.

## Exemplo

```text
Use o prompt prompts/diagnostico-cluster.md.
Analise as evidências em evidencias/crc-lab/<timestamp>.
Não execute remediação.
Separe fatos, hipóteses, riscos e próximos passos.
```
