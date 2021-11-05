import time
import pytest
from Town_Clock.program import ClockTime


def test_ensure_stored_clocktime_is_rounded():
    assert ClockTime.ensure_stored_clocktime_is_rounded(61) is 60
    assert ClockTime.ensure_stored_clocktime_is_rounded(35) is 60
    assert ClockTime.ensure_stored_clocktime_is_rounded(0) is 0
    
    