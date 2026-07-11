# Múltiplos clusters

Use inventário com `name`, `environment`, `context`, `kubeconfig`, `api_server` e `enabled`.

## Fluxo recomendado

1. Confirmar ambiente e cluster.
2. Validar contexto OpenShift e usuário autenticado.
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
scripts/preflight.sh
scripts/coletar-cluster.sh --cluster cluster-dev --environment development
scripts/gerar-relatorio.sh --path evidencias/cluster-dev/<coleta>
```
