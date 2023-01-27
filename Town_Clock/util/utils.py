from enum import Enum, auto  # type: ignore
from typing import Literal  # type: ignore


class Diff(Enum):
    FAST = auto()
    SLOW = auto()
    ON_TIME = auto()


class Log_Level(Enum):
    """Log Levels:
    CRITICAL: 50
    EXCEPTION = 40
    ERROR: 40
    WARNING: 30
    INFO: 20
    DEBUG: 10
    NOTSET: 0
    """

    CRITICAL = 50
    ERROR = 40
    EXCEPTION = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Mode(Enum):
    """Either Test or Active\n
    DEV = 'dev'
    TEST = 'test'
    ACTIVE = 'active'
    """

    DEV = "dev"
    TEST = "test"
    ACTIVE = "active"


class CLOCK(Enum):
    """CLOCK Names
    A enum used for controlling and altering the clock times independently.
    todo: Use enum with objects..
    """

    ALL = 0
    ONE = 1
    TWO = 2

    @classmethod
    def values(cls) -> tuple[Literal[0], Literal[1], Literal[2]]:
        return 0, 1, 2


# todo: Add logging to exceptions themselves.
class ClockGroupError(ExceptionGroup):
    ...


class PulseError(Exception):
    ...


class NoValidTimeFromFileError(Exception):
    ...


def convert_position_string_to_number(position_str: str) -> float:
    """
    Converts a position string to a number.

    args:
        position_str: str: Position in the form of a string. eg "30.3402W"
    """
    if isinstance(position_str, int | float):
        return position_str
    elif not isinstance(position_str, str):
        raise TypeError()
    pos_list = list(position_str)
    direction: int = int()
    match pos_list.pop().upper():
        case "N" | "E":
            direction = 1
        case "S" | "W":
            direction = -1
    return float("".join(pos_list)) * direction
