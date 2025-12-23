"""MCP server lifecycle helpers."""

from typing import Tuple

from .mcp_server import start_mcp_server, stop_mcp_server
from .task_manager import TaskManager

HOST = "127.0.0.1"
PORT = 9100

_server = None
_thread = None


def is_server_running() -> bool:
    return _server is not None and _thread is not None and _thread.is_alive()


def get_server_url() -> str:
    return f"http://{HOST}:{PORT}"


def start_server() -> Tuple[bool, str]:
    global _server, _thread
    if is_server_running():
        return True, f"Fusion MCP server is already running at {get_server_url()}"

    if not TaskManager.is_running():
        TaskManager.start()

    _server, _thread = start_mcp_server(host=HOST, port=PORT)
    if _server:
        return True, f"Fusion MCP server started at {get_server_url()}"

    _server = None
    _thread = None
    return False, "Failed to start Fusion MCP server."


def stop_server() -> Tuple[bool, str]:
    global _server, _thread
    if not _server and not _thread:
        return True, "Fusion MCP server is not running."

    ok = stop_mcp_server(_server, _thread)
    TaskManager.stop()
    _server = None
    _thread = None

    if ok:
        return True, "Fusion MCP server stopped."
    return False, "Error stopping Fusion MCP server."
