import asyncio
from collections import defaultdict
from metronome.task_registry import TaskRegistry
from metronome.application_context import APP_CONTEXT


class Engine:
    """
    Batches and runs all tasks from the given TaskRegistry.
    """

    __slots__ = ("task_groups",)

    def __init__(self, registry: TaskRegistry):

        self.task_groups = defaultdict(list)
        for task in registry.tasks.values():
            self.task_groups[task.interval].append(task.func)

    async def run(self):
        """
        Run all the tasks that have been registered in the TaskRegistry.
        """

        await asyncio.gather(
            *[
                self._run(interval, funcs)
                for interval, funcs in self.task_groups.items()
            ]
        )

    async def _run(self, interval, funcs):
        """ """

        while True:
            await asyncio.gather(
                *[self._safe_run(func) for func in funcs], return_exceptions=True
            )
            await asyncio.sleep(interval)

    async def _safe_run(self, func):
        """
        Safely execute target function.
        """
        APP_CONTEXT.logger.log_info(f"{func.__name__} started")
        try:
            await asyncio.to_thread(func)
        except Exception as e:
            APP_CONTEXT.logger.log_error(f"{func.__name__} failed: {e}")
