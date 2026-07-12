# Múltiplos clusters

Use o contexto atual do `oc` por padrão. Inventário com `name`, `environment`, `context`, `kubeconfig`, `api_server` e `enabled` é opcional para aliases, metadados, automações corporativas e comparação de clusters.

## Fluxo recomendado

1. Confirmar o contexto atual do `oc`.
2. Validar API OpenShift e usuário autenticado.
3. Executar comandos somente leitura.
4. Salvar evidências sanitizadas.
5. Separar fato, hipótese e conclusão.
6. Gerar plano de remediação sem executá-lo.

```mermaid
flowchart LR
  Operador --> Validacao[Validar contexto]
  Validacao --> Coleta[Coleta somente leitura]
  Coleta --> Sanitizacao[Sanitização]
  Sanitizacao --> Evidencias[Evidências]
  Evidencias --> Relatorio[Relatório]
```

## Comandos úteis

```bash
./openshift-aiops health
./openshift-aiops collect --context <contexto-opcional>
scripts/gerar-relatorio.sh --path evidencias/<cluster>/<coleta>
```
