from pathlib import Path
import pkgutil
from sonic_py_common import logger
import importlib

from metronome.models import TaskInterval, TaskFunction
from metronome.task_registry import TaskRegistry
from metronome.application_context import APP_CONTEXT
from metronome.engine import Engine

LOGGER = logger.Logger("METRONOME")


def _import_all_tasks():
    """Dynamically import all tasks to ensure they are registered."""
    current_dir = Path(__file__).parent
    for _, name, ispkg in pkgutil.iter_modules([str(current_dir)]):
        if ispkg:
            try:
                module = importlib.import_module(f".{name}", package=__name__)
                if hasattr(module, "__all__"):
                    for attr_name in module.__all__:
                        globals()[attr_name] = getattr(module, attr_name)
                else:
                    for attr_name in dir(module):
                        if not attr_name.startswith("_"):
                            globals()[attr_name] = getattr(module, attr_name)
            except ImportError as e:
                msg = f"Failed to import task {name}: {e}"
                LOGGER.log_error(msg)


# Automatically import all tasks
_import_all_tasks()


__all__ = [
    "APP_CONTEXT",
    "TaskRegistry",
    "TaskInterval",
    "TaskFunction",
    "Engine",
    "ApplicationContext",
]
