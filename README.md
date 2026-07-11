# OpenShift AIOps Toolkit

Plataforma profissional, local e somente leitura para diagnóstico, coleta de evidências, análise operacional e assistência por IA em Red Hat OpenShift Container Platform.

## Objetivo e público-alvo

Atender equipes de Operações, Infraestrutura, DevOps, SRE, Plataforma, Segurança e sustentação OpenShift em clusters de desenvolvimento, homologação, produção, cloud, on-premises, compactos, SNO, gerenciados e CRC/laboratório.

## Benefícios

- Diagnóstico padronizado e reproduzível.
- Multi-cluster com contexto explícito.
- Evidências sanitizadas e empacotáveis.
- Relatórios técnicos e executivos em Markdown.
- MCP `openshift-readonly` para Codex, sem terminal genérico.

## Arquitetura

```mermaid
flowchart LR
  Operador --> Codex[Codex opcional]
  Operador --> Scripts[Scripts Bash]
  Codex --> MCP[MCP openshift-readonly]
  Scripts --> Python[Python toolkit]
  MCP --> Python
  Python --> Contexto[Validação de contexto]
  Contexto --> Allowlist[Allowlist read-only]
  Allowlist --> API[OpenShift API]
  API --> Evidencias[Evidências]
  Evidencias --> Sanitizacao[Sanitização]
  Sanitizacao --> Relatorios[Relatórios]
```

## Pré-requisitos

Bash, Python 3.10+, `oc`, `jq`, `tar`, `gzip` e `sha256sum`. Opcionais: Codex CLI, `yq`, Podman e CRC.

## Instalação

```bash
git clone https://github.com/<org-ou-usuario>/openshift-aiops-toolkit.git
cd openshift-aiops-toolkit
scripts/install.sh
```

## Configuração e inventário

```bash
cp .env.example .env
cp inventories/clusters.example.yaml inventories/clusters.yaml
```

Nunca armazene tokens no inventário. Use kubeconfig já autenticado com permissão somente leitura.

## Uso em cluster único

```bash
scripts/preflight.sh --environment development
scripts/validar-contexto.sh
scripts/coletar-cluster.sh --cluster cluster-dev --environment development
scripts/gerar-relatorio.sh --path evidencias/cluster-dev/<coleta>
```

## Uso em múltiplos clusters

```bash
scripts/listar-clusters.sh
scripts/coletar-cluster.sh --cluster cluster-hml --context hml-context --environment homologation
```

O toolkit não troca contexto silenciosamente.

## Produção

Em produção, confirme explicitamente cluster, API, usuário, versão e infraestrutura. O toolkit é assistivo; remediações seguem gestão de mudança externa.

## Codex e MCP

```bash
scripts/configurar-codex-mcp.sh
codex mcp list
```

Configuração manual: `.codex/config.toml.example`.

## Scripts principais

- `preflight.sh`: valida dependências, contexto, API e permissões.
- `coletar-cluster.sh`: coleta evidências gerais.
- `diagnosticar-pod.sh`, `diagnosticar-operator.sh`, `diagnosticar-node.sh`: investigação direcionada.
- `gerar-relatorio.sh`: cria relatório Markdown.
- `sanitizar-evidencias.sh` e `empacotar-evidencias.sh`: preparo para compartilhamento.

## Evidências

```text
evidencias/<cluster>/<YYYYMMDD-HHMMSS>/
  metadata/ cluster/ operators/ nodes/ namespaces/ workloads/
  storage/ network/ monitoring/ events/ logs/
  manifest.json
  checksums.sha256
```

## Segurança e RBAC

Não coleta conteúdo de Secrets, não altera recursos, bloqueia verbos de escrita, sanitiza credenciais e não expõe terminal genérico no MCP. Exemplo documental: `docs/examples/rbac-readonly-example.yaml`.

## Must-gather

`coletar-must-gather.sh` exige confirmação humana, pode gerar pacote grande e potencialmente sensível, calcula SHA256 e não faz upload.

## Limitações

Permissões insuficientes reduzem evidências. Métricas dependem da API de métricas. Causa raiz só deve ser declarada com evidência suficiente.

## Troubleshooting

```bash
scripts/preflight.sh --verbose
python3 -m compileall mcp_server
tests/run.sh
```

## Roadmap

Mais correlações, perfis de coleta por domínio e exportadores de relatório.

## Referências oficiais

- Red Hat OpenShift Documentation: https://docs.redhat.com/en/documentation/openshift_container_platform
- OpenShift CLI: https://docs.redhat.com/en/documentation/openshift_container_platform/latest/html/cli_tools/openshift-cli-oc
- Model Context Protocol: https://modelcontextprotocol.io/
```
