from __future__ import annotations
import json, sys
from typing import Any
from .sanitizers import sanitize_obj, sanitize_text
from .tools import call_tool, list_tools
try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    FastMCP = None
SERVER_NAME='openshift-readonly'
def _jsonrpc_response(request_id: Any, result: Any = None, error: Any = None) -> dict[str, Any]:
    payload={'jsonrpc':'2.0','id':request_id}
    if error is not None:
        payload['error']=error
    else:
        payload['result']=sanitize_obj(result)
    return payload
def _fallback_stdio() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req=json.loads(line); method=req.get('method'); rid=req.get('id'); params=req.get('params') or {}
            if method == 'initialize':
                resp=_jsonrpc_response(rid, {'protocolVersion':'2024-11-05','serverInfo':{'name':SERVER_NAME,'version':'0.1.0'},'capabilities':{'tools':{}}})
            elif method == 'tools/list':
                resp=_jsonrpc_response(rid, {'tools': list_tools()})
            elif method == 'tools/call':
                result=call_tool(params.get('name'), params.get('arguments') or {})
                resp=_jsonrpc_response(rid, {'content':[{'type':'text','text':json.dumps(result, ensure_ascii=False, indent=2)}]})
            else:
                resp=_jsonrpc_response(rid, error={'code':-32601,'message':'método não suportado'})
        except Exception as exc:
            resp=_jsonrpc_response(None, error={'code':-32000,'message':sanitize_text(str(exc))})
        print(json.dumps(resp, ensure_ascii=False), flush=True)
def _run_fastmcp() -> None:
    mcp=FastMCP(SERVER_NAME)
    for tool in list_tools():
        name=tool['name']; description=tool['description']
        def _make_handler(tool_name: str, desc: str):
            def handler(arguments: dict[str, Any] | None = None) -> str:
                return json.dumps(call_tool(tool_name, arguments or {}), ensure_ascii=False, indent=2)
            handler.__name__=tool_name; handler.__doc__=desc
            return handler
        mcp.tool(name=name, description=description)(_make_handler(name, description))
    mcp.run(transport='stdio')
def main() -> int:
    if FastMCP is not None:
        _run_fastmcp()
    else:
        _fallback_stdio()
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
