# Arquitetura

Arquitetura: operador, Codex opcional, MCP, validação, allowlist, OpenShift API, evidências, sanitização e relatórios.

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

## Diagramas de referência

### 1. Arquitetura geral

```mermaid
flowchart LR
  Operador --> Codex[Codex opcional]
  Operador --> Scripts[Scripts Bash]
  Codex --> MCP[MCP openshift-readonly]
  Scripts --> Python[Python toolkit]
  MCP --> Python
  Python --> API[OpenShift API]
  API --> Evidencias[Evidências]
  Evidencias --> Relatorios[Relatórios]
```

### 2. Codex, MCP e OpenShift

```mermaid
sequenceDiagram
  participant U as Operador
  participant C as Codex
  participant M as MCP readonly
  participant O as OpenShift API
  U->>C: pergunta operacional
  C->>M: chama ferramenta específica
  M->>O: comando permitido
  O-->>M: saída
  M-->>C: saída sanitizada
  C-->>U: análise com evidência
```

### 3. Seleção de cluster

```mermaid
flowchart TD
  Inventario[Inventário YAML] --> Selecao[Cluster informado]
  Selecao --> Contexto[Contexto esperado]
  Contexto --> Atual[Contexto atual]
  Atual -->|compatível| Coleta[Coleta]
  Atual -->|divergente| Bloqueio[Interromper e orientar]
```

### 4. Fluxo de diagnóstico

```mermaid
flowchart LR
  Detectar --> Registrar --> Precheck --> ColetaInicial --> Triagem --> EvidenciaDirecionada --> Hipoteses --> Validacao --> Relatorio
```

### 5. Fluxo de evidências

```mermaid
flowchart TD
  Comando[Comando read-only] --> Saida[Saída bruta]
  Saida --> Sanitizacao[Sanitização]
  Sanitizacao --> Arquivo[Arquivo em evidências]
  Arquivo --> Manifesto[manifest.json]
  Arquivo --> Hash[checksums.sha256]
```

### 6. Fluxo de sanitização

```mermaid
flowchart LR
  Texto --> Regex[Regras de redaction]
  JSON --> Objeto[Sanitização de chaves sensíveis]
  Regex --> Redacted[[REDACTED]]
  Objeto --> Redacted
  Redacted --> Relatorio
```

### 7. Fronteira de segurança

```mermaid
flowchart LR
  Entrada[Parâmetros] --> Validacao[Validação]
  Validacao --> Allowlist[Allowlist]
  Allowlist --> ReadOnly[Somente leitura]
  ReadOnly --> API[API OpenShift]
  Entrada -.bloqueio.-> Denylist[Denylist]
```

### 8. Processo de incidente

```mermaid
flowchart TD
  Incidente --> Contexto --> Evidencias --> Achados --> Plano
  Plano --> Aprovacao[Aprovação humana]
  Aprovacao --> ExecucaoExterna[Execução fora do toolkit]
  ExecucaoExterna --> PosMudanca[Validação pós-mudança]
  PosMudanca --> Encerramento
```

### 9. Comparação de coletas

```mermaid
flowchart LR
  ColetaA[Coleta anterior] --> Comparador
  ColetaB[Coleta atual] --> Comparador
  Comparador --> Novos[Novos sintomas]
  Comparador --> Resolvidos[Itens resolvidos]
  Comparador --> Persistentes[Persistentes]
  Comparador --> Regressoes[Regressões]
```

### 10. Operação em produção

```mermaid
flowchart TD
  Producao[Ambiente production] --> Identidade[Exibir cluster/API/usuário/versão]
  Identidade --> Confirmacao[Confirmação explícita]
  Confirmacao -->|ok| ColetaReadOnly[Coleta somente leitura]
  Confirmacao -->|falha| Interromper[Interromper]
  ColetaReadOnly --> Auditoria[Auditoria local]
```
