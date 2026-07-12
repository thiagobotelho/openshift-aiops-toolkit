#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
python3 -m compileall -q mcp_server
bash tests/test_scripts.sh
make help >/dev/null
make check >/dev/null 2>&1
python3 -m unittest discover -s tests -p 'test_*.py'
