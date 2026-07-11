require_command() { command -v "$1" >/dev/null 2>&1 || { log_error "Dependência ausente: $1"; return 1; }; }
validate_not_empty() { [ -n "${2:-}" ] || { log_error "$1 é obrigatório"; return 2; }; }
