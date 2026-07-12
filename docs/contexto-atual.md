# Operação com contexto atual do oc

O OpenShift AIOps Toolkit usa o contexto atual do `oc` como fonte principal para identificar o cluster e executar diagnósticos consultivos.

## Fluxo recomendado

Confirme o contexto antes de executar diagnósticos:

```bash
oc config current-context
oc whoami
oc whoami --show-server
```

Execute a saúde geral:

```bash
./openshift-aiops health
```

Consulte a identidade detectada:

```bash
./openshift-aiops cluster
```

## Regras operacionais

- O toolkit não executa `oc login`.
- O toolkit não executa `oc config use-context`.
- O toolkit não grava alterações no kubeconfig.
- O toolkit não exige inventário para uso normal.
- O toolkit não exige classificação de ambiente.
- O toolkit não acessa conteúdo de Secrets.
- O toolkit usa comandos `oc` consultivos permitidos por allowlist.

## Opções avançadas

Para consultar outro contexto apenas nesta execução:

```bash
./openshift-aiops health --context outro-contexto
```

Para usar um kubeconfig específico apenas nesta execução:

```bash
./openshift-aiops health --kubeconfig /caminho/kubeconfig
```

Essas opções são passadas ao processo atual do `oc`; nada é persistido.

## Identidade segura do cluster

O identificador usado em evidências e relatórios segue esta prioridade:

1. `Infrastructure.status.infrastructureName`;
2. URL da API retornada por `oc whoami --show-server`;
3. contexto atual retornado por `oc config current-context`;
4. fallback `openshift-cluster`.

O valor é sanitizado para uso seguro em nomes de diretório.

## Capacidades dinâmicas

O toolkit detecta recursos disponíveis com consultas como:

```bash
oc api-resources
oc api-versions
oc auth can-i --list
```

Recursos opcionais ausentes são reportados como:

- `NÃO APLICÁVEL`;
- `SEM PERMISSÃO`;
- `INDISPONÍVEL`;
- `NÃO VERIFICADO`.

A ausência de um recurso opcional não interrompe o diagnóstico geral.

## Inventários opcionais

Inventários em `inventories/` são úteis para aliases, metadados, automações corporativas e comparação de clusters.

Eles não devem conter tokens, senhas ou kubeconfigs completos.

## Must-gather

Must-gather é uma operação especial e exige confirmação explícita digitando o identificador do cluster:

```bash
make must-gather-preflight
make must-gather
```

Os dados brutos ficam em `evidencias/<cluster>/<timestamp>/must-gather/` e são classificados como confidenciais.
