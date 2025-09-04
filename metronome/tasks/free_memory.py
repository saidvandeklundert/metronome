from typing import Optional
import subprocess
from dataclasses import dataclass

from metronome import APP_CONTEXT, TaskRegistry, TaskInterval

ROUND_PRECISION = 2


@dataclass
class Free:
    """
    Representation of the available memory on a Linux system.

    All values are in Megabytes.
    """

    total_memory: int
    used_memory: int
    free_memory: int
    shared: int
    buffer: int
    available: int
    swap_total: int
    swap_used: int
    swap_free: int

    @property
    def free_memory_percentage(self) -> float:
        """
        Returns the available memory as a percentage of the total memory
        """
        return round(self.free_memory / self.total_memory * 100, ROUND_PRECISION)


def parse_free(output: str) -> Free:
    """
    Parse the output of the 'free -m' command.
    This command outputs the amount of free and used physical and swap memory
     in the system, as well as the buffers and caches used by the kernel.
    admin@sdievpn-spine-1:~$ free -m
                   total        used        free      shared  buff/cache   available
    Mem:           15960        3634        9460          49        3256       12325
    Swap:              0           0           0
    """
    total_memory = -1
    used_memory = -1
    free_memory = -1
    shared = -1
    buffer = -1
    available = -1
    swap_total = -1
    swap_used = -1
    swap_free = -1
    for line in output.splitlines():
        chunks = line.split()
        if len(chunks) == 7 and chunks[0].startswith("Mem"):
            total_memory = int(chunks[1])
            used_memory = int(chunks[2])
            free_memory = int(chunks[3])
            shared = int(chunks[4])
            buffer = int(chunks[5])
            available = int(chunks[6])
        if len(chunks) == 4 and chunks[0].startswith("Swap"):
            swap_total = int(chunks[1])
            swap_used = int(chunks[2])
            swap_free = int(chunks[3])
    return Free(
        total_memory=total_memory,
        used_memory=used_memory,
        free_memory=free_memory,
        shared=shared,
        buffer=buffer,
        available=available,
        swap_total=swap_total,
        swap_used=swap_used,
        swap_free=swap_free,
    )


def get_memory_info() -> Optional[Free]:
    """
    Retrieve device memory information.
    """
    try:
        result = subprocess.run(["free", "-m"], capture_output=True, text=True)

        if result.returncode == 0:
            return parse_free(result.stdout)
        else:
            APP_CONTEXT.logger.log_error(f"Error running command: {result.stderr}")

    except Exception as e:
        APP_CONTEXT.logger.log_error(f"running and parsing 'free -m': {str(e)}")


@TaskRegistry.register(interval=TaskInterval.THIRTY_SECONDS)
def task_set_free_memory() -> None:
    """
    Retrieve the memory that is avaialble on the device and populate STATE_DB with
    this value.

    Expected runtime ~0.007 sec.
    """
    APP_CONTEXT.logger.log_warning("running task_set_free_memory")
    free = get_memory_info()
    if free is None:
        return
    APP_CONTEXT.custom_table.set(
        "MEMORY",
        [
            (
                "free_memory_percentage",
                str(round(free.free_memory_percentage, ROUND_PRECISION)),
            ),
            ("total_memory_mb", str(round(free.total_memory, ROUND_PRECISION))),
            ("used_memory_mb", str(round(free.used_memory, ROUND_PRECISION))),
            ("free_memory_mb", str(round(free.free_memory, ROUND_PRECISION))),
            ("available_memory_mb", str(round(free.available, ROUND_PRECISION))),
        ],
    )
