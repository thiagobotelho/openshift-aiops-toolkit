#!/usr/bin/env bash

OUTPUT_ASCII="${OPENSHIFT_AIOPS_ASCII:-false}"
OUTPUT_NO_COLOR="${NO_COLOR:+true}"

terminal_width() {
  tput cols 2>/dev/null || printf '100\n'
}

supports_color() {
  [ -t 1 ] || return 1
  [ "${OUTPUT_NO_COLOR:-false}" != "true" ] || return 1
  command -v tput >/dev/null 2>&1 || return 1
  [ "$(tput colors 2>/dev/null || printf '0')" -ge 8 ]
}

supports_unicode() {
  [ "${OUTPUT_ASCII:-false}" != "true" ] || return 1
  case "${LC_ALL:-${LC_CTYPE:-${LANG:-}}}" in
    *UTF-8*|*utf8*|*utf-8*) return 0 ;;
    *) return 1 ;;
  esac
}

status_label() {
  local status="$1"
  if supports_unicode; then
    case "${status}" in
      ok) printf '✓ OK' ;;
      warning) printf '! ALERTA' ;;
      critical) printf '✗ CRÍTICO' ;;
      informational) printf 'i INFORMATIVO' ;;
      not_applicable) printf -- '- NÃO APLICÁVEL' ;;
      permission_denied) printf '! SEM PERMISSÃO' ;;
      unavailable) printf '! INDISPONÍVEL' ;;
      *) printf '? NÃO VERIFICADO' ;;
    esac
  else
    case "${status}" in
      ok) printf '[OK]' ;;
      warning) printf '[ALERTA]' ;;
      critical) printf '[CRITICO]' ;;
      informational) printf '[INFO]' ;;
      not_applicable) printf '[N/A]' ;;
      permission_denied) printf '[SEM PERMISSAO]' ;;
      unavailable) printf '[INDISPONIVEL]' ;;
      *) printf '[NAO VERIFICADO]' ;;
    esac
  fi
}

print_header() {
  printf 'OpenShift AIOps Toolkit\n'
  if supports_unicode; then
    printf '────────────────────────────────────────────────────────────\n'
  else
    printf '%s\n' '------------------------------------------------------------'
  fi
}

print_section() {
  printf '\n%s\n' "$1"
  if supports_unicode; then
    printf '────────────────────────────────────────────────────────────\n'
  else
    printf '%s\n' '------------------------------------------------------------'
  fi
}

print_key_value() {
  printf '  %-18s %s\n' "$1:" "${2:-não informado}"
}

print_info() {
  printf 'INFO: %s\n' "$*"
}

print_warning() {
  printf 'AVISO: %s\n' "$*" >&2
}

print_error() {
  printf 'ERRO: %s\n' "$*" >&2
}

truncate_text() {
  local text="$1"
  local limit="${2:-120}"
  if [ "${#text}" -le "${limit}" ]; then
    printf '%s\n' "${text}"
  else
    printf '%s ...[truncado]\n' "${text:0:$((limit - 15))}"
  fi
}
