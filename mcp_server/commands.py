from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from typing import Any, Iterable, Sequence
from . import config
from .models import CommandResult
from .sanitizers import sanitize_text
from .validators import ValidationError, validate_context, validate_environment, validate_timeout

MUTATING_OC_VERBS={"delete","apply","create","patch","edit","replace","scale","expose","set","annotate","label","exec","rsh","debug","attach","cp","rsync","port-forward"}
MUTATING_OC_ADM_VERBS={"drain","cordon","uncordon","taint","policy","groups","certificate"}
READONLY_OC_VERBS={"config","whoami","version","get","describe","logs","auth","adm"}
READONLY_OC_ADM_VERBS={"top","inspect","must-gather"}
SECRET_RESOURCES={"secret","secrets"}
GLOBAL_FLAGS_WITH_VALUE={"--context","--kubeconfig","--namespace","-n","-o","--output","--field-selector","--sort-by","--tail","-c"}
GLOBAL_FLAGS_NO_VALUE={"-A","--all-namespaces","--show-server","--previous"}
class CommandBlocked(RuntimeError): pass

def require_production_confirmation(args: argparse.Namespace) -> None:
    if args.environment != 'production':
        return
    expected = args.cluster or args.context or 'production'
    provided = args.confirm_production or os.environ.get('OPENSHIFT_AIOPS_PRODUCTION_CONFIRM')
    if provided == expected:
        return
    identity = {}
    if shutil.which('oc'):
        for name, oc_args in {
            'context': ['config', 'current-context'],
            'user': ['whoami'],
            'server': ['whoami', '--show-server'],
            'version': ['version'],
            'infrastructure': ['get', 'infrastructure', 'cluster', '-o', 'json'],
        }.items():
            identity[name] = run_oc(oc_args, timeout=min(args.timeout, 30)).to_dict()
    message = {
        'environment': 'production',
        'expected_confirmation': expected,
        'identity': identity,
        'how_to_confirm': f'export OPENSHIFT_AIOPS_PRODUCTION_CONFIRM={expected}',
    }
    if sys.stdin.isatty():
        print(json.dumps(message, ensure_ascii=False, indent=2), file=sys.stderr)
        typed = input(f"Digite '{expected}' para confirmar produção: ").strip()
        if typed == expected:
            return
    raise ValidationError('ambiente production exige confirmação explícita do nome do cluster/contexto')

def truncate(text: str, max_bytes: int = 1_048_576) -> tuple[str, bool]:
    data=text.encode('utf-8', errors='replace')
    if len(data) <= max_bytes: return text, False
    return data[:max_bytes].decode('utf-8', errors='replace') + '\n[TRUNCATED]', True

def _first_non_global(args: Sequence[str]) -> tuple[int, str | None]:
    i=0
    while i < len(args):
        if args[i] in GLOBAL_FLAGS_WITH_VALUE: i += 2; continue
        if args[i] in GLOBAL_FLAGS_NO_VALUE: i += 1; continue
        return i,args[i]
    return -1,None

def validate_oc_args(args: Sequence[str]) -> None:
    if not args: raise CommandBlocked('comando oc vazio')
    _,verb=_first_non_global(args)
    if verb is None: raise CommandBlocked('comando oc sem verbo')
    if verb not in READONLY_OC_VERBS or verb in MUTATING_OC_VERBS: raise CommandBlocked(f'verbo oc bloqueado: {verb}')
    if verb in {'get','describe'}:
        pos=list(args).index(verb); resource=args[pos+1].lower() if len(args)>pos+1 else ''
        if resource in SECRET_RESOURCES: raise CommandBlocked('conteúdo de Secrets não é coletado')
    if verb == 'adm':
        pos=list(args).index('adm'); adm=args[pos+1] if len(args)>pos+1 else ''
        if adm in MUTATING_OC_ADM_VERBS or adm not in READONLY_OC_ADM_VERBS: raise CommandBlocked(f'oc adm {adm} não autorizado')
    if verb == 'auth':
        pos=list(args).index('auth'); sub=args[pos+1] if len(args)>pos+1 else ''
        if sub != 'can-i': raise CommandBlocked('somente oc auth can-i é permitido')
    if verb == 'config':
        pos=list(args).index('config'); sub=args[pos+1] if len(args)>pos+1 else ''
        if sub != 'current-context': raise CommandBlocked('somente oc config current-context é permitido')

def build_oc_command(args: Sequence[str], *, context: str | None=None, kubeconfig: str | None=None, namespace: str | None=None) -> list[str]:
    validate_oc_args(args); cmd=['oc']
    if context: cmd += ['--context', validate_context(context)]
    if kubeconfig: cmd += ['--kubeconfig', os.path.expanduser(kubeconfig)]
    if namespace: cmd += ['-n', namespace]
    return cmd + list(args)

def run_oc(args: Sequence[str], *, timeout: int=60, context: str | None=None, kubeconfig: str | None=None, namespace: str | None=None, max_output_bytes: int=1_048_576) -> CommandResult:
    timeout=validate_timeout(timeout); cmd=build_oc_command(args, context=context, kubeconfig=kubeconfig, namespace=namespace); start=time.monotonic()
    try:
        cp=subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        out,ot=truncate(sanitize_text(cp.stdout), max_output_bytes); err,et=truncate(sanitize_text(cp.stderr), max_output_bytes//4)
        return CommandResult(cmd, cp.returncode, out, err, time.monotonic()-start, truncated=ot or et)
    except FileNotFoundError:
        return CommandResult(cmd, 127, '', 'oc não encontrado no PATH', time.monotonic()-start)
    except subprocess.TimeoutExpired as exc:
        return CommandResult(cmd, 124, sanitize_text(exc.stdout or ''), sanitize_text(exc.stderr or 'timeout executando comando'), time.monotonic()-start, timed_out=True)

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
def sha256_file(path: Path) -> str:
    h=hashlib.sha256();
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def require_tools(names: Iterable[str]) -> dict[str,bool]: return {n: shutil.which(n) is not None for n in names}

def preflight(args):
    payload={'required_tools': require_tools(['python3','oc','jq','tar','gzip','sha256sum']), 'optional_tools': require_tools(['yq','codex','podman','crc']), 'readonly': True}
    if shutil.which('oc'):
        for name, oc_args in {'current_context':['config','current-context'], 'whoami':['whoami'], 'server':['whoami','--show-server'], 'version':['version'], 'clusterversion':['get','clusterversion','-o','json'], 'infrastructure':['get','infrastructure','cluster','-o','json'], 'can_i_list':['auth','can-i','--list']}.items():
            payload[name]=run_oc(oc_args, timeout=args.timeout).to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2)); return 0 if all(payload['required_tools'].values()) else 2

def list_clusters(args): print(json.dumps({'clusters': config.configured_clusters()}, ensure_ascii=False, indent=2)); return 0
def show_context(args):
    r=run_oc(['config','current-context'], timeout=args.timeout); print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2)); return r.exit_code

def sanitize_file(args):
    src=Path(args.path or args.name or '');
    if not src.exists(): print(f'arquivo não encontrado: {src}', file=sys.stderr); return 2
    dst=Path(args.output) if args.output else src.with_suffix(src.suffix+'.sanitized')
    dst.write_text(sanitize_text(src.read_text(encoding='utf-8', errors='replace')), encoding='utf-8'); print(str(dst)); return 0

def package_evidence(args):
    src=Path(args.path or args.name or '').resolve()
    if not src.exists() or not src.is_dir(): print('diretório de evidências inválido', file=sys.stderr); return 2
    dst=Path(args.output) if args.output else src.with_suffix('.tar.gz')
    with tarfile.open(dst,'w:gz') as tar: tar.add(src, arcname=src.name)
    print(json.dumps({'package': str(dst), 'sha256': sha256_file(dst)}, ensure_ascii=False, indent=2)); return 0

def generate_report(args):
    from .reports import generate_base_report
    target=Path(args.output) if args.output else config.project_root()/'relatorios'/'relatorio-diagnostico.md'
    target.parent.mkdir(parents=True, exist_ok=True); target.write_text(generate_base_report(Path(args.path) if args.path else None, args.title), encoding='utf-8'); print(str(target)); return 0

def collect_cluster(args):
    from .collectors import collect_cluster_evidence
    out=collect_cluster_evidence(cluster=args.cluster or 'cluster-nao-informado', environment=args.environment, context=args.context, kubeconfig=args.kubeconfig, output_dir=Path(args.output_dir), timeout=args.timeout)
    print(json.dumps({'evidence_dir': str(out)}, ensure_ascii=False, indent=2)); return 0

def diagnose(args):
    from .collectors import collect_target_evidence
    out=collect_target_evidence(target=args.target, namespace=args.namespace, name=args.name, kind=args.kind, output_dir=Path(args.output_dir), timeout=args.timeout, tail=args.tail, context=args.context, kubeconfig=args.kubeconfig)
    print(json.dumps({'evidence_dir': str(out)}, ensure_ascii=False, indent=2)); return 0

def compare(args):
    from .reports import compare_evidence_dirs
    print(compare_evidence_dirs(Path(args.old), Path(args.new))); return 0

def uninstall(args):
    v=config.project_root()/'.venv'
    if v.exists(): shutil.rmtree(v); print(f'Removido ambiente virtual local: {v}')
    else: print('Nenhum ambiente virtual local encontrado.')
    return 0

def build_parser():
    p=argparse.ArgumentParser(description='OpenShift AIOps Toolkit CLI')
    p.add_argument('action', nargs='?', default='help'); p.add_argument('name', nargs='?'); p.add_argument('extra', nargs='*')
    p.add_argument('--cluster', default=os.environ.get('OPENSHIFT_AIOPS_CLUSTER')); p.add_argument('--context', default=os.environ.get('OPENSHIFT_AIOPS_CONTEXT')); p.add_argument('--kubeconfig', default=os.environ.get('OPENSHIFT_AIOPS_KUBECONFIG'))
    p.add_argument('--environment', default=os.environ.get('OPENSHIFT_AIOPS_ENVIRONMENT','development')); p.add_argument('--output-dir', default=os.environ.get('OPENSHIFT_AIOPS_OUTPUT_DIR','evidencias'))
    p.add_argument('--timeout', default=int(os.environ.get('OPENSHIFT_AIOPS_TIMEOUT','60')), type=int); p.add_argument('--tail', default=int(os.environ.get('OPENSHIFT_AIOPS_LOG_TAIL','300')), type=int)
    p.add_argument('--namespace','-n'); p.add_argument('--kind'); p.add_argument('--path'); p.add_argument('--output'); p.add_argument('--old'); p.add_argument('--new'); p.add_argument('--title', default='Relatório de Diagnóstico OpenShift'); p.add_argument('--dry-run', action='store_true'); p.add_argument('--verbose', action='store_true')
    p.add_argument('--confirm-production')
    return p

def main(argv: Sequence[str] | None=None) -> int:
    p=build_parser(); args=p.parse_args(argv)
    if args.action in {'help','--help','-h'}: p.print_help(); return 0
    try:
        args.environment=validate_environment(args.environment)
        require_production_confirmation(args)
        actions={'preflight':preflight,'list-clusters':list_clusters,'context':show_context,'validate-context':show_context,'collect-cluster':collect_cluster,'collect-diagnostic':collect_cluster,'report':generate_report,'sanitize':sanitize_file,'bundle':package_evidence,'compare':compare,'uninstall':uninstall}
        if args.action == 'diagnose': args.target=args.name or 'cluster'; return diagnose(args)
        if args.action in actions: return actions[args.action](args)
        script=args.action.replace('.sh','')
        if script.startswith('diagnosticar-'):
            args.target=script.removeprefix('diagnosticar-'); pos=[x for x in [args.name,*args.extra] if x]
            if args.target in {'pod','service','route'} and len(pos)>=2: args.namespace,args.name=pos[0],pos[1]
            elif args.target in {'namespace','node','operator','alerta'} and pos: args.name=pos[0]
            return diagnose(args)
        if script.startswith('verificar-'):
            args.target=script.removeprefix('verificar-'); return diagnose(args)
        p.error(f'ação desconhecida: {args.action}')
    except (ValidationError, CommandBlocked) as exc:
        print(sanitize_text(str(exc)), file=sys.stderr); return 2
if __name__ == '__main__': raise SystemExit(main())
