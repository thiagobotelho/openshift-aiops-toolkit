# Runbooks

Runbooks descrevem sintomas, impacto, evidências esperadas, causas comuns, escalonamento e plano proposto.

Consulte também `runbooks/README.md`.

## Papel no processo

Runbooks são guias humanos de triagem. Eles ajudam a decidir quais diagnósticos direcionados executar depois da coleta completa segura.

Eles não são scripts e não fazem alteração no cluster.

## Fluxo recomendado

1. Execute `scripts/coletar-cluster.sh`.
2. Identifique o sintoma principal.
3. Abra o runbook correspondente.
4. Execute diagnósticos direcionados somente no alvo necessário.
5. Registre achados e plano proposto em `templates/`.

## Exemplo

```bash
scripts/coletar-cluster.sh
scripts/diagnosticar-pod.sh <namespace> <pod> --tail 100
```
