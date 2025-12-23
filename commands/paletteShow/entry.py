"""UI command to show the palette."""

import json
import adsk.core
import os
from lib import fusionAddInUtils as futil
import config
from datetime import datetime

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_PalleteShow'
CMD_NAME = 'Show My Palette'
CMD_Description = 'A Fusion Add-in Palette'
PALETTE_NAME = 'My Palette Sample'
IS_PROMOTED = False

# Palette settings
PALETTE_ID = config.sample_palette_id

PALETTE_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'html', 'index.html')
PALETTE_URL = PALETTE_URL.replace('\\', '/')
PALETTE_DOCKING = adsk.core.PaletteDockingStates.PaletteDockStateRight

# UI placement
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Icons
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Event handlers
local_handlers = []


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    futil.add_handler(cmd_def.commandCreated, command_created)

    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    control.isPromoted = IS_PROMOTED


def stop():
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    palette = ui.palettes.itemById(PALETTE_ID)

    if command_control:
        command_control.deleteMe()

    if command_definition:
        command_definition.deleteMe()

    if palette:
        palette.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{CMD_NAME}: Command created event.')

    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME}: Command execute event.')

    palettes = ui.palettes
    palette = palettes.itemById(PALETTE_ID)
    if palette is None:
        palette = palettes.add(
            id=PALETTE_ID,
            name=PALETTE_NAME,
            htmlFileURL=PALETTE_URL,
            isVisible=True,
            showCloseButton=True,
            isResizable=True,
            width=650,
            height=600,
            useNewWebBrowser=True
        )
        futil.add_handler(palette.closed, palette_closed)
        futil.add_handler(palette.navigatingURL, palette_navigating)
        futil.add_handler(palette.incomingFromHTML, palette_incoming)
        futil.log(f'{CMD_NAME}: Created a new palette: ID = {palette.id}, Name = {palette.name}')

    if palette.dockingState == adsk.core.PaletteDockingStates.PaletteDockStateFloating:
        palette.dockingState = PALETTE_DOCKING

    palette.isVisible = True


def palette_closed(args: adsk.core.UserInterfaceGeneralEventArgs):
    futil.log(f'{CMD_NAME}: Palette was closed.')


def palette_navigating(args: adsk.core.NavigationEventArgs):
    futil.log(f'{CMD_NAME}: Palette navigating event.')

    url = args.navigationURL

    log_msg = f"User is attempting to navigate to {url}\n"
    futil.log(log_msg, adsk.core.LogLevels.InfoLogLevel)

    if url.startswith("http"):
        args.launchExternally = True


def palette_incoming(html_args: adsk.core.HTMLEventArgs):
    futil.log(f'{CMD_NAME}: Palette incoming event.')

    message_data: dict = json.loads(html_args.data)
    message_action = html_args.action

    log_msg = f"Event received from {html_args.firingEvent.sender.name}\n"
    log_msg += f"Action: {message_action}\n"
    log_msg += f"Data: {message_data}"
    futil.log(log_msg, adsk.core.LogLevels.InfoLogLevel)

    if message_action == 'messageFromPalette':
        arg1 = message_data.get('arg1', 'arg1 not sent')
        arg2 = message_data.get('arg2', 'arg2 not sent')

        msg = 'An event has been fired from the html to Fusion with the following data:<br/>'
        msg += f'<b>Action</b>: {message_action}<br/><b>arg1</b>: {arg1}<br/><b>arg2</b>: {arg2}'               
        ui.messageBox(msg)

    now = datetime.now()
    currentTime = now.strftime('%H:%M:%S')
    html_args.returnData = f'OK - {currentTime}'


def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME}: Command destroy event.')

    global local_handlers
    local_handlers = []
