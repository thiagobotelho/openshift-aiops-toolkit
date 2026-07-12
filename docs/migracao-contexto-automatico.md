# Migração para contexto automático

Este guia descreve a migração do modelo antigo, baseado em `--environment` e `--cluster`, para o modelo atual, baseado no contexto ativo do `oc`.

## O que mudou

Antes, vários fluxos pediam ambiente lógico e nome do cluster:

```bash
scripts/coletar-cluster.sh --cluster crc-lab --environment laboratory
scripts/diagnosticar-operator.sh authentication --cluster crc-lab --environment laboratory
```

Agora, o toolkit usa por padrão o contexto atual:

```bash
oc whoami
oc whoami --show-server
oc config current-context
./openshift-aiops health
```

O toolkit não executa `oc login`, não troca contexto e não grava alterações no kubeconfig.

## Equivalência de comandos

| Fluxo antigo | Fluxo atual |
| --- | --- |
| `scripts/coletar-cluster.sh --cluster <cluster> --environment <ambiente>` | `./openshift-aiops collect` |
| `scripts/diagnosticar-operator.sh authentication --cluster <cluster>` | `./openshift-aiops operator authentication` ou `scripts/diagnosticar-operator.sh authentication` |
| `scripts/diagnosticar-node.sh <node> --environment laboratory` | `./openshift-aiops node <node>` ou `scripts/diagnosticar-node.sh <node>` |
| `scripts/preflight.sh --environment laboratory --cluster crc-lab` | `make check-cluster` |
| `make health ENVIRONMENT=laboratory CLUSTER=crc-lab` | `make health` |

Os parâmetros antigos continuam aceitos temporariamente para compatibilidade, mas exibem aviso de depreciação e não são usados para bloquear consultas read-only.

## Opções avançadas

Para consultar outro contexto sem alterar o contexto persistente:

```bash
./openshift-aiops health --context outro-contexto
```

Para usar um kubeconfig específico apenas nesta execução:

```bash
./openshift-aiops health --kubeconfig /caminho/kubeconfig
```

Essas opções são passadas diretamente ao `oc` no processo atual. O toolkit não executa `oc config use-context`.

## Identificação automática do cluster

O identificador seguro do cluster é derivado, nesta ordem, de:

1. `Infrastructure.status.infrastructureName`, quando disponível;
2. URL da API retornada por `oc whoami --show-server`;
3. contexto atual retornado por `oc config current-context`;
4. fallback `openshift-cluster`.

O valor é sanitizado para uso em diretórios de evidência e relatórios.

## Capacidades dinâmicas

Nem todo cluster possui os mesmos recursos. O toolkit usa consultas como `oc api-resources`, `oc api-versions` e `oc auth can-i` para classificar recursos como:

- `OK`;
- `ALERTA`;
- `CRÍTICO`;
- `INFORMATIVO`;
- `NÃO APLICÁVEL`;
- `SEM PERMISSÃO`;
- `INDISPONÍVEL`;
- `NÃO VERIFICADO`.

Um recurso opcional ausente não deve falhar o diagnóstico inteiro.

## Inventários

Inventários em `inventories/` continuam úteis para aliases, metadados, automações corporativas e comparação de clusters, mas não são pré-requisito.

Não grave tokens, senhas ou kubeconfigs completos nesses arquivos.

## Must-gather

Must-gather continua sendo operação especial. Mesmo no modelo de contexto automático, ele exige confirmação explícita digitando o identificador do cluster:

```bash
make must-gather-preflight
make must-gather
```

Essa proteção vale para qualquer cluster, sem depender de classificação como produção, laboratório ou homologação.
