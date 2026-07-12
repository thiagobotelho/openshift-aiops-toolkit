# Processo operacional — OpenShift AIOps Toolkit

Este documento explica como o toolkit é usado na prática, o que roda localmente, o que consulta o cluster e como entram `prompts/`, `runbooks/` e `templates/`.

## Visão curta

O usuário clona o repositório em uma máquina de operação, instala dependências Python em um ambiente virtual local e executa scripts somente leitura contra o OpenShift usando o `oc` já autenticado.

O toolkit não instala nada no cluster, não cria operadores, não aplica YAML e não faz remediação automática.

## Quem faz o quê

| Ator | Responsabilidade |
| --- | --- |
| Operador humano | Clona o repo, autentica no OpenShift, confirma contexto, decide escopo, revisa evidências e aprova qualquer ação fora do toolkit. |
| Scripts do toolkit | Fazem validações, executam consultas `oc` permitidas, coletam evidências, geram relatórios e pacotes locais. |
| MCP `openshift-readonly` | Expõe ferramentas consultivas para Codex, sem terminal genérico e sem comandos de escrita. |
| Codex | Ajuda a analisar evidências, usar prompts, estruturar achados e sugerir próximos passos sem executar remediação. |
| OpenShift API | Fonte consultada pelo `oc`; não recebe alterações pelo toolkit. |

## Onde cada coisa roda

| Etapa | Onde roda | O que acessa | O que grava |
| --- | --- | --- | --- |
| `scripts/install.sh` | Máquina local | Internet/PyPI para dependências Python | `.venv/`, caches Python locais |
| `make check` | Máquina local | Não acessa cluster | Nada relevante fora do repo |
| `make check-cluster` | Máquina local via `oc` | API OpenShift atual | Saída no terminal |
| `scripts/coletar-cluster.sh` | Máquina local via `oc` | API OpenShift atual | `evidencias/<cluster>/<timestamp>/` |
| `scripts/diagnosticar-*.sh` | Máquina local via `oc` | API OpenShift atual | Nova pasta em `evidencias/targeted/<timestamp>/` |
| `scripts/gerar-relatorio.sh` | Máquina local | Evidências locais | `relatorios/*.md` |
| `scripts/configurar-codex-mcp.sh` | Máquina local | Configuração do Codex CLI | Registro MCP global do Codex |
| `make must-gather` | Máquina local via `oc` | API OpenShift atual | `evidencias/<cluster>/<timestamp>/must-gather/` |

## Instalação local ou temporária?

As duas opções são válidas.

### Uso normal em máquina de operação

Clone uma vez e mantenha o repositório atualizado:

```bash
git clone https://github.com/thiagobotelho/openshift-aiops-toolkit.git
cd openshift-aiops-toolkit
scripts/install.sh
```

O script cria `.venv/` dentro do repo. Esse diretório é local, ignorado pelo Git e pode ser removido com:

```bash
scripts/uninstall.sh
```

### Uso temporário

Também é seguro clonar em um diretório temporário, executar uma coleta e apagar depois:

```bash
git clone https://github.com/thiagobotelho/openshift-aiops-toolkit.git
cd openshift-aiops-toolkit
scripts/install.sh
scripts/coletar-cluster.sh
```

Antes de apagar, copie apenas os relatórios/evidências que você precisa preservar.

## Fluxo recomendado ponta a ponta

### 1. Clonar ou atualizar

```bash
git clone https://github.com/thiagobotelho/openshift-aiops-toolkit.git
cd openshift-aiops-toolkit
```

Se já existe localmente:

```bash
git pull origin main
```

### 2. Instalar dependências locais

```bash
scripts/install.sh
```

O que faz:

- cria `.venv/`;
- instala dependências Python;
- valida importação do toolkit;
- roda testes locais;
- não acessa o OpenShift.

### 3. Autenticar no cluster fora do toolkit

O login é responsabilidade do operador e acontece fora do toolkit, conforme o procedimento seguro da sua organização. Não salve tokens, kubeconfigs completos ou credenciais no repositório.

```bash
oc whoami
oc whoami --show-server
oc config current-context
```

### 4. Validar localmente sem cluster

```bash
make check
```

O que faz:

- valida dependências obrigatórias;
- confirma que o ambiente local está pronto;
- não consulta a API OpenShift.

### 5. Validar contexto OpenShift

```bash
make check-cluster
```

O que faz:

- usa o contexto atual do `oc`;
- consulta API, usuário, versão, ClusterVersion e permissões;
- não troca contexto;
- não altera recursos.

### 6. Fazer coleta completa segura

```bash
scripts/coletar-cluster.sh
LATEST="$(ls -dt evidencias/*/* | head -1)"
(cd "$LATEST" && sha256sum -c checksums.sha256)
```

O que faz:

- coleta visão ampla do cluster;
- salva artefatos em `evidencias/`;
- registra comandos, exit codes, manifesto e checksums;
- não coleta YAML/logs completos de todos os pods por padrão.

### 7. Gerar relatório

```bash
scripts/gerar-relatorio.sh \
  --path "$LATEST" \
  --output relatorios/relatorio-diagnostico.md
```

O que faz:

- cria um relatório Markdown inicial;
- inclui manifesto sanitizado;
- aponta onde revisar evidências;
- não declara causa raiz sem análise humana.

### 8. Usar runbook quando houver sintoma

Escolha um arquivo em `runbooks/` de acordo com o sintoma.

Exemplos:

- `runbooks/pod-crashloopbackoff.md`;
- `runbooks/node-notready.md`;
- `runbooks/clusteroperator-degraded.md`;
- `runbooks/pvc-pending.md`.

O runbook orienta o que verificar, quais evidências procurar e quando escalar.

### 9. Fazer diagnóstico direcionado

Depois de identificar um alvo:

```bash
scripts/diagnosticar-pod.sh <namespace> <pod> --tail 100
scripts/diagnosticar-node.sh <node>
scripts/diagnosticar-namespace.sh <namespace>
scripts/diagnosticar-operator.sh authentication
```

O que faz:

- aprofunda em um recurso específico;
- coleta `describe`, eventos e logs limitados quando aplicável;
- gera nova pasta de evidência direcionada.

### 10. Usar prompts com Codex

Os arquivos em `prompts/` são instruções para Codex/IA.

Exemplo:

```text
Use o prompt prompts/diagnostico-cluster.md e analise as evidências em evidencias/crc-lab/<timestamp>.
Não execute remediação. Separe fatos, hipóteses e próximos passos.
```

Se o MCP estiver configurado:

```bash
scripts/configurar-codex-mcp.sh --yes --replace
codex
```

Depois, dentro do Codex:

```text
Continue a validação Codex + MCP usando o prompt prompts/continuar-validacao-mcp.md.
Tenho autorização para executar as fases até o preflight do must-gather.
```

### 11. Usar templates para registrar resultado

Os arquivos em `templates/` são modelos de documentação.

Use quando precisar formalizar:

- achado técnico;
- relatório executivo;
- relatório técnico;
- handover;
- timeline;
- plano de remediação;
- validação pós-mudança.

Exemplo:

```bash
cp templates/achado.md relatorios/achado-authentication-degraded.md
```

Depois preencha manualmente com base nas evidências.

### 12. Executar must-gather somente quando necessário

Use para coleta exaustiva ou suporte.

```bash
make must-gather-preflight
make must-gather
MUST_GATHER="$(ls -dt evidencias/*/*/must-gather | head -1)"
make analyze-must-gather RESOURCE="$MUST_GATHER"
```

O diretório bruto do must-gather é confidencial. Não publique `raw/` sem revisão.

## Status dos artefatos auxiliares

| Pasta | Estado | Como usar |
| --- | --- | --- |
| `prompts/` | Pronta como biblioteca de prompts base. `continuar-validacao-mcp.md` é o fluxo mais completo. Os demais são prompts iniciais por domínio. | Cole no Codex junto com o caminho das evidências ou use como instrução de análise. |
| `runbooks/` | Pronta como biblioteca de triagem. Os runbooks são guias humanos e podem ser especializados ao longo do uso real. | Escolha pelo sintoma e use para decidir quais evidências/diagnósticos coletar. |
| `templates/` | Pronta como biblioteca de modelos Markdown. | Copie para `relatorios/` e preencha com evidências. |

## Regra mental simples

```text
Scripts coletam.
Runbooks orientam.
Prompts ajudam a analisar.
Templates documentam.
Codex correlaciona, se você quiser.
O operador decide e aprova.
```
