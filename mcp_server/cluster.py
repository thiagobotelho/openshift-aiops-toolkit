from __future__ import annotations
from typing import Any
from .commands import run_oc

def identity(timeout: int = 60, context: str | None = None, kubeconfig: str | None = None) -> dict[str, Any]:
    checks={'context':['config','current-context'], 'user':['whoami'], 'server':['whoami','--show-server'], 'version':['version'], 'infrastructure':['get','infrastructure','cluster','-o','json'], 'clusterversion':['get','clusterversion','-o','json']}
    return {n: run_oc(a, timeout=timeout, context=context, kubeconfig=kubeconfig).to_dict() for n,a in checks.items()}
