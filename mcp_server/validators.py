from __future__ import annotations
import os, re
from pathlib import Path
K8S_NAME_RE = re.compile(r"^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$")
K8S_NAMESPACE_RE = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
CONTEXT_RE = re.compile(r"^[A-Za-z0-9_.:@/-]{1,253}$")
DANGEROUS_RE = re.compile(r"[;|&<>`$(){}\[\]\\\r\n\t\x00]")
ALLOWED_ENVIRONMENTS = {"current", "development", "homologation", "production", "laboratory"}
ALLOWED_WORKLOAD_KINDS = {"deployment", "deploymentconfig", "statefulset", "daemonset", "job", "cronjob", "replicaset"}
class ValidationError(ValueError): pass
def ensure_no_dangerous(value: str, field: str = "value") -> str:
    if value is None: raise ValidationError(f"{field} é obrigatório")
    if DANGEROUS_RE.search(value): raise ValidationError(f"{field} contém caracteres não permitidos")
    if len(value) > 253: raise ValidationError(f"{field} excede 253 caracteres")
    return value
def validate_k8s_name(value: str, field: str = "name") -> str:
    value = ensure_no_dangerous(value, field)
    if value.startswith("-") or not K8S_NAME_RE.match(value): raise ValidationError(f"{field} inválido")
    return value
def validate_namespace(value: str) -> str:
    value = ensure_no_dangerous(value, "namespace")
    if value.startswith("-") or not K8S_NAMESPACE_RE.match(value): raise ValidationError("namespace inválido")
    return value
def validate_context(value: str) -> str:
    value = ensure_no_dangerous(value, "context")
    if not CONTEXT_RE.match(value): raise ValidationError("contexto inválido")
    return value
def validate_cluster(value: str) -> str: return validate_k8s_name(value, "cluster")
def validate_environment(value: str) -> str:
    if value not in ALLOWED_ENVIRONMENTS: raise ValidationError(f"ambiente inválido: {value}")
    return value
def validate_workload_kind(value: str) -> str:
    v = ensure_no_dangerous(value.lower(), "kind")
    if v not in ALLOWED_WORKLOAD_KINDS: raise ValidationError(f"kind de workload não suportado: {value}")
    return v
def validate_tail(value: int | str, minimum: int = 1, maximum: int = 5000) -> int:
    try: n=int(value)
    except Exception as exc: raise ValidationError("tail deve ser numérico") from exc
    if n < minimum or n > maximum: raise ValidationError(f"tail deve estar entre {minimum} e {maximum}")
    return n
def validate_timeout(value: int | str, minimum: int = 1, maximum: int = 900) -> int:
    try: n=int(value)
    except Exception as exc: raise ValidationError("timeout deve ser numérico") from exc
    if n < minimum or n > maximum: raise ValidationError(f"timeout deve estar entre {minimum} e {maximum}")
    return n
def validate_local_path(value: str, base_dir: str | Path | None = None) -> Path:
    ensure_no_dangerous(value, "path")
    raw = Path(os.path.expanduser(value))
    if ".." in raw.parts: raise ValidationError("path traversal não permitido")
    if base_dir is not None:
        base = Path(base_dir).resolve()
        resolved = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
        if base not in [resolved, *resolved.parents]: raise ValidationError("path fora do diretório permitido")
        return resolved
    resolved = raw.resolve()
    return resolved
