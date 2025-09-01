from typing import Dict, Callable
from metronome.models import Task, TaskInterval


class TaskRegistry:
    """
    Registy of tasks.
    """

    tasks: Dict[str, Task] = {}

    @classmethod
    def register(cls, interval: TaskInterval):
        """
        Register target task to run at specified interval.
        """

        def decorator(func: Callable):
            cls.tasks[func.__name__] = Task(func, interval)
            return func

        return decorator
