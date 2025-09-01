from typing import Callable

from dataclasses import dataclass

from enum import Enum


TaskFunction = Callable[[], None]


class TaskInterval(int, Enum):
    THIRTY_SECONDS = 30
    SIXTY_SECONDS = 60


class SonicDb(str, Enum):
    """
    The Various SONiC Redis databases that exist.
    """

    STATE_DB = "STATE_DB"
    COUNTERS_DB = "COUNTERS_DB"
    ASIC_DB = "ASIC_DB"
    APPL_DB = "APPL_DB"
    CONFIG_DB = "CONFIG_DB"


@dataclass
class Task:
    """
    The callable and the interval at which it should run.
    """

    func: TaskFunction
    interval: TaskInterval
