from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
try:
    import yaml
except Exception:
    yaml = None
ROOT = Path(__file__).resolve().parents[1]
def project_root() -> Path: return ROOT
def load_yaml(path: str | Path, default: Any | None = None) -> Any:
    p=Path(path); p = p if p.is_absolute() else ROOT/p
    if not p.exists(): return {} if default is None else default
    text=p.read_text(encoding='utf-8')
    if yaml is None:
        result={}
        for line in text.splitlines():
            if line.strip() and not line.lstrip().startswith('#') and ':' in line:
                k,v=line.split(':',1); result[k.strip()]=v.strip() or {}
        return result
    return yaml.safe_load(text) or {}
@lru_cache(maxsize=16)
def defaults() -> dict[str, Any]: return load_yaml('config/defaults.yaml', {})
def load_inventory(path: str | Path | None = None) -> dict[str, Any]:
    return load_yaml(path or os.environ.get('OPENSHIFT_AIOPS_INVENTORY') or 'inventories/clusters.example.yaml', {'clusters': []})
def configured_clusters(path: str | Path | None = None) -> list[dict[str, Any]]:
    return [c for c in load_inventory(path).get('clusters', []) if c.get('enabled', True)]
def find_cluster(name: str, path: str | Path | None = None) -> dict[str, Any] | None:
    return next((c for c in configured_clusters(path) if c.get('name') == name), None)
def version() -> str:
    p=ROOT/'VERSION'; return p.read_text(encoding='utf-8').strip() if p.exists() else '0.0.0'
