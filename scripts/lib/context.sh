show_context_summary() {
  if command -v oc >/dev/null 2>&1; then
    oc config current-context 2>/dev/null | sed 's/^/context: /' || true
    oc whoami 2>/dev/null | sed 's/^/user: /' || true
    oc whoami --show-server 2>/dev/null | sed 's/^/server: /' || true
  fi
}
