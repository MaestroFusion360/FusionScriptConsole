"""
Task Manager Module

This module provides a TaskManager class for handling custom events and task execution
within the Fusion 360 environment.
"""

import json
import uuid
from typing import Dict, Callable, Any, Optional

try:
    import adsk.core
    app = adsk.core.Application.get()
except ImportError:
    app = None


class TaskManager:
    """
    TaskManager class for handling custom events and task execution.

    Provides a mechanism to post tasks with callbacks that will be executed
    when custom events are fired in the Fusion 360 environment.
    Acts as a singleton with class methods for global access.
    """

    _instance = None
    _event_handler = None
    _custom_event = None
    _pending_tasks: Dict[str, Dict[str, Any]] = {}
    _is_running = False

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the TaskManager (only called once due to singleton)."""
        if not hasattr(self, '_initialized'):
            self._event_handler = None
            self._custom_event = None
            self._pending_tasks = {}
            self._is_running = False
            self._initialized = True

    @classmethod
    def start(cls) -> bool:
        """
        Start the TaskManager by registering a custom event and handler.

        Returns:
            True if started successfully, False otherwise
        """
        if not app:
            return False

        if cls._is_running:
            return True

        try:
            cls._custom_event = app.registerCustomEvent('Fusion MCP Addin.TaskManagerEvent')
            cls._event_handler = TaskEventHandler(cls._pending_tasks)
            cls._custom_event.add(cls._event_handler)

            cls._is_running = True
            return True

        except Exception:
            return False

    @classmethod
    def stop(cls) -> bool:
        """
        Stop the TaskManager by removing the event handler.

        Returns:
            True if stopped successfully, False otherwise
        """
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

        except Exception:
            return False

    @classmethod
    def post(cls, command: str, callback: Callable[[Dict[str, Any]], None], data: Dict[str, Any]) -> Optional[str]:
        """
        Post a task with a callback to be executed when the custom event is fired.

        Args:
            command: Command string to identify the task type
            callback: Callable function to execute with the data
            data: Dictionary containing task data

        Returns:
            Task ID if posted successfully, None otherwise
        """
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

        except Exception:
            return None

    @classmethod
    def is_running(cls) -> bool:
        """Check if the TaskManager is currently running."""
        return cls._is_running

    @classmethod
    def get_pending_task_count(cls) -> int:
        """Get the number of pending tasks."""
        return len(cls._pending_tasks)


class TaskEventHandler(adsk.core.CustomEventHandler):
    """
    Event handler for TaskManager custom events.

    Handles the execution of callbacks when custom events are received.
    """

    def __init__(self, pending_tasks: Dict[str, Dict[str, Any]]):
        super().__init__()
        self._pending_tasks = pending_tasks

    def notify(self, args: adsk.core.CustomEventArgs):
        """Handle the custom event notification."""
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
            except Exception:
                pass

            del self._pending_tasks[task_id]

        except json.JSONDecodeError:
            pass
        except Exception:
            pass


def start_task_manager() -> bool:
    """Start the TaskManager singleton."""
    return TaskManager.start()


def stop_task_manager() -> bool:
    """Stop the TaskManager singleton."""
    return TaskManager.stop()
