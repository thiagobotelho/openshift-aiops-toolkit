#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'EOHELP'
Instala dependências locais do OpenShift AIOps Toolkit.
Uso: scripts/install.sh
Não instala pacotes do sistema, não usa sudo e não altera cluster OpenShift.
EOHELP
  exit 0
fi
need() { command -v "$1" >/dev/null 2>&1 || missing="${missing:-} $1"; }
missing=""
need bash; need python3; need oc; need jq; need tar; need gzip; need sha256sum
if [ -n "${missing}" ]; then printf 'Dependências obrigatórias ausentes:%s\n' "${missing}" >&2; exit 2; fi
python3 - <<'PYINSTALL'
import sys
if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10 ou superior é obrigatório')
PYINSTALL
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
chmod +x scripts/*.sh tests/run.sh tests/test_scripts.sh
mkdir -p evidencias relatorios logs
python -m compileall -q mcp_server
python -m unittest discover -s tests -p 'test_*.py'
echo "Instalação concluída. Próximos passos: scripts/preflight.sh e scripts/configurar-codex-mcp.sh"
