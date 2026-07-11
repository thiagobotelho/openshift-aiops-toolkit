#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
for script in scripts/*.sh scripts/lib/*.sh; do
  bash -n "${script}"
done
for script in scripts/*.sh; do
  test -x "${script}"
done
