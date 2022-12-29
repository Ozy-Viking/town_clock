from enum import Enum, auto  # type: ignore
from typing import Literal  # type: ignore


class Diff(Enum):
    FAST = auto()
    SLOW = auto()
    ON_TIME = auto()


class Log_Level(Enum):
    """Log Levels:
    CRITICAL: 50
    ERROR: 40
    WARNING: 30
    INFO: 20
    DEBUG: 10
    NOTSET: 0
    """

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Mode(Enum):
    """Either Test or Active\n
    Mode.TEST\n
    Mode.ACTIVE
    """

    TEST = auto()
    ACTIVE = auto()


class Clock(Enum):
    """Clock Names
    A enum used for controling and altering the clock times independently.

    Args:
        Enum (String): Clock names.
    """

    ALL = 0
    ONE = 1
    TWO = 2

    @classmethod
    def values(cls) -> tuple[Literal[0], Literal[1], Literal[2]]:
        return 0, 1, 2


class PulseError(Exception):
    pass


class NoValidTimeFromFileError(Exception):
    pass


if __name__ == "__main__":
    print(Clock.ONE.value)
