from __future__ import annotations
import json, re
from typing import Any
REDACTION = "[REDACTED]"
_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)(authorization:\s*)(bearer|basic)\s+[^\s,;]+"), r"\1" + REDACTION),
    (re.compile(r"(?i)((access|refresh|id)_token\s*[:=]\s*)[^\s,}\]]+"), r"\1" + REDACTION),
    (re.compile(r"(?i)((client_secret|clientSecret|password|passwd|senha)\s*[:=]\s*)[^\s,}\]]+"), r"\1" + REDACTION),
    (re.compile(r"(?i)((pullSecret|pull-secret|kubeadmin password)\s*[:=]\s*)[^\n]+"), r"\1" + REDACTION),
    (re.compile(r"(?i)(cookie:\s*)[^\n]+"), r"\1" + REDACTION),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), REDACTION),
    (re.compile(r"https?://([^:/\s]+):([^@/\s]+)@"), "https://" + REDACTION + "@"),
    (re.compile(r"(?i)(token:\s*)[A-Za-z0-9._~+/=-]{12,}"), r"\1" + REDACTION),
    (re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"), REDACTION),
    (re.compile(r"\b[A-Za-z0-9+/]{80,}={0,2}\b"), REDACTION),
    (re.compile(r"\b[0-9a-fA-F]{64,}\b"), REDACTION),
]
def sanitize_text(value: str | bytes | None, replacement: str = REDACTION) -> str:
    if value is None: return ""
    text = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
    for pattern, repl in _PATTERNS:
        text = pattern.sub(repl.replace(REDACTION, replacement), text)
    return text
def sanitize_obj(value: Any) -> Any:
    if isinstance(value, str): return sanitize_text(value)
    if isinstance(value, list): return [sanitize_obj(i) for i in value]
    if isinstance(value, tuple): return tuple(sanitize_obj(i) for i in value)
    if isinstance(value, dict):
        out={}
        for k,v in value.items():
            out[k] = REDACTION if re.search(r"(?i)(token|secret|password|passwd|senha|cookie|authorization)", str(k)) else sanitize_obj(v)
        return out
    return value
def sanitize_json_text(text: str) -> str:
    try: return json.dumps(sanitize_obj(json.loads(text)), ensure_ascii=False, indent=2)
    except Exception: return sanitize_text(text)
