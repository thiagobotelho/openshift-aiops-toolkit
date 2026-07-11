sanitize_stream() { python3 -c 'import sys; from mcp_server.sanitizers import sanitize_text; print(sanitize_text(sys.stdin.read()), end="")'; }
