#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT}/.venv/bin/python"
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOHELP'
Configura o servidor MCP openshift-readonly para Codex CLI.
Uso: scripts/configurar-codex-mcp.sh
O script não armazena token OpenShift e usa o contexto já autenticado pelo usuário.
EOHELP
  exit 0
fi
if [ ! -x "${PYTHON_BIN}" ]; then echo "Ambiente virtual não encontrado. Execute scripts/install.sh primeiro." >&2; exit 2; fi
if ! command -v codex >/dev/null 2>&1; then echo "Codex CLI não encontrado. Use .codex/config.toml.example para configuração manual." >&2; exit 2; fi
if codex mcp list 2>/dev/null | grep -q 'openshift-readonly'; then echo "Servidor MCP openshift-readonly já existe. Nada foi sobrescrito."; codex mcp list; exit 0; fi
codex mcp add openshift-readonly -- "${PYTHON_BIN}" -m mcp_server.server
codex mcp list
