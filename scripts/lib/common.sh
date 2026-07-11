#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONPATH="${TOOLKIT_ROOT}:${PYTHONPATH:-}"
source "${SCRIPT_DIR}/logging.sh"
source "${SCRIPT_DIR}/security.sh"
source "${SCRIPT_DIR}/validators.sh"
source "${SCRIPT_DIR}/context.sh"
set_secure_umask
on_error() { local exit_code=$?; log_error "Falha em ${0##*/} na linha ${BASH_LINENO[0]} com código ${exit_code}"; exit "${exit_code}"; }
trap on_error ERR
usage_common() {
  cat <<'EOHELP'
Uso:
  script [argumentos] [opções]

Opções comuns:
  --cluster <nome>          Cluster do inventário.
  --context <contexto>      Contexto kubeconfig explícito.
  --kubeconfig <arquivo>    Caminho do kubeconfig.
  --environment <ambiente>  development, homologation, production ou laboratory.
  --output-dir <diretório>  Diretório de evidências.
  --timeout <segundos>      Timeout por comando.
  --tail <linhas>           Linhas de log para diagnóstico de Pod.
  --dry-run                 Mostra intenção sem alterar cluster.
  --verbose                 Saída detalhada.
  -h, --help                Ajuda.

Política: somente leitura, sem conteúdo de Secrets e sem remediação automática.
EOHELP
}
run_python_action() {
  local action="$1"; shift || true
  if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then usage_common; exit 0; fi
  cd "${TOOLKIT_ROOT}"
  log_info "Executando ação ${action} em modo somente leitura"
  python3 -m mcp_server.commands "${action}" "$@"
}
