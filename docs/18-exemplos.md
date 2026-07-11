# Exemplos

Exemplos: ClusterOperator Degraded, node NotReady, Pod CrashLoopBackOff, PVC Pending, DNS/Ingress/API degradados e upgrade bloqueado.

## Fluxo recomendado

1. Confirmar ambiente e cluster.
2. Validar contexto OpenShift e usuário autenticado.
3. Executar comandos somente leitura.
4. Salvar evidências sanitizadas.
5. Separar fato, hipótese e conclusão.
6. Gerar plano de remediação sem executá-lo.


## Comandos úteis

```bash
scripts/preflight.sh
scripts/coletar-cluster.sh --cluster cluster-dev --environment development
scripts/gerar-relatorio.sh --path evidencias/cluster-dev/<coleta>
```
