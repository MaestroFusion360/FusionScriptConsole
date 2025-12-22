import json
import adsk.core
import os
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_palette_send'
CMD_NAME = 'Send to Palette'
CMD_Description = 'Send some information to the palette'
IS_PROMOTED = False

PALETTE_ID = config.sample_palette_id

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

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

    if command_control:
        command_control.deleteMe()

    if command_definition:
        command_definition.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

    inputs = args.command.commandInputs

    inputs.addTextBoxCommandInput('text_input', 'Text Message', 'Enter some text', 1, False)

    users_current_units = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString(f'1 {users_current_units}')
    inputs.addValueInput('value_input', 'Value Message', users_current_units, default_value)


def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs

    text_input: adsk.core.TextBoxCommandInput = inputs.itemById('text_input')
    value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    message_action = 'updateMessage'
    message_data = {
        'myValue': f'{value_input.value} cm',
        'myExpression': value_input.expression,
        'myText': text_input.formattedText
    }
    message_json = json.dumps(message_data)

    palette = ui.palettes.itemById(PALETTE_ID)
    palette.sendInfoToHTML(message_action, message_json)


def command_preview(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
