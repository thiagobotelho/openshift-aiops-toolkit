# Validação CRC/OpenShift Local

Este documento descreve a validação consultiva do toolkit em CRC/OpenShift Local usando o contexto atual do `oc`.

## Última validação

- Data: 2026-07-12
- Contexto: `crc-admin`
- API: `https://api.crc.testing:6443`
- Usuário: `kubeadmin`
- OpenShift: `4.22.1`
- Cluster detectado: `crc-tg922`
- Resultado: **APROVADO PARA LABORATÓRIO**
- Relatório: `relatorios/validacao-consultiva-crc-20260712.md`
- Must-gather: `docs/validacao-must-gather-crc-20260712.md`

Observações operacionais:

- quando `oc` não está no `PATH` da sessão, use `OPENSHIFT_AIOPS_OC_BIN`;
- `health` ainda não transforma `Upgradeable=False` em alerta;
- RBAC limitado não foi exercitado porque o usuário atual é `kubeadmin`.

## Must-gather validado

O fluxo de must-gather usa confirmação explícita pelo identificador do cluster. Na validação CRC de 2026-07-12, o identificador usado foi `crc-tg922`.

Resumo:

- exit code: `0`;
- duração: `37.907s`;
- arquivos brutos: `4331`;
- tamanho bruto aproximado: `199441515 bytes`;
- checksums: PASSOU;
- análise offline: PASSOU;
- pods/namespaces residuais `must-gather`: não encontrados.

Detalhes: `docs/validacao-must-gather-crc-20260712.md`.

## Pré-check humano

Confirme no terminal:

```bash
crc status
oc config current-context
oc whoami
oc whoami --show-server
```

O toolkit não executa `oc login` e não troca contexto.

## Variáveis opcionais para ambiente isolado

Use apenas quando o `oc` estiver no host e o toolkit estiver rodando em ambiente isolado:

```bash
export OPENSHIFT_AIOPS_COMMAND_PREFIX="flatpak-spawn --host"
export OPENSHIFT_AIOPS_OC_BIN="<caminho-real-do-oc>"
```

## Validação offline

Não acessa a API do OpenShift:

```bash
make check
tests/run.sh
bash tests/test_scripts.sh
```

## Validação consultiva no CRC

Execute somente depois de confirmar que o contexto atual aponta para o CRC desejado:

```bash
make check-cluster
./openshift-aiops health
./openshift-aiops cluster
./openshift-aiops operators
./openshift-aiops nodes
./openshift-aiops pods
./openshift-aiops storage
./openshift-aiops network
./openshift-aiops ingress
./openshift-aiops dns
./openshift-aiops monitoring
./openshift-aiops olm
./openshift-aiops certificates
./openshift-aiops capacity
./openshift-aiops events
```

Valide formatos:

```bash
./openshift-aiops health --output json
./openshift-aiops health --output markdown
NO_COLOR=1 ./openshift-aiops health
./openshift-aiops health --ascii
./openshift-aiops health --quiet
./openshift-aiops health --verbose
```

## Coleta de evidências

```bash
./openshift-aiops collect
LATEST="$(ls -dt evidencias/*/* | head -1)"
scripts/gerar-relatorio.sh --path "$LATEST" --output relatorios/relatorio-diagnostico.md
```

## Must-gather

Não faz parte da validação básica. Só execute com autorização explícita:

```bash
make must-gather-preflight
make must-gather
```

Será exigida confirmação digitando o identificador do cluster.

## Comandos não permitidos durante a validação

- qualquer `oc apply/create/delete/patch/edit`;
- `oc exec`, `oc debug`, `oc rsh`;
- criação de Pods temporários;
- acesso ao conteúdo de Secrets;
- troca de contexto;
- must-gather sem autorização separada.
