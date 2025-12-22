"""
Fusion Add-in entry point.
"""

import traceback
import adsk.core
from .server.mcp_server import start_mcp_server, stop_mcp_server
from .server.task_manager import TaskManager

app = adsk.core.Application.get()
ui = app.userInterface
server = None
thread = None

HOST = 'localhost'
PORT = 9100


def run(context):
    """Called when add-in starts"""
    try:
        global server, thread
        TaskManager.start()
        server, thread = start_mcp_server(host=HOST, port=PORT)

        if not server:
            if ui:
                ui.messageBox("Failed to start Fusion MCP Add-in")
            if app:
                app.log("Failed to start Fusion MCP Add-in")
    except Exception:
        app.log(f'Failed to start Fusion MCP Add-in:\n{traceback.format_exc()}')


def stop(context):
    """Called when add-in stops"""
    try:
        TaskManager.stop()
        if stop_mcp_server(server, thread):
            if app:
                app.log("Fusion MCP Add-in stopped successfully.")
        else:
            if app:
                app.log("Error stopping Fusion MCP Add-in")
    except Exception:
        if app:
            app.log(f"Error stopping Fusion MCP Add-in:\n{traceback.format_exc()}")

