"""
Fusion Add-in entry point.
"""

import os
import sys
import traceback
import adsk.core

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

import commands
from server.server_manager import start_server, stop_server

app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    """Called when add-in starts"""
    try:
        commands.start()
        ok, message = start_server()
        if not ok:
            if ui:
                ui.messageBox(message)
            if app:
                app.log(message)
    except Exception:
        app.log(f'Failed to start Fusion MCP Add-in:\n{traceback.format_exc()}')


def stop(context):
    """Called when add-in stops"""
    try:
        commands.stop()
        ok, message = stop_server()
        if app:
            app.log(message if ok else f"Error stopping Fusion MCP Add-in: {message}")
    except Exception:
        if app:
            app.log(f"Error stopping Fusion MCP Add-in:\n{traceback.format_exc()}")
