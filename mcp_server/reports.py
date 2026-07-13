from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from .sanitizers import sanitize_text

CORE_COMMANDS = {"current-context", "whoami", "server", "version", "clusterversion", "clusteroperators"}

def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def _json_loads(value: str) -> dict[str, Any]:
    try:
        payload = json.loads(value)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}

def _load_result(evidence_dir: Path, relative_path: str | None) -> dict[str, Any]:
    if not relative_path:
        return {}
    path = evidence_dir / relative_path
    payload = _json_loads(_safe_read(path))
    payload["_evidence_path"] = relative_path
    return payload

def _file_index(manifest: dict[str, Any]) -> dict[str, str]:
    index: dict[str, str] = {}
    for item in manifest.get("files", []):
        if not isinstance(item, dict):
            continue
        relative = item.get("path")
        if isinstance(relative, str):
            index[Path(relative).stem] = relative
    return index

def _command_summary(result: dict[str, Any]) -> str:
    stdout = str(result.get("stdout") or "").strip()
    stderr = str(result.get("stderr") or "").strip()
    payload = _json_loads(stdout) if stdout.startswith(("{", "[")) else {}
    if payload:
        if isinstance(payload.get("items"), list):
            return f"JSON com {len(payload['items'])} item(ns)"
        keys = ", ".join(list(payload.keys())[:6])
        return f"JSON com campos: {keys}"
    text = stdout or stderr
    if not text:
        return "sem saída"
    first = text.splitlines()[0].strip()
    return first[:180]

def _finding(
    findings: list[dict[str, str]],
    *,
    severity: str,
    area: str,
    symptom: str,
    evidence: str,
    probable_cause: str,
    validate: str,
    resolve: str,
    confidence: str = "média",
) -> None:
    findings.append(
        {
            "severity": severity,
            "area": area,
            "symptom": sanitize_text(symptom),
            "evidence": sanitize_text(evidence),
            "probable_cause": sanitize_text(probable_cause),
            "validate": sanitize_text(validate),
            "resolve": sanitize_text(resolve),
            "confidence": confidence,
        }
    )

def _parse_json_stdout(result: dict[str, Any]) -> dict[str, Any]:
    return _json_loads(str(result.get("stdout") or ""))

def _condition_map(item: dict[str, Any]) -> dict[str, dict[str, Any]]:
    conditions = item.get("status", {}).get("conditions", [])
    if not isinstance(conditions, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for condition in conditions:
        if isinstance(condition, dict) and condition.get("type"):
            out[str(condition["type"])] = condition
    return out

def _data_lines(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    if lines[0].upper().startswith(("NAME ", "LAST SEEN", "NAMESPACE ")):
        lines = lines[1:]
    return [line for line in lines if "No resources found" not in line]

def _analyze_command_results(evidence_dir: Path, manifest: dict[str, Any], findings: list[dict[str, str]]) -> list[dict[str, Any]]:
    files = _file_index(manifest)
    rows: list[dict[str, Any]] = []
    for command in manifest.get("commands", []):
        if not isinstance(command, dict):
            continue
        name = str(command.get("name") or "sem-nome")
        result = _load_result(evidence_dir, files.get(name))
        exit_code = command.get("exit_code", result.get("exit_code"))
        evidence = result.get("_evidence_path") or files.get(name) or "manifest.json"
        rows.append({"name": name, "exit_code": exit_code, "summary": _command_summary(result), "evidence": evidence})
        if isinstance(exit_code, int) and exit_code != 0:
            severity = "critical" if name in CORE_COMMANDS else "warning"
            _finding(
                findings,
                severity=severity,
                area="execução",
                symptom=f"Comando `{name}` retornou exit code {exit_code}.",
                evidence=f"{evidence}: {_command_summary(result)}",
                probable_cause="Permissão insuficiente, recurso ausente, API indisponível ou comando incompatível com a versão/capacidade do cluster.",
                validate=f"Reexecutar a consulta `{name}` com o mesmo contexto e revisar stdout/stderr em `{evidence}`.",
                resolve="Corrigir autenticação/RBAC, validar existência do recurso ou ajustar a coleta para tratar recurso opcional como não aplicável.",
                confidence="alta",
            )
        if result.get("timed_out"):
            _finding(
                findings,
                severity="warning",
                area="execução",
                symptom=f"Comando `{name}` atingiu timeout.",
                evidence=str(evidence),
                probable_cause="API lenta, recurso com volume alto ou timeout configurado baixo para o estado atual do cluster.",
                validate=f"Repetir `{name}` com timeout maior e comparar duração.",
                resolve="Aumentar timeout ou coletar o domínio de forma direcionada.",
            )
        if result.get("truncated"):
            _finding(
                findings,
                severity="warning",
                area="evidência",
                symptom=f"Saída do comando `{name}` foi truncada.",
                evidence=str(evidence),
                probable_cause="Volume de saída maior que o limite seguro de captura.",
                validate=f"Abrir `{evidence}` e verificar marcador de truncamento.",
                resolve="Executar coleta direcionada para o namespace/recurso afetado.",
            )
    return rows

def _analyze_clusteroperators(result: dict[str, Any], findings: list[dict[str, str]]) -> None:
    payload = _parse_json_stdout(result)
    for item in payload.get("items", []) if isinstance(payload.get("items"), list) else []:
        if not isinstance(item, dict):
            continue
        name = item.get("metadata", {}).get("name", "desconhecido")
        conditions = _condition_map(item)
        degraded = conditions.get("Degraded", {})
        available = conditions.get("Available", {})
        progressing = conditions.get("Progressing", {})
        evidence = result.get("_evidence_path", "operators/clusteroperators.json")
        if degraded.get("status") == "True":
            message = degraded.get("message") or degraded.get("reason") or "Degraded=True"
            _finding(
                findings,
                severity="critical",
                area="operators",
                symptom=f"ClusterOperator `{name}` está Degraded=True.",
                evidence=f"{evidence}: {message}",
                probable_cause="Falha em componente gerenciado pelo operador; a causa específica normalmente aparece na mensagem da condição, eventos e pods relacionados.",
                validate=f"Consultar `oc describe clusteroperator {name}` e eventos/pods do namespace relacionado.",
                resolve="Corrigir a dependência indicada pela condição do operador e validar retorno para Available=True/Degraded=False.",
                confidence="alta",
            )
        if available.get("status") == "False":
            message = available.get("message") or available.get("reason") or "Available=False"
            _finding(
                findings,
                severity="critical",
                area="operators",
                symptom=f"ClusterOperator `{name}` está Available=False.",
                evidence=f"{evidence}: {message}",
                probable_cause="Componente essencial indisponível, rollout incompleto ou dependência não saudável.",
                validate=f"Consultar `oc get clusteroperator {name} -o yaml` e workloads do operador.",
                resolve="Restaurar a dependência indisponível e aguardar reconciliação do operador.",
                confidence="alta",
            )
        if progressing.get("status") == "True":
            message = progressing.get("message") or progressing.get("reason") or "Progressing=True"
            _finding(
                findings,
                severity="warning",
                area="operators",
                symptom=f"ClusterOperator `{name}` está Progressing=True.",
                evidence=f"{evidence}: {message}",
                probable_cause="Atualização, rollout, reconciliação pendente ou componente aguardando dependência.",
                validate=f"Verificar se `{name}` permanece Progressing em nova coleta.",
                resolve="Se persistente, investigar pods/eventos do operador e dependências citadas na mensagem.",
            )

def _analyze_clusterversion(result: dict[str, Any], findings: list[dict[str, str]]) -> None:
    payload = _parse_json_stdout(result)
    conditions = _condition_map(payload)
    evidence = result.get("_evidence_path", "cluster/clusterversion.json")
    for condition_name, severity in {"Failing": "critical", "Progressing": "warning"}.items():
        condition = conditions.get(condition_name, {})
        if condition.get("status") == "True":
            message = condition.get("message") or condition.get("reason") or f"{condition_name}=True"
            _finding(
                findings,
                severity=severity,
                area="cluster-version",
                symptom=f"ClusterVersion está {condition_name}=True.",
                evidence=f"{evidence}: {message}",
                probable_cause="Upgrade/reconciliação do cluster com falha ou em andamento.",
                validate="Consultar `oc get clusterversion -o yaml` e histórico de atualizações.",
                resolve="Tratar o componente indicado na condição antes de tentar nova atualização.",
                confidence="alta",
            )

def _analyze_text_domains(results: dict[str, dict[str, Any]], findings: list[dict[str, str]]) -> None:
    pods = results.get("pods-not-running", {})
    pod_lines = _data_lines(str(pods.get("stdout") or ""))
    if pod_lines:
        _finding(
            findings,
            severity="warning",
            area="workloads",
            symptom=f"{len(pod_lines)} linha(s) de pods fora de Running/Succeeded foram encontradas.",
            evidence=f"{pods.get('_evidence_path', 'workloads/pods-not-running.json')}: {' | '.join(pod_lines[:5])}",
            probable_cause="Pods em Pending, Failed, CrashLoopBackOff, ImagePullBackOff ou estado transitório.",
            validate="Investigar primeiro os pods listados com `describe`, eventos e logs atuais/anteriores.",
            resolve="Corrigir imagem, configuração, recursos, PVC, probe ou dependência externa conforme o pod afetado.",
        )
    events = results.get("warning-events", {})
    event_lines = _data_lines(str(events.get("stdout") or ""))
    if event_lines:
        _finding(
            findings,
            severity="warning",
            area="eventos",
            symptom=f"{len(event_lines)} evento(s) Warning foram coletados.",
            evidence=f"{events.get('_evidence_path', 'events/warning-events.json')}: {' | '.join(event_lines[:5])}",
            probable_cause="Eventos Warning podem indicar falhas recentes ou históricas; exigem correlação temporal com pods/operators.",
            validate="Separar eventos atuais de históricos e correlacionar `lastTimestamp`, namespace e objeto envolvido.",
            resolve="Atuar no recurso envolvido nos eventos recorrentes ou atuais.",
            confidence="média",
        )
    nodes = results.get("nodes-wide", {})
    not_ready = [line for line in _data_lines(str(nodes.get("stdout") or "")) if "NotReady" in line]
    if not_ready:
        _finding(
            findings,
            severity="critical",
            area="nodes",
            symptom=f"{len(not_ready)} node(s) NotReady encontrados.",
            evidence=f"{nodes.get('_evidence_path', 'nodes/nodes-wide.json')}: {' | '.join(not_ready[:5])}",
            probable_cause="Kubelet, rede do node, pressão de recursos, runtime ou problema da VM/host.",
            validate="Consultar `oc describe node <node>` e eventos do node.",
            resolve="Corrigir condição do node indicada em `describe`, liberar recursos ou reiniciar componente conforme política operacional.",
            confidence="alta",
        )
    pvcs = results.get("pvcs", {})
    pvc_problem = [line for line in _data_lines(str(pvcs.get("stdout") or "")) if any(term in line for term in ["Pending", "Lost"])]
    if pvc_problem:
        _finding(
            findings,
            severity="warning",
            area="storage",
            symptom=f"{len(pvc_problem)} PVC(s) Pending/Lost encontrados.",
            evidence=f"{pvcs.get('_evidence_path', 'storage/pvcs.json')}: {' | '.join(pvc_problem[:5])}",
            probable_cause="StorageClass ausente/incorreta, provisioner indisponível, capacidade insuficiente ou binding bloqueado.",
            validate="Consultar PVC, StorageClass, PV e eventos no namespace afetado.",
            resolve="Corrigir StorageClass/provisioner/capacidade ou recriar PVC conforme política de dados.",
        )

def analyze_evidence(evidence_dir: Path | None) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, Any]], list[str]]:
    if not evidence_dir:
        return {}, [], [], ["Diretório de evidências não informado."]
    manifest_path = evidence_dir / "manifest.json"
    if not manifest_path.exists():
        return {}, [], [], [f"Manifesto não encontrado em `{manifest_path}`."]
    manifest = _json_loads(_safe_read(manifest_path))
    findings: list[dict[str, str]] = []
    command_rows = _analyze_command_results(evidence_dir, manifest, findings)
    files = _file_index(manifest)
    results = {name: _load_result(evidence_dir, path) for name, path in files.items()}
    if "clusteroperators" in results:
        _analyze_clusteroperators(results["clusteroperators"], findings)
    if "clusterversion" in results:
        _analyze_clusterversion(results["clusterversion"], findings)
    _analyze_text_domains(results, findings)
    limitations = [
        "A análise automática não declara causa raiz definitiva sem correlação suficiente.",
        "Eventos Warning podem ser históricos; valide timestamp antes de concluir impacto atual.",
        "Secrets e credenciais não são exibidos no relatório.",
    ]
    return manifest, findings, command_rows, limitations

def _severity_rank(value: str) -> int:
    return {"critical": 0, "warning": 1, "informational": 2}.get(value, 3)

def _finding_id(index: int) -> str:
    return f"ACH-{index:03d}"

def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(sanitize_text(str(item)).replace("\n", " ") for item in row) + " |")
    return "\n".join(out)

def generate_base_report(evidence_dir: Path | None = None, title: str = 'Relatório de Diagnóstico OpenShift') -> str:
    now = datetime.now().isoformat(timespec='seconds')
    manifest, findings, command_rows, limitations = analyze_evidence(evidence_dir)
    manifest_text = 'Manifesto não informado.'
    if evidence_dir and (evidence_dir / 'manifest.json').exists():
        manifest_text = (evidence_dir / 'manifest.json').read_text(encoding='utf-8')
    manifest_text = sanitize_text(manifest_text)
    findings = sorted(findings, key=lambda item: (_severity_rank(item["severity"]), item["area"], item["symptom"]))
    critical = sum(1 for item in findings if item["severity"] == "critical")
    warning = sum(1 for item in findings if item["severity"] == "warning")
    status = "CRÍTICO" if critical else "ATENÇÃO" if warning else "SEM ACHADOS PRIORITÁRIOS"
    finding_rows = [
        [_finding_id(i), f["severity"], f["area"], f["symptom"], f["evidence"], f["confidence"]]
        for i, f in enumerate(findings, start=1)
    ]
    command_table = _markdown_table(
        ["Comando", "Exit", "Resumo", "Evidência"],
        [[row["name"], row.get("exit_code", ""), row.get("summary", ""), row.get("evidence", "")] for row in command_rows],
    ) if command_rows else "Nenhum comando registrado no manifesto."
    finding_table = _markdown_table(
        ["ID", "Severidade", "Área", "Sintoma", "Evidência", "Confiança"],
        finding_rows,
    ) if finding_rows else "Nenhum erro prioritário foi detectado automaticamente nas evidências disponíveis."
    details = []
    for i, finding in enumerate(findings, start=1):
        details.append(
            f"""### {_finding_id(i)} — {finding['area']} — {finding['severity']}

- Sintoma: {finding['symptom']}
- Evidência: `{finding['evidence']}`
- Causa provável: {finding['probable_cause']}
- Como validar: {finding['validate']}
- Como resolver: {finding['resolve']}
- Confiança: {finding['confidence']}
"""
        )
    details_text = "\n".join(details) if details else "Sem detalhamento adicional porque nenhum achado prioritário foi detectado automaticamente."
    limitations_text = "\n".join(f"- {item}" for item in limitations)
    cluster = manifest.get("cluster", "não informado") if manifest else "não informado"
    environment = manifest.get("environment", "não informado") if manifest else "não informado"
    context = manifest.get("context", "não informado") if manifest else "não informado"
    return f"""# {title}

## Identificação

- Data: {now}
- Escopo: diagnóstico assistivo somente leitura
- Evidências: {str(evidence_dir) if evidence_dir else 'não informado'}
- Cluster: {cluster}
- Ambiente lógico: {environment}
- Contexto: {context}

## Resumo executivo

- Status automático: **{status}**
- Achados críticos: {critical}
- Achados de atenção: {warning}
- Causa raiz definitiva: declarada somente quando as evidências sustentarem; caso contrário, o relatório informa causa provável e como validar.

## Como interpretar

Cada achado segue o padrão: sintoma observado, evidência, causa provável, validação recomendada, caminho de resolução e confiança. O relatório não aplica mudanças no cluster.

## Achados priorizados

{finding_table}

## Detalhamento dos achados

{details_text}

## Comandos e evidências analisadas

{command_table}

## Limitações e cuidados

{limitations_text}

## Manifesto sanitizado

```json
{manifest_text[:6000]}
```

## Recomendações

- Validar cada achado crítico ou de atenção com os comandos indicados.
- Priorizar erros atuais e recorrentes antes de eventos históricos.
- Aprovar remediações fora do toolkit.
- Executar validação pós-mudança e comparar coletas.
"""

def _load_manifest(path: Path) -> dict:
    p = path / 'manifest.json'
    if not p.exists():
        return {}
    return json.loads(sanitize_text(p.read_text(encoding='utf-8')))

def compare_evidence_dirs(old: Path, new: Path) -> str:
    a, b = _load_manifest(old), _load_manifest(new)
    return f"""# Comparação de Coletas

## Coleta antiga

- Caminho: `{old}`
- Cluster: {a.get('cluster', 'desconhecido')}
- Horário: {a.get('started_at', 'desconhecido')}

## Coleta nova

- Caminho: `{new}`
- Cluster: {b.get('cluster', 'desconhecido')}
- Horário: {b.get('started_at', 'desconhecido')}

## Diferenças iniciais

- Comandos antigos: {len(a.get('commands', []))}
- Comandos novos: {len(b.get('commands', []))}
- Arquivos antigos: {len(a.get('files', []))}
- Arquivos novos: {len(b.get('files', []))}

Revise novos sintomas, itens resolvidos, regressões e diferenças de versão/capacidade.
"""
