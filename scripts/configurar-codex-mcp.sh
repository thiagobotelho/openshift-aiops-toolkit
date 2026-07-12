#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT}/.venv/bin/python"
YES=false
REPLACE=false
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOHELP'
Configura o servidor MCP openshift-readonly para Codex CLI.
Uso:
  scripts/configurar-codex-mcp.sh [--yes] [--replace]

Opções:
  --yes    Aplica a configuração sem prompt interativo.
  --replace Remove e recria apenas o servidor openshift-readonly se ele já existir.

O script não armazena token OpenShift e usa o contexto já autenticado pelo usuário.
EOHELP
  exit 0
fi
for arg in "$@"; do
  case "${arg}" in
    --yes) YES=true ;;
    --replace) REPLACE=true ;;
  esac
done
if [ ! -x "${PYTHON_BIN}" ]; then echo "Ambiente virtual não encontrado. Execute scripts/install.sh primeiro." >&2; exit 2; fi
if ! command -v codex >/dev/null 2>&1; then echo "Codex CLI não encontrado. Use .codex/config.toml.example para configuração manual." >&2; exit 2; fi
if ! "${PYTHON_BIN}" -c 'import mcp_server.server' >/dev/null 2>&1; then
  echo "Falha ao importar mcp_server.server usando ${PYTHON_BIN}." >&2
  exit 2
fi
if codex mcp list 2>/dev/null | grep -q 'openshift-readonly'; then
  if [ "${REPLACE}" = "true" ]; then
    codex mcp remove openshift-readonly
  else
    echo "Servidor MCP openshift-readonly já existe. Nada foi sobrescrito."
    codex mcp list
    exit 0
  fi
fi
ADD_ARGS=(mcp add --env "PYTHONPATH=${ROOT}")
if [ -n "${OPENSHIFT_AIOPS_COMMAND_PREFIX:-}" ]; then
  ADD_ARGS+=(--env "OPENSHIFT_AIOPS_COMMAND_PREFIX=${OPENSHIFT_AIOPS_COMMAND_PREFIX}")
fi
if [ -n "${OPENSHIFT_AIOPS_OC_BIN:-}" ]; then
  ADD_ARGS+=(--env "OPENSHIFT_AIOPS_OC_BIN=${OPENSHIFT_AIOPS_OC_BIN}")
fi
ADD_ARGS+=(openshift-readonly -- "${PYTHON_BIN}" -m mcp_server.server)
echo "Projeto: ${ROOT}"
echo "Python: ${PYTHON_BIN}"
echo "Comando MCP:"
printf "  codex"
printf " %q" "${ADD_ARGS[@]}"
printf "\n"
if [ "${YES}" != "true" ]; then
  printf "Deseja adicionar o servidor MCP openshift-readonly ao Codex? [y/N] "
  read -r answer
  case "${answer}" in
    y|Y|yes|YES|sim|SIM) ;;
    *) echo "Nenhuma configuração foi alterada."; exit 0 ;;
  esac
fi
codex "${ADD_ARGS[@]}"
codex mcp list
