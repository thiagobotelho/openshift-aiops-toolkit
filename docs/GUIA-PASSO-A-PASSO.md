# Guia passo a passo — OpenShift AIOps Toolkit

Este guia mostra o fluxo completo para instalar, validar, operar, coletar evidências, usar MCP/Codex e executar must-gather controlado com o `openshift-aiops-toolkit`.

O toolkit é assistivo e somente leitura por padrão. Ele não executa remediação automática e não deve ser usado para alterar recursos do cluster.

## 1. Pré-requisitos

Ferramentas obrigatórias:

- Bash;
- Python 3.10 ou superior;
- `tar`;
- `gzip`;
- `sha256sum`.

Ferramentas recomendadas:

- `oc`;
- `jq`;
- Codex CLI;
- CRC/OpenShift Local, quando o ambiente for laboratório local.

Ferramentas opcionais:

- `yq`;
- Podman;
- GitHub CLI.

Valide o básico:

```bash
bash --version
python3 --version
python3 -m pip --version
```

## 2. Clonar o repositório

```bash
git clone https://github.com/thiagobotelho/openshift-aiops-toolkit.git
cd openshift-aiops-toolkit
```

Se você já possui o repositório local:

```bash
cd openshift-aiops-toolkit
git status --short
```

## 3. Instalar dependências Python

```bash
scripts/install.sh
```

O script:

- cria `.venv`;
- instala dependências Python declaradas;
- não usa `sudo`;
- não instala pacotes do sistema;
- não acessa o cluster.

Ative o ambiente, se quiser executar comandos Python diretamente:

```bash
source .venv/bin/activate
```

## 4. Configurar variáveis locais

Crie o `.env`:

```bash
cp .env.example .env
```

Edite apenas valores locais. Não coloque tokens, senhas ou kubeconfig completo no repositório.

No modo simples, nenhuma variável é obrigatória. O toolkit usa o contexto atual do `oc` e detecta um nome lógico para salvar as evidências.

Parâmetros como `OPENSHIFT_AIOPS_ENVIRONMENT` e `OPENSHIFT_AIOPS_CLUSTER` são metadados opcionais para inventário, auditoria ou automações corporativas. Eles não são pré-requisito para diagnosticar o cluster atual.

Se precisar consultar outro contexto sem alterar o kubeconfig persistente, prefira:

```bash
./openshift-aiops health --context outro-contexto
./openshift-aiops health --kubeconfig /caminho/kubeconfig
```

Quando o toolkit roda em ambiente isolado e o `oc` está disponível no host, configure:

```bash
export OPENSHIFT_AIOPS_COMMAND_PREFIX="flatpak-spawn --host"
export OPENSHIFT_AIOPS_OC_BIN="$HOME/.crc/cache/<versao-do-crc>/oc"
```

Use o caminho real do `oc` existente no seu ambiente.

## 5. Validar localmente sem acessar o cluster

```bash
make check
```

Esse comando roda em modo offline e não consulta a API OpenShift.

Valide a suíte:

```bash
python3 -m compileall -q mcp_server
tests/run.sh
bash tests/test_scripts.sh
```

## 6. Validar contexto OpenShift

Antes de qualquer coleta, confirme que você está no cluster correto:

```bash
oc config current-context
oc whoami
oc whoami --show-server
oc version
```

Para CRC/OpenShift Local, o servidor esperado normalmente é:

```text
https://api.crc.testing:6443
```

Depois rode:

```bash
make check-cluster
./openshift-aiops health
```

Esse comando é consultivo.

Por padrão, a saída é resumida para leitura humana. Quando precisar do JSON completo para automação ou debug:

```bash
scripts/preflight.sh --json
```

## 7. Coleta completa segura de evidências

Quando a intenção é fazer uma coleta completa do estado do cluster pelo toolkit, use este fluxo.

Neste projeto, "coleta completa segura" significa coletar uma visão ampla e reproduzível do cluster sem sair capturando YAML detalhado e logs de todos os pods. Essa escolha é proposital: logs e objetos completos de todos os workloads podem gerar muito volume e podem carregar dados sensíveis.

Para uma coleta exaustiva no padrão de suporte OpenShift, use o fluxo controlado de `must-gather` da seção 13.

### 7.1 Executar a coleta principal

Essa é a primeira coleta recomendada. Ela consulta o cluster de forma ampla e registra:

- identidade, API e versão do cluster;
- ClusterOperators;
- nodes;
- pods que não estão em `Running`;
- eventos `Warning`;
- PVCs e StorageClasses;
- routes e services;
- regras de monitoring.

```bash
scripts/coletar-cluster.sh \
  --output-dir evidencias \
  --timeout 60
```

Guarde o diretório gerado em uma variável para os próximos passos:

```bash
LATEST="$(ls -dt evidencias/*/* | head -1)"
echo "$LATEST"
```

Saída esperada:

```text
evidencias/<cluster>/<timestamp>/
```

O diretório contém:

- comandos executados;
- arquivos de evidência;
- `manifest.json`;
- `checksums.sha256`.

### 7.2 Validar integridade da coleta

```bash
(cd "$LATEST" && sha256sum -c checksums.sha256)
```

Se algum checksum falhar, descarte a coleta e execute novamente.

### 7.3 Gerar relatório da coleta

```bash
scripts/gerar-relatorio.sh \
  --path "$LATEST" \
  --output relatorios/relatorio-diagnostico.md
```

O relatório é um ponto de partida para análise. Ele referencia os artefatos coletados, mas não substitui a leitura dos arquivos de evidência quando houver incidente.

## 8. Diagnósticos direcionados

Use estes comandos somente depois da coleta completa segura, quando você já sabe qual recurso precisa de drilldown.

Eles coletam mais detalhes de um alvo específico, como `describe`, eventos relacionados e logs limitados quando aplicável.

Para descobrir os alvos:

```bash
oc get clusteroperators
oc get nodes
oc get namespaces
oc get pods -A
```

Operador específico:

```bash
scripts/diagnosticar-operator.sh authentication \
  --timeout 60
```

Node específico:

```bash
scripts/diagnosticar-node.sh <node> \
  --timeout 60
```

Namespace específico:

```bash
scripts/diagnosticar-namespace.sh <namespace> \
  --timeout 60
```

Pod com logs limitados:

```bash
scripts/diagnosticar-pod.sh <namespace> <pod> \
  --tail 100
```

Não use os comandos `diagnosticar-*` como substitutos da coleta completa. Eles são ferramentas de aprofundamento em um alvo conhecido.

Exemplos de quando usar:

- ClusterOperator `authentication` está `Degraded`;
- node `crc` está com pressão de memória, disco ou PID;
- namespace específico tem eventos `Warning`;
- pod específico está em `CrashLoopBackOff`, `ImagePullBackOff` ou reiniciando muito.

Não existe um `diagnosticar tudo profundamente` por padrão. Para uma coleta realmente exaustiva, use o fluxo controlado de must-gather descrito mais abaixo.

Domínios prontos para aprofundamento opcional:

```bash
scripts/diagnosticar-storage.sh
scripts/diagnosticar-network.sh
scripts/diagnosticar-ingress.sh
scripts/diagnosticar-dns.sh
scripts/diagnosticar-olm.sh
scripts/diagnosticar-monitoring.sh
scripts/verificar-capacidade.sh
```

Rode esses comandos quando a coleta completa segura indicar suspeita naquele domínio ou quando você quiser complementar a análise com um recorte específico.

## 9. Gerar relatório base

Se você seguiu a seção 7, o relatório já foi gerado usando a variável `LATEST`.

Para gerar novamente manualmente:

```bash
scripts/gerar-relatorio.sh \
  --path evidencias/<cluster>/<timestamp> \
  --output relatorios/relatorio-diagnostico.md
```

Os relatórios operacionais ficam em `relatorios/`, que é ignorado pelo Git por padrão.

## 10. Configurar MCP para Codex

Execute:

```bash
scripts/configurar-codex-mcp.sh
```

Para automação consciente:

```bash
scripts/configurar-codex-mcp.sh --yes --replace
```

Verifique:

```bash
codex mcp list
codex mcp get openshift-readonly
```

O servidor esperado:

```text
openshift-readonly
transport: stdio
enabled: true
```

Importante: se a sessão Codex já estava aberta antes da configuração, abra uma nova sessão para carregar o MCP.

## 11. Validar MCP via STDIO

Execute a suíte:

```bash
tests/run.sh
```

Ela valida:

- inicialização do servidor MCP;
- `tools/list`;
- schemas específicos;
- parâmetros opcionais de compatibilidade sem exigir ambiente;
- proteção específica de must-gather;
- ausência de ferramenta genérica de shell.

## 12. Fluxo com Codex + MCP

Abra uma sessão Codex na raiz do repositório:

```bash
cd openshift-aiops-toolkit
codex
```

Use o prompt:

```text
Continue a validação Codex + MCP usando o prompt prompts/continuar-validacao-mcp.md.
Tenho autorização para executar as fases até o preflight do must-gather.
```

Se o MCP não aparecer como ferramenta nativa da sessão, valide via STDIO e registre a limitação.

## 13. Must-gather controlado

Use must-gather apenas quando necessário. Ele pode coletar dados sensíveis.

### 13.1 Preflight

```bash
make must-gather-preflight
```

O preflight valida:

- contexto;
- usuário;
- API;
- versão;
- `oc adm must-gather --help`;
- flags suportadas;
- destino;
- espaço disponível;
- `.gitignore`.

### 13.2 Execução

Execute somente após confirmar que o cluster é o correto:

```bash
make must-gather
```

O toolkit usa:

- `umask 077`;
- diretório timestampado;
- `raw/` preservado;
- `metadata/`;
- `analysis/`;
- `sanitized/`;
- manifesto;
- checksums;
- marcador `DO-NOT-COMMIT.txt`.

Destino:

```text
evidencias/<cluster>/<timestamp>/must-gather/
```

### 13.3 Validar integridade

```bash
cd evidencias/<cluster>/<timestamp>/must-gather
sha256sum -c metadata/checksums.sha256
```

### 13.4 Analisar offline

```bash
make analyze-must-gather RESOURCE=evidencias/<cluster>/<timestamp>/must-gather
```

Saídas:

```text
analysis/security-findings.json
analysis/technical-index.json
analysis/analise-must-gather.md
```

Nunca publique o diretório `raw/` sem revisão.

## 14. Empacotar evidências sanitizadas

Para evidências comuns:

```bash
scripts/sanitizar-evidencias.sh --path evidencias/<cluster>/<timestamp>
scripts/empacotar-evidencias.sh --path evidencias/<cluster>/<timestamp>
```

Não use isso como garantia absoluta para must-gather bruto. Must-gather precisa de revisão manual antes de compartilhamento.

## 15. Uso em clusters críticos

Diagnósticos consultivos usam o contexto atual do `oc` e não exigem `--environment production`. Antes de operar em cluster crítico, confirme contexto, API, usuário e política interna.

Exemplo:

```bash
oc config current-context
oc whoami
oc whoami --show-server
./openshift-aiops health
```

Regras:

- não executar remediações;
- não alterar RBAC;
- não aplicar manifestos;
- não acessar Secrets;
- não executar must-gather sem autorização formal;
- guardar evidências conforme política interna.

## 16. Validações finais antes de commit

```bash
python3 -m compileall -q mcp_server
tests/run.sh
bash tests/test_scripts.sh
make check
git diff --check
git status --short --ignored
```

Confirme que não há artefatos versionados:

```bash
git status --short --ignored evidencias relatorios
```

`evidencias/**` e `relatorios/**` devem aparecer como ignorados, não staged.

## 17. Troubleshooting rápido

`oc` não encontrado:

```bash
export OPENSHIFT_AIOPS_OC_BIN=/caminho/para/oc
```

Ambiente isolado/Flatpak:

```bash
export OPENSHIFT_AIOPS_COMMAND_PREFIX="flatpak-spawn --host"
```

MCP não aparece no Codex:

```bash
codex mcp list
codex mcp get openshift-readonly
```

Depois reinicie a sessão Codex na raiz do repositório.

Must-gather grande ou sensível:

- mantenha em `evidencias/**`;
- não publique;
- revise `analysis/security-findings.json`;
- compartilhe apenas derivados revisados.

## 18. Sequência resumida para CRC

```bash
cd openshift-aiops-toolkit
scripts/install.sh
make check
make check-cluster
scripts/coletar-cluster.sh
LATEST="$(ls -dt evidencias/*/* | head -1)"
(cd "$LATEST" && sha256sum -c checksums.sha256)
scripts/gerar-relatorio.sh --path "$LATEST" --output relatorios/relatorio-diagnostico.md
scripts/configurar-codex-mcp.sh --yes --replace
make must-gather-preflight
make must-gather
MUST_GATHER="$(ls -dt evidencias/*/*/must-gather | head -1)"
make analyze-must-gather RESOURCE="$MUST_GATHER"
```
