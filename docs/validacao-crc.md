# Validação CRC

- Data: 2026-07-11
- Status: PASSOU COM RESSALVAS
- Ambiente: CRC/OpenShift Local usado exclusivamente como laboratório

## Confirmação do ambiente

Sinais confirmados:

- `crc status`: CRC VM Running e OpenShift Running;
- versão OpenShift Local: 4.22.1;
- contexto: `default/api-crc-testing:6443/kubeadmin`;
- API: `https://api.crc.testing:6443`;
- Infrastructure: `crc-tg922`;
- topologia: `SingleReplica`;
- `oc auth can-i get pods --all-namespaces`: yes;
- `oc auth can-i get clusteroperators`: yes;
- `oc auth can-i get nodes`: yes.

## Variáveis usadas no ambiente de validação

```bash
export OPENSHIFT_AIOPS_COMMAND_PREFIX="flatpak-spawn --host"
export OPENSHIFT_AIOPS_OC_BIN="<caminho-do-oc-do-crc>"
```

## Comandos executados

```bash
scripts/preflight.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/validar-contexto.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/coletar-cluster.sh --environment laboratory --cluster crc-lab --output-dir evidencias --timeout 60
scripts/diagnosticar-operator.sh authentication --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-node.sh crc --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-namespace.sh openshift-console --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-pod.sh openshift-console console-648cfb69b5-rf2mz --environment laboratory --cluster crc-lab --tail 100 --timeout 60
scripts/diagnosticar-workload.sh openshift-console console --kind deployment --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-storage.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-network.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-ingress.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-dns.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-olm.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/diagnosticar-monitoring.sh --environment laboratory --cluster crc-lab --timeout 60
scripts/verificar-capacidade.sh --environment laboratory --cluster crc-lab --timeout 60
```

## Evidências

- Coleta geral: `evidencias/crc-lab/20260711-143517/`;
- Coletas direcionadas: `evidencias/targeted/20260711-143727-*` até `evidencias/targeted/20260711-143732-*`;
- Relatório: `relatorios/validacao-crc-20260711-144131.md`;
- Validação MCP: `relatorios/validacao-mcp-crc-20260711-143918.json`.
- Must-gather controlado: `evidencias/<cluster>/<timestamp>/must-gather/`;
- Análise offline do must-gather: `relatorios/analise-must-gather-crc-<timestamp>.md`.

## Validações

| Item | Resultado |
|----|----|
| criação de diretórios | PASSOU |
| manifesto JSON | PASSOU |
| checksums SHA256 | PASSOU |
| exit codes da coleta geral | PASSOU |
| sanitização | PASSOU |
| ausência de conteúdo de Secrets | PASSOU |
| ausência de kubeconfig | PASSOU |
| logs limitados de Pod | PASSOU |
| logs anteriores de Pod | PASSOU COM RESSALVA: não existiam logs anteriores |
| must-gather controlado | PASSOU |
| checksums do must-gather | PASSOU |
| análise offline do must-gather | PASSOU COM RESSALVA: dados brutos são confidenciais |

## Achados

- ClusterVersion `Upgradeable=False` por motivos esperados no laboratório: overrides do ClusterVersion e operadores com limite máximo de OCP 4.22.
- Usuário de validação: `kubeadmin`, com permissões amplas; a segurança do teste dependeu do modo read-only do toolkit.
- Must-gather gerou indicadores de possível sensibilidade; isso é esperado e reforça que `evidencias/**` não deve ser versionado nem publicado.

## Comandos não executados

- qualquer `oc apply/create/delete/patch/edit`;
- `oc exec`, `oc debug`, `oc rsh`;
- criação de Pods temporários;
- acesso ao conteúdo de Secrets.
