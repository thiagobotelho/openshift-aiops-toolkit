# Must-gather

Coleta grande e potencialmente sensível. Exige confirmação, valida espaço, gera hash e não compartilha automaticamente.

## Fluxo recomendado

1. Confirmar o contexto atual do `oc`.
2. Validar API OpenShift e usuário autenticado.
3. Executar comandos somente leitura.
4. Salvar evidências sanitizadas.
5. Separar fato, hipótese e conclusão.
6. Gerar plano de remediação sem executá-lo.


## Comandos úteis

```bash
make must-gather-preflight
make must-gather
scripts/gerar-relatorio.sh --path evidencias/<cluster>/<coleta>
```
