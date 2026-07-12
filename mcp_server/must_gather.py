from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config
from .commands import build_oc_command, command_prefix, run_oc
from .sanitizers import sanitize_text
from .validators import validate_k8s_name, validate_timeout

SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("authorization_header", re.compile(r"(?i)authorization:\s*(bearer|basic)\s+\S+"), "alta"),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"), "alta"),
    ("password", re.compile(r"(?i)\b(password|passwd|senha)\b\s*[:=]"), "alta"),
    ("client_secret", re.compile(r"(?i)\b(client_secret|clientSecret)\b\s*[:=]"), "alta"),
    ("access_token", re.compile(r"(?i)\b(access_token|refresh_token|id_token)\b\s*[:=]"), "alta"),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "critica"),
    ("cookie", re.compile(r"(?i)\bcookie:\s*"), "media"),
    ("credential_url", re.compile(r"https?://[^:/\s]+:[^@/\s]+@"), "alta"),
    ("base64_long", re.compile(r"\b[A-Za-z0-9+/]{120,}={0,2}\b"), "media"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_cluster(value: str | None) -> str:
    if not value:
        return "cluster-nao-informado"
    try:
        return validate_k8s_name(value, "cluster")
    except Exception:
        return "cluster-nao-informado"


def must_gather_base(cluster: str | None, output_dir: str | Path = "evidencias") -> Path:
    root = config.project_root()
    out = Path(output_dir)
    out = out if out.is_absolute() else root / out
    return out / safe_cluster(cluster) / timestamp() / "must-gather"


def prepare_directories(base: Path) -> dict[str, Path]:
    previous_umask = os.umask(0o077)
    os.umask(previous_umask)
    paths = {
        "base": base,
        "raw": base / "raw",
        "metadata": base / "metadata",
        "analysis": base / "analysis",
        "sanitized": base / "sanitized",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            raise ValueError(f"diretório não pode ser symlink: {path}")
    (base / "DO-NOT-COMMIT.txt").write_text(
        "CONFIDENCIAL — NÃO PUBLICAR\n"
        "Este diretório pode conter dados sensíveis de must-gather.\n"
        "Não versionar, não anexar em issues públicas e não fazer upload sem revisão.\n",
        encoding="utf-8",
    )
    return paths


def gitignore_covers_evidence() -> bool:
    gitignore = config.project_root() / ".gitignore"
    if not gitignore.exists():
        return False
    lines = {line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()}
    return "evidencias/**" in lines and "!evidencias/.gitkeep" in lines


def run_host_command(args: list[str], timeout: int = 30) -> dict[str, Any]:
    command = command_prefix() + args
    start = time.monotonic()
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": sanitize_text(completed.stdout),
            "stderr": sanitize_text(completed.stderr),
            "duration_seconds": round(time.monotonic() - start, 3),
        }
    except Exception as exc:
        return {
            "command": command,
            "exit_code": 127,
            "stdout": "",
            "stderr": sanitize_text(str(exc)),
            "duration_seconds": round(time.monotonic() - start, 3),
        }


def collect_preflight(
    cluster: str | None,
    timeout: int,
    output_dir: str | Path = "evidencias",
    base: Path | None = None,
    context: str | None = None,
    kubeconfig: str | None = None,
) -> dict[str, Any]:
    timeout = validate_timeout(timeout)
    base = base or must_gather_base(cluster, output_dir)
    usage = shutil.disk_usage(base.parent if base.parent.exists() else config.project_root())
    statvfs = os.statvfs(base.parent if base.parent.exists() else config.project_root())
    help_result = run_oc(["adm", "must-gather", "--help"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict()
    help_text = help_result.get("stdout", "")
    supports = {
        "dest_dir": "--dest-dir" in help_text,
        "all_images": "--all-images" in help_text,
        "volume_percentage": "--volume-percentage" in help_text,
        "timeout_flag": "--timeout" in help_text,
    }
    payload = {
        "started_at": utc_now(),
        "cluster": safe_cluster(cluster),
        "environment": os.environ.get("OPENSHIFT_AIOPS_ENVIRONMENT", "laboratory"),
        "destination": str(base),
        "gitignore_covers_evidence": gitignore_covers_evidence(),
        "disk": {"total": usage.total, "used": usage.used, "free": usage.free},
        "inodes": {"files": statvfs.f_files, "free": statvfs.f_ffree},
        "crc_status": run_host_command(["crc", "status"], timeout=min(timeout, 30)),
        "context": run_oc(["config", "current-context"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "user": run_oc(["whoami"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "server": run_oc(["whoami", "--show-server"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "version": run_oc(["version"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "infrastructure": run_oc(["get", "infrastructure", "cluster", "-o", "json"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "clusterversion": run_oc(["get", "clusterversion", "-o", "json"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "permissions": run_oc(["auth", "can-i", "--list"], timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict(),
        "must_gather_help": help_result,
        "supported_options": supports,
    }
    command = ["adm", "must-gather"]
    if supports["dest_dir"]:
        command.append(f"--dest-dir={base / 'raw'}")
    if supports["all_images"]:
        command.append("--all-images=false")
    payload["planned_oc_args"] = command
    payload["planned_command"] = build_oc_command(command, context=context, kubeconfig=kubeconfig)
    payload["finished_at"] = utc_now()
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def directory_stats(path: Path) -> dict[str, Any]:
    files = [p for p in path.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    return {"files": len(files), "size_bytes": size}


def write_checksums(base: Path) -> Path:
    checksum_path = base / "metadata" / "checksums.sha256"
    rows: list[str] = []
    for path in sorted(p for p in base.rglob("*") if p.is_file() and p != checksum_path):
        rows.append(f"{sha256_file(path)}  {path.relative_to(base)}")
    checksum_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return checksum_path


def execute_must_gather(*, cluster: str | None, output_dir: str | Path, timeout: int, context: str | None = None, kubeconfig: str | None = None) -> Path:
    timeout = validate_timeout(timeout)
    base = must_gather_base(cluster, output_dir)
    paths = prepare_directories(base)
    preflight = collect_preflight(cluster, timeout, output_dir, base=base, context=context, kubeconfig=kubeconfig)
    command_args = list(preflight["planned_oc_args"])
    if not any(arg.startswith("--dest-dir") for arg in command_args):
        raise RuntimeError("oc adm must-gather local não informou suporte a --dest-dir; execução bloqueada")
    command = build_oc_command(command_args, context=context, kubeconfig=kubeconfig)
    started = time.monotonic()
    started_at = utc_now()
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    duration = time.monotonic() - started
    (paths["metadata"] / "stdout.log").write_text(completed.stdout, encoding="utf-8", errors="replace")
    (paths["metadata"] / "stderr.log").write_text(completed.stderr, encoding="utf-8", errors="replace")
    residual = run_oc(["get", "pods", "-A", "-o", "wide"], timeout=min(timeout, 60), context=context, kubeconfig=kubeconfig).to_dict()
    write_json(paths["metadata"] / "residual-pods.json", residual)
    manifest = {
        "type": "must-gather",
        "classification": "CONFIDENCIAL — NÃO PUBLICAR",
        "cluster": safe_cluster(cluster),
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(duration, 3),
        "command": command,
        "exit_code": completed.returncode,
        "timed_out": False,
        "preflight": preflight,
        "raw": directory_stats(paths["raw"]),
        "metadata": directory_stats(paths["metadata"]),
        "gitignore_covers_evidence": gitignore_covers_evidence(),
    }
    write_json(paths["metadata"] / "manifest.json", manifest)
    write_checksums(base)
    if completed.returncode != 0:
        raise RuntimeError(f"oc adm must-gather falhou com exit_code={completed.returncode}; ver metadata/stderr.log")
    return base


def scan_sensitive(path: Path, *, max_file_bytes: int = 5 * 1024 * 1024, max_files: int = 20000) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scanned = 0
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        if scanned >= max_files:
            break
        try:
            if file_path.stat().st_size > max_file_bytes:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for finding_type, pattern, severity in SENSITIVE_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "type": finding_type,
                            "file": str(file_path.relative_to(path)),
                            "line": lineno,
                            "severity": severity,
                            "status": "revisar antes de compartilhar",
                        }
                    )
                    break
    return findings


def build_technical_index(path: Path) -> dict[str, Any]:
    domains = {
        "clusterversion": ["clusterversion", "cluster-version"],
        "clusteroperators": ["clusteroperator", "clusteroperators"],
        "nodes": ["/nodes/", "node.yaml", "nodes.json"],
        "events": ["events"],
        "pods": ["pods"],
        "storage": ["persistentvolume", "persistentvolumeclaim", "storageclass", "volumeattachment"],
        "network": ["network", "routes", "services", "endpoints"],
        "monitoring": ["monitoring", "prometheus", "alertmanager"],
        "olm": ["clusterserviceversion", "subscription", "installplan", "catalogsource"],
        "certificates": ["csr", "certificatesigningrequest", "certificate"],
    }
    files = [p for p in path.rglob("*") if p.is_file()]
    result: dict[str, Any] = {"root": str(path), "files": len(files), "domains": {}}
    lower_paths = [str(p.relative_to(path)).lower() for p in files]
    for domain, needles in domains.items():
        matches = [p for p in lower_paths if any(needle in p for needle in needles)]
        result["domains"][domain] = {
            "status": "potencialmente relevante" if matches else "indisponível",
            "examples": matches[:20],
            "count": len(matches),
        }
    return result


def analyze_must_gather(path: Path) -> Path:
    base = path
    raw = base / "raw"
    analysis = base / "analysis"
    sanitized = base / "sanitized"
    analysis.mkdir(parents=True, exist_ok=True, mode=0o700)
    sanitized.mkdir(parents=True, exist_ok=True, mode=0o700)
    findings = scan_sensitive(raw)
    index = build_technical_index(raw)
    write_json(analysis / "security-findings.json", {"findings": findings, "count": len(findings)})
    write_json(analysis / "technical-index.json", index)
    report = [
        "# Análise do must-gather",
        "",
        "## Identificação",
        f"- Diretório: `{base}`",
        "- Classificação: CONFIDENCIAL — NÃO PUBLICAR",
        "",
        "## Integridade da coleta",
        f"- Arquivos brutos indexados: {index['files']}",
        f"- Achados potenciais de sensibilidade: {len(findings)}",
        "",
        "## Limitações",
        "- A análise é offline e conservadora.",
        "- Dados brutos não foram modificados.",
        "- Achados de sensibilidade são indicadores, não garantia absoluta.",
        "",
        "## Domínios indexados",
    ]
    for domain, item in index["domains"].items():
        report.append(f"- {domain}: {item['status']} ({item['count']} arquivos relacionados)")
    report.extend(
        [
            "",
            "## Conclusão",
            "Must-gather preservado localmente. Revisar achados de sensibilidade antes de qualquer compartilhamento.",
        ]
    )
    output = analysis / "analise-must-gather.md"
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    return output
