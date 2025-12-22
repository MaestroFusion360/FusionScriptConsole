import adsk.core


def run(context):
    app = adsk.core.Application.get()
    app.log(app.activeDocument.name)
    return app.activeDocument.name
