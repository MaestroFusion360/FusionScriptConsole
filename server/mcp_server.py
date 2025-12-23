"""
Minimal HTTP server for Fusion that accepts POST /mcp with Python code.
"""

import hmac
import json
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Any, Dict, Tuple, Optional

from .task_manager import TaskManager
from tools.execute_api_script import handler as execute_script_handler
import config

try:
    import adsk.core
    app = adsk.core.Application.get()
except Exception:
    app = None


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server that handles requests in separate threads."""
    daemon_threads = True
    allow_reuse_address = True


class MCPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for minimal /mcp endpoint."""

    def _is_authorized(self) -> bool:
        api_key = config.get_api_key() or ""
        if not api_key:
            return False
        header_key = self.headers.get('X-API-Key', '')
        auth_header = self.headers.get('Authorization', '')
        bearer_key = auth_header.replace('Bearer ', '', 1) if auth_header else ''
        return hmac.compare_digest(header_key, api_key) or hmac.compare_digest(bearer_key, api_key)

    def _send_unauthorized(self):
        self.send_response(401)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"ok": false, "error": "Unauthorized"}')

    def do_POST(self):
        if not self._is_authorized():
            self._send_unauthorized()
            return
        if self.path != '/mcp':
            self.send_error(404, "Not Found")
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        except Exception as exc:
            self.send_error(500, str(exc))
            return

        code = (
            request_data.get('code')
            or request_data.get('script')
            or request_data.get('python')
            or ''
        )
        if not code:
            self.send_error(400, "Missing 'code' in request body")
            return

        response = self._execute_python(code)
        self._send_json_response(response)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            if not self._is_authorized():
                self._send_unauthorized()
                return
            self._send_json_response({"status": "healthy"})
            return
        self.send_error(404, "Not Found")

    def _send_json_response(self, data):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _execute_python(self, code: str) -> Dict[str, Any]:
        if "def run" not in code:
            indented = "\n".join([f"    {line}" for line in code.splitlines()])
            code = f"def run(context):\n{indented}\n"

        if not TaskManager.is_running():
            TaskManager.start()

        done = threading.Event()
        result_box = {"result": None, "error": None}

        def callback(data):
            try:
                result_box["result"] = execute_script_handler(data["code"])
            except Exception as ex:
                result_box["error"] = str(ex)
            finally:
                done.set()

        task_id = TaskManager.post("execute_script", callback, {"code": code})
        if not task_id:
            return {"ok": False, "error": "Failed to post task"}

        if not done.wait(30):
            return {"ok": False, "error": "Timeout while executing script"}

        if result_box["error"]:
            return {"ok": False, "error": result_box["error"]}

        if isinstance(result_box["result"], dict) and result_box["result"].get("isError"):
            return {
                "ok": False,
                "result": result_box["result"],
                "error": result_box["result"].get("message", "Script execution failed"),
            }

        return {"ok": True, "result": result_box["result"]}

    def log_message(self, format, *args):
        return


def start_mcp_server(
    host: str = 'localhost',
    port: int = 9100
) -> Tuple[Optional[ThreadedHTTPServer], Optional[threading.Thread]]:
    """Start minimal HTTP server with /mcp endpoint."""
    try:
        server_address = (host, port)

        http_server = ThreadedHTTPServer(server_address, MCPHandler)
        server_thread = threading.Thread(
            target=http_server.serve_forever,
            daemon=True,
            name=f"MCP-Server-{host}:{port}"
        )
        server_thread.start()
        return http_server, server_thread
    except Exception as exc:
        print(f"Failed to start MCP server: {str(exc)}")
        if app:
            app.log(f"Failed to start MCP server: {str(exc)}\n{traceback.format_exc()}")
        return None, None


def stop_mcp_server(http_server, server_thread, timeout=5):
    """Stop the MCP server."""
    try:
        if http_server:
            http_server.shutdown()
            http_server.server_close()

        if server_thread and server_thread.is_alive():
            server_thread.join(timeout=timeout)
            return not server_thread.is_alive()

        return True
    except Exception as exc:
        print(f"Error stopping MCP server: {str(exc)}")
        if app:
            app.log(f"Error stopping MCP server: {str(exc)}")
        return False


