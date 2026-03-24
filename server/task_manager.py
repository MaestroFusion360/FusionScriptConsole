"""Custom event task manager for Fusion 360."""

import json
import uuid
from typing import Dict, Callable, Any, Optional

try:
    import adsk.core
    app = adsk.core.Application.get()
except ImportError:
    app = None


def _log_error(message: str) -> None:
    if not app:
        return
    try:
        app.log(
            message,
            adsk.core.LogLevels.ErrorLogLevel,
            adsk.core.LogTypes.ConsoleLogType
        )
    except Exception:
        pass


class TaskManager:
    """Singleton for posting tasks via custom events."""

    _instance = None
    _event_handler = None
    _custom_event = None
    _pending_tasks: Dict[str, Dict[str, Any]] = {}
    _is_running = False

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the TaskManager."""
        if not hasattr(self, '_initialized'):
            self._event_handler = None
            self._custom_event = None
            self._pending_tasks = {}
            self._is_running = False
            self._initialized = True

    @classmethod
    def start(cls) -> bool:
        """Register the custom event and handler."""
        if not app:
            return False

        if cls._is_running:
            return True

        try:
            cls._custom_event = app.registerCustomEvent('Fusion API Server Addin.TaskManagerEvent')
            cls._event_handler = TaskEventHandler(cls._pending_tasks)
            cls._custom_event.add(cls._event_handler)

            cls._is_running = True
            return True

        except Exception as exc:
            _log_error(f"TaskManager.start() failed: {exc}")
            return False

    @classmethod
    def stop(cls) -> bool:
        """Remove the custom event handler."""
        if not cls._is_running:
            return True

        try:
            if cls._custom_event and cls._event_handler:
                cls._custom_event.remove(cls._event_handler)
                cls._event_handler = None
                cls._custom_event = None

            cls._pending_tasks.clear()
            cls._is_running = False
            return True

        except Exception as exc:
            _log_error(f"TaskManager.stop() failed: {exc}")
            return False

    @classmethod
    def post(cls, command: str, callback: Callable[[Dict[str, Any]], None], data: Dict[str, Any]) -> Optional[str]:
        """Post a task and return its id."""
        if not cls._is_running:
            return None

        if not callable(callback):
            return None

        try:
            task_id = str(uuid.uuid4())
            cls._pending_tasks[task_id] = {
                'command': command,
                'callback': callback,
                'data': data
            }

            event_data = {
                'task_id': task_id,
                'command': command,
                'data': data
            }

            app.fireCustomEvent(cls._custom_event.eventId, json.dumps(event_data))
            return task_id

        except Exception as exc:
            _log_error(f"TaskManager.post() failed: {exc}")
            return None

    @classmethod
    def is_running(cls) -> bool:
        """Return True when the event handler is active."""
        return cls._is_running

    @classmethod
    def get_pending_task_count(cls) -> int:
        """Return the pending task count."""
        return len(cls._pending_tasks)


class TaskEventHandler(adsk.core.CustomEventHandler):
    """Custom event handler for TaskManager tasks."""

    def __init__(self, pending_tasks: Dict[str, Dict[str, Any]]):
        super().__init__()
        self._pending_tasks = pending_tasks

    def notify(self, args: adsk.core.CustomEventArgs):
        """Dispatch the task callback."""
        try:
            event_data = json.loads(args.additionalInfo)
            task_id = event_data.get('task_id')
            data = event_data.get('data', {})

            if not task_id or task_id not in self._pending_tasks:
                return

            task_info = self._pending_tasks[task_id]
            callback = task_info['callback']

            try:
                callback(data)
            except Exception as exc:
                _log_error(f"TaskEventHandler callback failed: {exc}")

            del self._pending_tasks[task_id]

        except json.JSONDecodeError as exc:
            _log_error(f"TaskEventHandler JSON decode error: {exc}")
        except Exception as exc:
            _log_error(f"TaskEventHandler notify failed: {exc}")


def start_task_manager() -> bool:
    """Start the TaskManager."""
    return TaskManager.start()


def stop_task_manager() -> bool:
    """Stop the TaskManager."""
    return TaskManager.stop()
