"""
Execute Fusion API Python scripts.
"""

import os
import re
import traceback
import adsk.core

app = adsk.core.Application.get()


def handler(script: str) -> dict:
    """
    Execute Fusion API Python script source code.

    The script must define a run(context) function.
    Output is collected from log()/print() and optional return value.
    """
    run_function_match = re.search(r'def\s+run\s*\(\s*(\w+)\s*\):', script)
    if not run_function_match:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Script does not have a run function that takes a single argument"
                }
            ],
            "isError": True,
            "message": "Script does not have a run function that takes a single argument",
        }


    try:
        debug_path = os.path.join(os.path.dirname(__file__), "last_script.py")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(script)
    except Exception:
        pass
    try:
        output_lines = []

        def log(message):
            text = str(message)
            output_lines.append(text)
            try:
                app.log(text, adsk.core.LogLevels.InfoLogLevel, adsk.core.LogTypes.ConsoleLogType)
            except Exception:
                pass

        class _AppProxy:
            def __init__(self, inner):
                self._inner = inner

            def __getattr__(self, name):
                return getattr(self._inner, name)

            def log(self, message, level=adsk.core.LogLevels.InfoLogLevel, log_type=adsk.core.LogTypes.ConsoleLogType):
                text = str(message)
                output_lines.append(text)
                try:
                    return self._inner.log(message, level, log_type)
                except Exception:
                    return None

        proxy_app = _AppProxy(app)
        try:
            adsk.core.Application.get = staticmethod(lambda: proxy_app)
        except Exception:
            pass

        scope = {
            "adsk": adsk,
            "app": proxy_app,
            "ui": proxy_app.userInterface,
            "log": log,
            "print": log,
        }

        exec(script, scope, scope)
        run_func = scope.get("run")
        result_value = None
        if callable(run_func):
            result_value = run_func(None)

        output = "\n".join(output_lines).strip()
        if not output and result_value is not None:
            output = str(result_value)
            try:
                app.log(output, adsk.core.LogLevels.InfoLogLevel, adsk.core.LogTypes.ConsoleLogType)
            except Exception:
                pass

        result = {
            "isError": False,
            "message": "Script executed successfully",
            "output": output,
            "value": result_value,
        }
        if output:
            result["content"] = [
                {
                    "type": "text",
                    "text": output
                }
            ]
        return result
    except Exception as exc:
        res = traceback.format_exc()
        try:
            app.log(res, adsk.core.LogLevels.ErrorLogLevel, adsk.core.LogTypes.ConsoleLogType)
        except Exception:
            pass
        return {
            "content": [
                {
                    "type": "text",
                    "text": res
                }
            ],
            "isError": True,
            "message": "Script execution failed"
        }


