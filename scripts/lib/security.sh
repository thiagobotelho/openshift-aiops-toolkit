set_secure_umask() { umask 077; }
redact_line() {
  sed -E 's/(Authorization:[[:space:]]*)(Bearer|Basic)[[:space:]]+[^[:space:]]+/\1[REDACTED]/Ig; s/((password|token|client_secret)[=:])[^"[:space:]]+/\1[REDACTED]/Ig'
}
