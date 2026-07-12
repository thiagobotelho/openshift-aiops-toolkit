# Continuar validação Codex + MCP

Use este prompt após reiniciar o Codex para carregar o servidor MCP `openshift-readonly`.

## Contexto

O repositório está em:

```bash
<caminho-do-repositorio>/openshift-aiops-toolkit
```

O servidor MCP foi registrado no Codex CLI como `openshift-readonly`, usando:

- `.venv/bin/python`;
- `PYTHONPATH` apontando para o repositório;
- `OPENSHIFT_AIOPS_COMMAND_PREFIX=flatpak-spawn --host`;
- `OPENSHIFT_AIOPS_OC_BIN=<caminho-do-oc-do-crc>`.

## Regras

- Use apenas ferramentas MCP consultivas do `openshift-readonly`.
- Não execute comandos de escrita.
- Não execute `oc adm must-gather`.
- Não crie Pods temporários.
- Não acesse conteúdo de Secrets.
- Não altere contexto.
- Não faça remediação.

## Objetivo

Realizar diagnóstico consultivo do CRC/OpenShift Local e gerar:

```text
relatorios/validacao-crc-<timestamp>.md
```

## Etapas

1. Validar contexto atual.
2. Validar identidade do cluster.
3. Confirmar API `https://api.crc.testing:6443`.
4. Confirmar ambiente `laboratory`.
5. Analisar ClusterVersion.
6. Analisar ClusterOperators.
7. Analisar node.
8. Analisar Pods problemáticos.
9. Analisar eventos Warning.
10. Analisar storage.
11. Analisar network, ingress e DNS.
12. Analisar capacidade.
13. Correlacionar evidências.
14. Registrar achados, limitações e próximos passos.

## Saída esperada

- Identificação do ambiente.
- Versão do toolkit.
- Versão do Codex, MCP, `oc`, CRC e OpenShift.
- Ferramentas MCP utilizadas.
- Achados e evidências.
- Nível de confiança.
- Limitações.
- Falhas do toolkit.
- Melhorias recomendadas.
- Conclusão do teste.
