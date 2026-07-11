from __future__ import annotations
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from . import config
from .commands import run_oc, write_json
from .models import EvidenceFile, EvidenceManifest
from .sanitizers import sanitize_text
from .validators import validate_k8s_name, validate_namespace, validate_tail, validate_workload_kind

def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d-%H%M%S')

def _hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def _safe_cluster_name(cluster: str) -> str:
    try:
        return validate_k8s_name(cluster, 'cluster')
    except Exception:
        return 'cluster-nao-informado'

def create_evidence_dir(cluster: str, output_dir: Path) -> Path:
    directory = config.project_root() / output_dir if not output_dir.is_absolute() else output_dir
    target = directory / _safe_cluster_name(cluster) / _timestamp()
    for child in ['metadata','cluster','operators','nodes','namespaces','workloads','storage','network','monitoring','events','logs']:
        (target / child).mkdir(parents=True, exist_ok=True)
    return target

def _record_command(base: Path, manifest: EvidenceManifest, group: str, name: str, args: list[str], **kwargs: Any) -> None:
    result = run_oc(args, **kwargs)
    file_path = base / group / f'{name}.json'
    write_json(file_path, result.to_dict())
    manifest.commands.append({'name': name, 'command': result.command, 'exit_code': result.exit_code})
    manifest.files.append(EvidenceFile(str(file_path.relative_to(base)), _hash(file_path), file_path.stat().st_size))

def collect_cluster_evidence(*, cluster: str, environment: str, context: str | None = None, kubeconfig: str | None = None, output_dir: Path = Path('evidencias'), timeout: int = 60) -> Path:
    base = create_evidence_dir(cluster, output_dir)
    manifest = EvidenceManifest(cluster=cluster, environment=environment, context=context or 'current')
    command_sets = [
        ('metadata','current-context',['config','current-context']),
        ('metadata','whoami',['whoami']),
        ('metadata','server',['whoami','--show-server']),
        ('metadata','version',['version']),
        ('cluster','infrastructure',['get','infrastructure','cluster','-o','json']),
        ('cluster','clusterversion',['get','clusterversion','-o','json']),
        ('operators','clusteroperators',['get','clusteroperators','-o','json']),
        ('nodes','nodes-wide',['get','nodes','-o','wide']),
        ('workloads','pods-not-running',['get','pods','-A','--field-selector=status.phase!=Running','-o','wide']),
        ('events','warning-events',['get','events','-A','--field-selector=type=Warning','--sort-by=.lastTimestamp']),
        ('storage','pvcs',['get','pvc','-A','-o','wide']),
        ('storage','storageclasses',['get','storageclass','-o','wide']),
        ('network','routes',['get','routes','-A','-o','wide']),
        ('network','services',['get','services','-A','-o','wide']),
        ('monitoring','alerts',['get','prometheusrules','-A','-o','wide']),
    ]
    for group, name, args in command_sets:
        _record_command(base, manifest, group, name, args, timeout=timeout, context=context, kubeconfig=kubeconfig)
    manifest.finish()
    manifest_path = base / 'manifest.json'
    write_json(manifest_path, manifest.to_dict())
    checksums = [f'{f.sha256}  {f.path}' for f in manifest.files]
    checksums.append(f'{_hash(manifest_path)}  manifest.json')
    (base / 'checksums.sha256').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
    return base

def collect_target_evidence(*, target: str, namespace: str | None = None, name: str | None = None, kind: str | None = None, output_dir: Path = Path('evidencias'), timeout: int = 60, tail: int = 300, context: str | None = None, kubeconfig: str | None = None) -> Path:
    base = create_evidence_dir('targeted', output_dir)
    manifest = EvidenceManifest(cluster='targeted', environment='unknown', context=context or 'current')
    tail = validate_tail(tail)
    commands: list[tuple[str, str, list[str]]] = []
    if target == 'pod' and namespace and name:
        ns = validate_namespace(namespace)
        pod = validate_k8s_name(name, 'pod')
        commands += [
            ('workloads','pod-get',['get','pod',pod,'-n',ns,'-o','yaml']),
            ('workloads','pod-describe',['describe','pod',pod,'-n',ns]),
            ('events','pod-events',['get','events','-n',ns,'--field-selector',f'involvedObject.name={pod}','--sort-by=.lastTimestamp']),
            ('logs','pod-logs',['logs',pod,'-n',ns,'--tail',str(tail)]),
            ('logs','pod-previous-logs',['logs',pod,'-n',ns,'--previous','--tail',str(tail)]),
        ]
    elif target == 'namespace' and name:
        ns = validate_namespace(name)
        commands += [
            ('namespaces','namespace',['get','namespace',ns,'-o','yaml']),
            ('namespaces','pods',['get','pods','-n',ns,'-o','wide']),
            ('events','namespace-events',['get','events','-n',ns,'--sort-by=.lastTimestamp']),
            ('storage','namespace-pvcs',['get','pvc','-n',ns,'-o','wide']),
            ('network','namespace-routes',['get','routes','-n',ns,'-o','wide']),
        ]
    elif target == 'operator' and name:
        op = validate_k8s_name(name, 'operator')
        commands += [
            ('operators','clusteroperator',['get','clusteroperator',op,'-o','yaml']),
            ('operators','clusteroperator-describe',['describe','clusteroperator',op]),
            ('events','operator-events',['get','events','-A','--field-selector=type=Warning','--sort-by=.lastTimestamp']),
        ]
    elif target == 'node' and name:
        node = validate_k8s_name(name, 'node')
        commands += [
            ('nodes','node',['get','node',node,'-o','yaml']),
            ('nodes','node-describe',['describe','node',node]),
            ('nodes','node-pods',['get','pods','-A','--field-selector',f'spec.nodeName={node}','-o','wide']),
        ]
    elif target in {'workload','deployment','statefulset','daemonset','job','cronjob','replicaset'} and namespace and name:
        ns = validate_namespace(namespace)
        wk = validate_workload_kind(kind or target)
        nm = validate_k8s_name(name, 'workload')
        commands += [
            ('workloads','workload',['get',wk,nm,'-n',ns,'-o','yaml']),
            ('workloads','workload-describe',['describe',wk,nm,'-n',ns]),
            ('events','workload-events',['get','events','-n',ns,'--sort-by=.lastTimestamp']),
        ]
    else:
        commands += [
            ('cluster','clusteroperators',['get','clusteroperators','-o','wide']),
            ('events','warning-events',['get','events','-A','--field-selector=type=Warning','--sort-by=.lastTimestamp']),
        ]
    for group, item, args in commands:
        _record_command(base, manifest, group, item, args, timeout=timeout, context=context, kubeconfig=kubeconfig)
    manifest.finish()
    manifest_path = base / 'manifest.json'
    write_json(manifest_path, manifest.to_dict())
    (base / 'checksums.sha256').write_text(f'{_hash(manifest_path)}  manifest.json\n', encoding='utf-8')
    return base

def sanitize_evidence_tree(path: Path) -> int:
    count = 0
    for f in path.rglob('*'):
        if f.is_file() and f.suffix in {'.json','.yaml','.yml','.txt','.log','.md'}:
            f.write_text(sanitize_text(f.read_text(encoding='utf-8', errors='replace')), encoding='utf-8')
            count += 1
    return count
