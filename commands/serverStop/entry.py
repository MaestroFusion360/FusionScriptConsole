import adsk.core
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from ...server.server_manager import stop_server, is_server_running

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_server_stop'
CMD_NAME = 'Stop Fusion Script Console'
CMD_Description = 'Stop Fusion MCP server'
IS_PROMOTED = False

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_panel'
PANEL_NAME = 'Fusion Script Console'
TAB_ID = 'SolidTab'
FALLBACK_PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

local_handlers = []


def _get_or_create_panel():
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    if panel:
        return panel
    try:
        panel = workspace.toolbarPanels.add(PANEL_ID, PANEL_NAME, TAB_ID)
        return panel
    except Exception:
        return workspace.toolbarPanels.itemById(FALLBACK_PANEL_ID)


def start():
    existing_def = ui.commandDefinitions.itemById(CMD_ID)
    if existing_def:
        existing_def.deleteMe()
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)

    panel = _get_or_create_panel()
    if not panel:
        return
    before_id = '' if panel.id == PANEL_ID else COMMAND_BESIDE_ID
    control = panel.controls.addCommand(cmd_def, before_id, False)
    control.isPromoted = IS_PROMOTED


def stop():
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    if not panel:
        return
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    if command_control:
        command_control.deleteMe()

    if command_definition:
        command_definition.deleteMe()

    if panel:
        panel.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    if not is_server_running():
        ui.messageBox('Fusion MCP server is not running.')
        return

    ok, message = stop_server()
    if ok:
        ui.messageBox(message)
    else:
        ui.messageBox(message)


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
