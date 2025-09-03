from metronome.tasks.free_memory import task_set_free_memory
from metronome.tasks.errors_per_second import task_set_errors_per_second
from metronome.tasks.cpu import task_set_cpu_usage

__all__ = [
    "task_set_free_memory",
    "task_set_errors_per_second",
    "task_set_cpu_usage",
]
