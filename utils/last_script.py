import adsk.core
import adsk.fusion
import traceback
import tempfile
import os


def log(app, text=''):
    app.log(str(text))


def run(context):
    app = adsk.core.Application.get()

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            log(app, 'ERROR: Design document is not active.')
            return

        root = design.rootComponent
        lines = [
            f'Root component: {root.name}',
            '',
        ]

        occs = root.allOccurrences
        lines.append(f'Occurrences: {occs.count}')

        for i in range(occs.count):
            occ = occs.item(i)
            comp = occ.component
            lines.append(
                f'{i + 1:03d}. occ="{occ.name}" | comp="{comp.name}" | bodies={comp.bRepBodies.count}'
            )

        lines.append('')
        lines.append(f'Root bodies: {root.bRepBodies.count}')

        for i in range(root.bRepBodies.count):
            body = root.bRepBodies.item(i)
            lines.append(f'  {i + 1:03d}. {body.name}')

        text = '\n'.join(lines)
        out_path = os.path.join(tempfile.gettempdir(), 'fusion_component_report.txt')

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)

        log(app, '=== Fusion Component Report ===')
        log(app, text)
        log(app, '')
        log(app, f'Saved to: {out_path}')

    except:
        log(app, 'ERROR:')
        log(app, traceback.format_exc())