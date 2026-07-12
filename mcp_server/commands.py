from __future__ import annotations
import argparse, hashlib, json, os, re, shlex, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse
from . import config
from .models import CommandResult
from .sanitizers import sanitize_text
from .validators import (
    ValidationError,
    validate_context,
    validate_environment,
    validate_local_path,
    validate_timeout,
)

MUTATING_OC_VERBS={"delete","apply","create","patch","edit","replace","scale","expose","set","annotate","label","exec","rsh","debug","attach","cp","rsync","port-forward"}
MUTATING_OC_ADM_VERBS={"drain","cordon","uncordon","taint","policy","groups","certificate"}
READONLY_OC_VERBS={"config","whoami","version","api-resources","api-versions","get","describe","logs","auth","adm"}
READONLY_OC_ADM_VERBS={"top","inspect","must-gather"}
SECRET_RESOURCES={"secret","secrets"}
GLOBAL_FLAGS_WITH_VALUE={"--context","--kubeconfig","--namespace","-n","-o","--output","--field-selector","--sort-by","--tail","-c"}
GLOBAL_FLAGS_NO_VALUE={"-A","--all-namespaces","--show-server","--previous"}
class CommandBlocked(RuntimeError): pass

ALLOWED_COMMAND_PREFIXES = {(), ('flatpak-spawn', '--host')}
DEFAULT_ENVIRONMENT = 'current'

def command_prefix() -> list[str]:
    raw = os.environ.get('OPENSHIFT_AIOPS_COMMAND_PREFIX', '').strip()
    if not raw:
        return []
    parts = shlex.split(raw)
    if tuple(parts) not in ALLOWED_COMMAND_PREFIXES:
        raise CommandBlocked('prefixo de comando não autorizado')
    return parts

def oc_binary() -> str:
    return os.environ.get('OPENSHIFT_AIOPS_OC_BIN', 'oc')

def oc_available() -> bool:
    binary = oc_binary()
    if os.path.sep not in binary and shutil.which(binary) is None and not command_prefix():
        return False
    try:
        completed = subprocess.run(
            command_prefix() + [binary, 'version', '--client'],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return completed.returncode == 0
    except Exception:
        return False

def slugify_cluster(value: str | None, fallback: str = 'current-cluster') -> str:
    raw = (value or '').strip().lower()
    if raw.startswith('api.'):
        raw = raw.removeprefix('api.')
    raw = raw.replace('_', '-')
    raw = re.sub(r'[^a-z0-9.-]+', '-', raw)
    raw = re.sub(r'-+', '-', raw).strip('-.')
    return raw or fallback

def cluster_name_from_api_server(value: str | None, fallback: str = 'openshift-cluster') -> str:
    """Derive a stable, filesystem-safe cluster identifier from an API URL.

    Examples:
      https://api.crc.testing:6443 -> crc
      https://api.cluster-prd.example.com:6443 -> cluster-prd
    """
    raw = (value or '').strip()
    if not raw:
        return fallback
    parsed = urlparse(raw)
    host = parsed.hostname or raw
    labels = [item for item in host.lower().split('.') if item]
    if labels and labels[0] == 'api' and len(labels) > 1:
        return slugify_cluster(labels[1], fallback=fallback)
    if labels:
        return slugify_cluster(labels[0], fallback=fallback)
    return slugify_cluster(host, fallback=fallback)

def detect_cluster_name(*, timeout: int = 10, context: str | None = None, kubeconfig: str | None = None) -> str:
    infrastructure = run_oc(['get', 'infrastructure', 'cluster', '-o', 'json'], timeout=timeout, context=context, kubeconfig=kubeconfig)
    if infrastructure.exit_code == 0 and infrastructure.stdout.strip():
        try:
            data = json.loads(infrastructure.stdout)
            name = ((data.get('status') or {}).get('infrastructureName') or '').strip()
            if name:
                return slugify_cluster(name, fallback='openshift-cluster')
        except Exception:
            pass
    server = run_oc(['whoami', '--show-server'], timeout=timeout, context=context, kubeconfig=kubeconfig)
    if server.exit_code == 0 and server.stdout.strip():
        return cluster_name_from_api_server(server.stdout.strip())
    current = run_oc(['config', 'current-context'], timeout=timeout, context=context, kubeconfig=kubeconfig)
    if current.exit_code == 0 and current.stdout.strip():
        parts = [part for part in current.stdout.strip().split('/') if part]
        if len(parts) >= 2:
            return slugify_cluster(parts[1])
        return slugify_cluster(current.stdout.strip())
    return 'openshift-cluster'

def resolve_cluster_name(args: argparse.Namespace) -> str:
    value = args.cluster or os.environ.get('OPENSHIFT_AIOPS_CLUSTER')
    if value:
        return slugify_cluster(value)
    if getattr(args, 'offline', False) or getattr(args, 'dry_run', False):
        return 'current-cluster'
    return detect_cluster_name(timeout=min(getattr(args, 'timeout', 60), 10), context=args.context, kubeconfig=args.kubeconfig)

def emit_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

def command_stdout(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key) or {}
    if isinstance(value, dict):
        return str(value.get('stdout') or '').strip()
    return ''

def command_exit(payload: dict[str, Any], key: str) -> int | None:
    value = payload.get(key) or {}
    if isinstance(value, dict):
        exit_code = value.get('exit_code')
        return int(exit_code) if isinstance(exit_code, int) else None
    return None

def summarize_version(payload: dict[str, Any]) -> str:
    raw = command_stdout(payload, 'clusterversion')
    if not raw:
        return 'não identificado'
    try:
        data = json.loads(raw)
        items = data.get('items') or []
        if not items:
            return 'não identificado'
        status = items[0].get('status') or {}
        version = (status.get('desired') or {}).get('version') or 'desconhecida'
        conditions = {item.get('type'): item for item in status.get('conditions') or []}
        available = (conditions.get('Available') or {}).get('status', '?')
        progressing = (conditions.get('Progressing') or {}).get('status', '?')
        failing = (conditions.get('Failing') or {}).get('status', '?')
        upgradeable = (conditions.get('Upgradeable') or {}).get('status')
        suffix = f'Available={available}, Progressing={progressing}, Failing={failing}'
        if upgradeable is not None:
            suffix += f', Upgradeable={upgradeable}'
        return f'{version} ({suffix})'
    except Exception:
        return 'não identificado'

def summarize_infrastructure(payload: dict[str, Any]) -> str:
    raw = command_stdout(payload, 'infrastructure')
    if not raw:
        return 'não identificado'
    try:
        data = json.loads(raw)
        status = data.get('status') or {}
        topology = status.get('controlPlaneTopology') or status.get('infrastructureTopology') or 'desconhecida'
        name = status.get('infrastructureName') or 'sem nome'
        platform = status.get('platform') or 'desconhecida'
        return f'{name}, plataforma={platform}, topologia={topology}'
    except Exception:
        return 'não identificado'

def print_preflight_summary(payload: dict[str, Any]) -> None:
    required = payload.get('required_tools') or {}
    missing_required = [name for name, ok in required.items() if not ok]
    optional = payload.get('optional_tools') or {}
    missing_optional = [name for name, ok in optional.items() if not ok]
    print('OpenShift AIOps Toolkit — preflight')
    print(f"Modo: {'offline/local' if payload.get('mode') == 'offline' else 'cluster atual'}")
    print('Política: somente leitura')
    if missing_required:
        print(f"Obrigatórios ausentes: {', '.join(missing_required)}")
    else:
        print('Obrigatórios: OK')
    if missing_optional:
        print(f"Opcionais ausentes: {', '.join(missing_optional)}")
    if payload.get('mode') != 'offline':
        print(f"Contexto: {command_stdout(payload, 'current_context') or 'não identificado'}")
        print(f"Usuário: {command_stdout(payload, 'whoami') or 'não identificado'}")
        print(f"API: {command_stdout(payload, 'server') or 'não identificada'}")
        print(f"OpenShift: {summarize_version(payload)}")
        print(f"Infraestrutura: {summarize_infrastructure(payload)}")
        can_i = command_exit(payload, 'can_i_list')
        if can_i is not None:
            print(f"Permissões consultadas: {'OK' if can_i == 0 else 'falhou'}")
        print('Próximo passo sugerido: ./openshift-aiops health')
    else:
        print('Próximo passo sugerido: make check-cluster')

def print_path_result(title: str, path: Path | str, *, next_steps: list[str] | None = None) -> None:
    print(title)
    print(f'Caminho: {path}')
    if next_steps:
        print('Próximos passos:')
        for step in next_steps:
            print(f'  {step}')

def warn_deprecated_parameters(argv: Sequence[str] | None, args: argparse.Namespace) -> None:
    raw = list(argv) if argv is not None else sys.argv[1:]
    messages: list[str] = []
    if '--environment' in raw or os.environ.get('OPENSHIFT_AIOPS_ENVIRONMENT') not in {None, '', DEFAULT_ENVIRONMENT}:
        messages.append('AVISO: --environment/OPENSHIFT_AIOPS_ENVIRONMENT é opcional; o contexto atual do oc é usado para diagnósticos comuns.')
    if '--cluster' in raw or os.environ.get('OPENSHIFT_AIOPS_CLUSTER'):
        messages.append('AVISO: --cluster/OPENSHIFT_AIOPS_CLUSTER é tratado como alias/metadado; a identidade principal vem da API e do contexto atual.')
    if '--confirm-production' in raw or os.environ.get('OPENSHIFT_AIOPS_PRODUCTION_CONFIRM'):
        messages.append('AVISO: --confirm-production não é necessário em consultas read-only; must-gather usa confirmação própria.')
    if args.action in {'must-gather', 'must-gather-preflight'}:
        return
    if getattr(args, 'json', False):
        return
    for message in messages:
        print(message, file=sys.stderr)

def confirm_must_gather(args: argparse.Namespace, cluster_name: str) -> None:
    provided = getattr(args, 'confirm_must_gather', None) or os.environ.get('OPENSHIFT_AIOPS_MUST_GATHER_CONFIRM')
    if provided == cluster_name:
        return
    message = (
        'ATENÇÃO: o must-gather cria recursos temporários no cluster e pode coletar dados sensíveis.\n'
        f'Cluster: {cluster_name}\n'
        f'Destino: {args.output_dir}\n'
        f'Digite "{cluster_name}" para confirmar: '
    )
    if sys.stdin.isatty():
        typed = input(message).strip()
        if typed == cluster_name:
            return
    raise ValidationError('must-gather exige confirmação explícita do identificador do cluster')

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
        resource_names = {item.split('/')[0] for item in resource.split(',') if item}
        if resource_names & SECRET_RESOURCES: raise CommandBlocked('conteúdo de Secrets não é coletado')
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
    validate_oc_args(args); cmd=command_prefix() + [oc_binary()]
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

def required_tools_status(names: Iterable[str]) -> dict[str, bool]:
    status = require_tools([name for name in names if name != 'oc'])
    if 'oc' in names:
        status['oc'] = oc_available()
    return status

def resolve_project_path(value: str | Path, *, must_exist: bool = False) -> Path:
    path = validate_local_path(str(value), config.project_root())
    if must_exist and not path.exists():
        raise ValidationError(f'path não encontrado: {path}')
    return path

def preflight(args):
    offline = args.offline or os.environ.get('OPENSHIFT_AIOPS_OFFLINE', '').lower() in {'1', 'true', 'yes'}
    required_names = ['python3', 'tar', 'gzip', 'sha256sum']
    if not offline:
        required_names.extend(['oc', 'jq'])
    payload={
        'mode': 'offline' if offline else 'cluster',
        'required_tools': required_tools_status(required_names),
        'optional_tools': require_tools(['jq', 'yq', 'codex', 'podman', 'crc']),
        'readonly': True,
        'venv_exists': (config.project_root() / '.venv').exists(),
    }
    try:
        import mcp  # type: ignore[import-not-found]
        payload['mcp_sdk'] = {'available': True, 'version': getattr(mcp, '__version__', 'unknown')}
    except Exception as exc:
        payload['mcp_sdk'] = {'available': False, 'error': type(exc).__name__}
    if offline:
        if getattr(args, 'json', False) or getattr(args, 'verbose', False):
            emit_json(payload)
        else:
            print_preflight_summary(payload)
        return 0 if all(payload['required_tools'].values()) else 2
    if oc_available():
        for name, oc_args in {'current_context':['config','current-context'], 'whoami':['whoami'], 'server':['whoami','--show-server'], 'version':['version'], 'clusterversion':['get','clusterversion','-o','json'], 'infrastructure':['get','infrastructure','cluster','-o','json'], 'can_i_list':['auth','can-i','--list']}.items():
            payload[name]=run_oc(oc_args, timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig).to_dict()
    if getattr(args, 'json', False) or getattr(args, 'verbose', False):
        emit_json(payload)
    else:
        print_preflight_summary(payload)
    return 0 if all(payload['required_tools'].values()) else 2

def list_clusters(args):
    payload = {'clusters': config.configured_clusters()}
    if getattr(args, 'json', False):
        emit_json(payload)
    else:
        clusters = payload['clusters']
        if not clusters:
            print('Nenhum cluster habilitado no inventário.')
        else:
            print('Clusters configurados:')
            for item in clusters:
                print(f"- {item.get('name')} ({item.get('environment', 'sem ambiente')}) contexto={item.get('context', '-')}")
    return 0
def show_context(args):
    r=run_oc(['config','current-context'], timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
    if getattr(args, 'json', False):
        emit_json(r.to_dict())
    else:
        print(f"Contexto atual: {r.stdout.strip() if r.stdout else 'não identificado'}")
    return r.exit_code

def sanitize_file(args):
    src=resolve_project_path(args.path or args.name or '', must_exist=True)
    dst=resolve_project_path(args.output) if args.output else src.with_suffix(src.suffix+'.sanitized')
    dst.write_text(sanitize_text(src.read_text(encoding='utf-8', errors='replace')), encoding='utf-8'); print(str(dst)); return 0

def package_evidence(args):
    src=resolve_project_path(args.path or args.name or '', must_exist=True)
    if not src.exists() or not src.is_dir(): print('diretório de evidências inválido', file=sys.stderr); return 2
    dst=resolve_project_path(args.output) if args.output else src.with_suffix('.tar.gz')
    with tarfile.open(dst,'w:gz') as tar: tar.add(src, arcname=src.name)
    print(json.dumps({'package': str(dst), 'sha256': sha256_file(dst)}, ensure_ascii=False, indent=2)); return 0

def generate_report(args):
    from .reports import generate_base_report
    evidence = resolve_project_path(args.path, must_exist=True) if args.path else None
    target=resolve_project_path(args.output) if args.output else config.project_root()/'relatorios'/'relatorio-diagnostico.md'
    target.parent.mkdir(parents=True, exist_ok=True); target.write_text(generate_base_report(evidence, args.title), encoding='utf-8')
    if getattr(args, 'json', False):
        emit_json({'report': str(target), 'evidence_dir': str(evidence) if evidence else None})
    else:
        print_path_result('Relatório gerado.', target, next_steps=[f'Abra: {target}'])
    return 0

def collect_cluster(args):
    from .collectors import collect_cluster_evidence
    cluster_name = resolve_cluster_name(args)
    if args.dry_run or args.offline:
        payload = {'dry_run': True, 'offline': args.offline, 'action': 'collect-cluster', 'cluster': cluster_name, 'environment': args.environment}
        if getattr(args, 'json', False):
            emit_json(payload)
        else:
            print('Coleta não executada.')
            print(f"Modo: {'offline' if args.offline else 'dry-run'}")
            print(f"Cluster lógico: {cluster_name}")
        return 0
    out=collect_cluster_evidence(cluster=cluster_name, environment=args.environment, context=args.context, kubeconfig=args.kubeconfig, output_dir=resolve_project_path(args.output_dir), timeout=args.timeout)
    if getattr(args, 'json', False):
        emit_json({'evidence_dir': str(out), 'cluster': cluster_name, 'environment': args.environment})
    else:
        try:
            relative = out.relative_to(config.project_root())
        except ValueError:
            relative = out
        print_path_result(
            'Coleta completa segura concluída.',
            out,
            next_steps=[
                f'LATEST="{relative}"',
                '(cd "$LATEST" && sha256sum -c checksums.sha256)',
                'scripts/gerar-relatorio.sh --path "$LATEST" --output relatorios/relatorio-diagnostico.md',
            ],
        )
    return 0

def diagnose(args):
    from .collectors import collect_target_evidence
    if args.dry_run or args.offline:
        payload = {'dry_run': True, 'offline': args.offline, 'action': 'diagnose', 'target': args.target, 'namespace': args.namespace, 'name': args.name}
        if getattr(args, 'json', False):
            emit_json(payload)
        else:
            print('Diagnóstico direcionado não executado.')
            print(f"Alvo: {args.target}")
        return 0
    out=collect_target_evidence(target=args.target, namespace=args.namespace, name=args.name, kind=args.kind, output_dir=resolve_project_path(args.output_dir), timeout=args.timeout, tail=args.tail, context=args.context, kubeconfig=args.kubeconfig)
    if getattr(args, 'json', False):
        emit_json({'evidence_dir': str(out), 'target': args.target, 'namespace': args.namespace, 'name': args.name})
    else:
        print_path_result('Diagnóstico direcionado concluído.', out)
    return 0

def compare(args):
    from .reports import compare_evidence_dirs
    print(compare_evidence_dirs(resolve_project_path(args.old, must_exist=True), resolve_project_path(args.new, must_exist=True))); return 0

def must_gather_preflight(args):
    from .must_gather import collect_preflight
    cluster_name = resolve_cluster_name(args)
    payload = collect_preflight(cluster_name, args.timeout, args.output_dir, context=args.context, kubeconfig=args.kubeconfig)
    if getattr(args, 'json', False) or getattr(args, 'verbose', False):
        emit_json(payload)
    else:
        print('Preflight de must-gather concluído.')
        print(f"Cluster lógico: {payload.get('cluster')}")
        print(f"Destino planejado: {payload.get('destination')}")
        print(f"Gitignore protege evidências: {'sim' if payload.get('gitignore_covers_evidence') else 'não'}")
        print(f"Espaço livre: {int((payload.get('disk') or {}).get('free', 0) / (1024 ** 3))} GiB")
        print(f"Suporte a --dest-dir: {'sim' if (payload.get('supported_options') or {}).get('dest_dir') else 'não'}")
        print('Próximo passo, se autorizado: make must-gather')
    return 0

def must_gather_collect(args):
    from .must_gather import execute_must_gather
    cluster_name = resolve_cluster_name(args)
    confirm_must_gather(args, cluster_name)
    out = execute_must_gather(cluster=cluster_name, output_dir=args.output_dir, timeout=args.timeout, context=args.context, kubeconfig=args.kubeconfig)
    if getattr(args, 'json', False):
        emit_json({'must_gather_dir': str(out), 'cluster': cluster_name})
    else:
        print_path_result(
            'Must-gather concluído.',
            out,
            next_steps=[
                f'MUST_GATHER="{out}"',
                'make analyze-must-gather RESOURCE="$MUST_GATHER"',
                'Não publique raw/ sem revisão.',
            ],
        )
    return 0

def must_gather_analyze(args):
    from .must_gather import analyze_must_gather
    target = resolve_project_path(args.path or args.name or '', must_exist=True)
    report = analyze_must_gather(target)
    if getattr(args, 'json', False):
        emit_json({'analysis_report': str(report)})
    else:
        print_path_result('Análise offline de must-gather gerada.', report)
    return 0

def uninstall(args):
    v=config.project_root()/'.venv'
    if v.exists(): shutil.rmtree(v); print(f'Removido ambiente virtual local: {v}')
    else: print('Nenhum ambiente virtual local encontrado.')
    return 0

def build_parser():
    p=argparse.ArgumentParser(description='OpenShift AIOps Toolkit CLI')
    p.add_argument('action', nargs='?', default='help'); p.add_argument('name', nargs='?'); p.add_argument('extra', nargs='*')
    p.add_argument('--cluster', default=os.environ.get('OPENSHIFT_AIOPS_CLUSTER')); p.add_argument('--context', default=os.environ.get('OPENSHIFT_AIOPS_CONTEXT')); p.add_argument('--kubeconfig', default=os.environ.get('OPENSHIFT_AIOPS_KUBECONFIG'))
    p.add_argument('--environment', default=os.environ.get('OPENSHIFT_AIOPS_ENVIRONMENT', DEFAULT_ENVIRONMENT)); p.add_argument('--output-dir', default=os.environ.get('OPENSHIFT_AIOPS_OUTPUT_DIR','evidencias'))
    p.add_argument('--timeout', default=int(os.environ.get('OPENSHIFT_AIOPS_TIMEOUT','60')), type=int); p.add_argument('--tail', default=int(os.environ.get('OPENSHIFT_AIOPS_LOG_TAIL','300')), type=int)
    p.add_argument('--namespace','-n'); p.add_argument('--kind'); p.add_argument('--path'); p.add_argument('--output'); p.add_argument('--old'); p.add_argument('--new'); p.add_argument('--title', default='Relatório de Diagnóstico OpenShift'); p.add_argument('--dry-run', action='store_true'); p.add_argument('--offline', action='store_true'); p.add_argument('--verbose', action='store_true')
    p.add_argument('--json', action='store_true', help='mantém saída detalhada em JSON para automação')
    p.add_argument('--confirm-production')
    p.add_argument('--confirm-must-gather')
    return p

def main(argv: Sequence[str] | None=None) -> int:
    p=build_parser(); args=p.parse_args(argv)
    if args.action in {'help','--help','-h'}: p.print_help(); return 0
    try:
        args.environment=validate_environment(args.environment)
        warn_deprecated_parameters(argv, args)
        actions={'preflight':preflight,'list-clusters':list_clusters,'context':show_context,'validate-context':show_context,'collect-cluster':collect_cluster,'collect-diagnostic':collect_cluster,'report':generate_report,'sanitize':sanitize_file,'bundle':package_evidence,'compare':compare,'uninstall':uninstall,'must-gather-preflight':must_gather_preflight,'must-gather':must_gather_collect,'analyze-must-gather':must_gather_analyze}
        if args.action == 'diagnose': args.target=args.name or 'cluster'; return diagnose(args)
        if args.action in actions: return actions[args.action](args)
        script=args.action.replace('.sh','')
        if script.startswith('diagnosticar-'):
            args.target=script.removeprefix('diagnosticar-'); pos=[x for x in [args.name,*args.extra] if x]
            if args.target == 'must-gather': return must_gather_collect(args)
            if args.target in {'pod','service','route','workload'} and len(pos)>=2: args.namespace,args.name=pos[0],pos[1]
            elif args.target in {'namespace','node','operator','alerta'} and pos: args.name=pos[0]
            return diagnose(args)
        if script.startswith('verificar-'):
            args.target=script.removeprefix('verificar-'); return diagnose(args)
        p.error(f'ação desconhecida: {args.action}')
    except (ValidationError, CommandBlocked) as exc:
        print(sanitize_text(str(exc)), file=sys.stderr); return 2
if __name__ == '__main__': raise SystemExit(main())
