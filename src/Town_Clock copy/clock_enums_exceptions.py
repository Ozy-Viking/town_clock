from enum import Enum, auto

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
    ONE = 1
    TWO = 2
    ALL = 3

    # @property
    def values(self):
        return 1, 2, 3


class PulseError(Exception):
    pass
