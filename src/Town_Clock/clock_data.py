import os
import time
import glob
from pandas import read_csv
from dataclasses import dataclass
from numpy import nan
import numpy as np

from Town_Clock.clock_enums_exceptions import Diff, Mode, Clock, PulseError, NoValidTimeFromFileError
from Town_Clock.clock_logging import Worker


@dataclass
class _ClockTime:
    name: str
    _clock_time: float = time.time()
    freq_pulse: int = 60
    diff_from_current_time: int = 0
    _clock_time_error = 0
    local_clock_time = time.localtime(_clock_time)
    asc_clock_time = time.asctime(local_clock_time)

    def __post_init__(self):
        self.logger = Worker(name=f'{self.name}', clock=None)
        self.logger.log('debug', repr(self))
        self.clock_time = self._clock_time

    def mod_freq(self, tm: float | int, freq: float = 0) -> float:
        """
        Mod Time to show clean minutes

        Args:
            tm (float): Input time in seconds.
            freq (float, optional): Frequency of pulses. Defaults to 0.

        Raises:
            ValueError: When a given variable is not a number.
            ValueError: When freq is less than 0.

        Returns:
            float: Seconds rounded to the nearest minute. Unless freq is set.
        """
        self.logger.log('debug', 'mod_freq')
        if type(tm) not in (float, int, np.float64):
            raise ValueError('Not a Number.')

        if freq > 0:
            mod_freq = freq
        elif freq == 0:
            mod_freq = self.freq_pulse
        else:
            raise ValueError('Number less than 0.')
        tm_mod = tm % self.freq_pulse

        match tm:
            case tm if tm_mod >= mod_freq / 2:
                return tm + (mod_freq - tm_mod)
            case tm if tm_mod < mod_freq / 2:
                return tm - tm_mod

    @property
    def clock_time(self) -> float:
        """
        Returns clock time

        Returns:
            float: Current clocktime as a float in seconds since epoch.
        """
        self.logger.log('debug', f'{self.name} getter: {self._clock_time}')
        return self._clock_time

    @clock_time.setter
    def clock_time(self, tm: float = time.time()) -> None:
        """
        Sets Clock Time

        Args:
            tm (float, optional): Seconds since epoch at last pulse. Defaults to time.time().

        Sets: 
            self._clock_time_error: Error in ms at last pulse.
            self._clock_time: Cleaned version of seconds since epoch at last pulse.
                            Using a mod_freq() to round to the closest minute
            self.local_clock_time: Converts clock time to structured time from the Time module.
            self.asc_clock_time: Convert clock time into an ascii string.
        """
        self.logger.log('debug', f'{self.name} setter: {tm}')
        self._clock_time_error = (tm % self.freq_pulse) * 1000
        self._clock_time = self.mod_freq(tm)
        self.local_clock_time = time.localtime(self._clock_time)
        self.asc_clock_time = time.asctime(self.local_clock_time)


@dataclass
class ClockTime:
    """
    Class for representing and managing time values.

    Raises:
        ValueError: Putting a non number in tm_mod.
        ValueError: When freq is less than 0.
        ValueError: When variable is not a number in clock_time_diff.

    Returns:
        folder_path: str
        mode: Mode = Mode.TEST
        _clock_time: float = time.time()
        _clock_time_error: float = 0.0
        _prog_start_time: float = time.localtime()
        current_time: float = time.time()
        diff: int = 0 
        diff_secs: float = 0.0
        diff_state: Diff = Diff.ON_TIME
        freq_pulse: int = 60
        GPS_Fix: bool = False
        local_clock_time: time.struct_time = time.localtime()
        asc_clock_time: str = time.asctime(local_clock_time)
        pulsed: bool = False
        sleep_time: float = 0.09
        logger = Worker(name = 'Time', clock = None)
    """

    folder_path: str
    mode: Mode = Mode.TEST
    _clock_time_error: float = 0.0
    _prog_start_time: time.struct_time = time.asctime()
    current_time: float = time.time()
    diff: list[int] = 0
    diff_secs: list[float] = 0
    diff_state: Diff = Diff.ON_TIME
    freq_pulse: int = 60
    GPS_Fix: bool = False
    pulsed: bool = False
    sleep_time: float = 0.09

    def __post_init__(self):
        self.logger = Worker(name='Clock Time', clock=None)
        self._clock_time: list[_ClockTime, _ClockTime] = [_ClockTime(name='Clock 1 Time'),
                                                          _ClockTime(name='Clock 2 Time')]
        self.full_path = self._get_full_path()
        self.clock_time = self._get_last_time_from_file()
        self.logger.log('debug', repr(self))

    def _get_full_path(self) -> str:
        self.logger.log('debug', '_get_full_path')
        folder_path = self.folder_path
        pulse_log = '*pulse.log'
        full_path = os.path.join(folder_path, pulse_log)
        path = glob.glob(full_path)
        if not path:
            self.logger.log('error', 'FAILED to get full path')
            self.logger.log('error', f'{path}')
        self.logger.log('debug', f'{path}')

        return path[0]

    def _get_last_time_from_file(self) -> list:
        self.logger.log('debug', '_get_last_time_from_file')
        try:
            data = read_csv(self.full_path, sep=';')

            if not data.size:
                raise NoValidTimeFromFileError
            
            logtime = data.tail(3)
            for i in range(2,-1,-1):
                if (float(logtime.iat[i,6]) > 0) and (float(logtime.iat[i,7]) > 0):
                    ct = [float(logtime.iat[i,6]), float(logtime.iat[i,7])]
                    self.logger.log('debug', f'Time from file: {ct}')
                    return ct
            raise NoValidTimeFromFileError('No valid time in last 3 logs.')
        
        except NoValidTimeFromFileError as e:
            self.logger.logger.error('Failed to access time from csv.')
            self.logger.logger.error(e)
            tm = self.mod_freq(time.time())
            return [tm, tm]

    def __str__(self):
        return (f'Pulse: {self.clock_asc_time[0]}, {self.clock_asc_time[1]}, ' 
                f'Error: {self._clock_time_error:.2f}ms')

    def __repr__(self) -> str:
        """Pandas DataFrame for Logging
        Returns a DataFrame containing data for logging.

        Returns:
            str: Structured dataframe for logging.
        """
        data = (f'{self.current_time:.1f};{self.clock_time[0]};{self.clock_time[1]};'
                f'{self.diff};{self.clock_asc_time};'
                f'{self.GPS_Fix}; Pulsed = {self.pulsed};{self._prog_start_time}')
        return data

    def mod_freq(self, tm: float | int, freq: float = 0) -> float:
        """
        Mod Time to show clean minutes in seconds.

        Args:
            tm (float): Input time in seconds.
            freq (float, optional): Frequency of pulses. Defaults to 0.

        Raises:
            ValueError: When a given variable is not a number.
            ValueError: When freq is less than 0.

        Returns:
            float: Seconds rounded to the nearest minute. Unless freq is set.
        """
        self.logger.log('debug', 'mod_freq')
        if type(tm) not in (float, int, np.float64):
            raise ValueError('Not a Number.')

        if freq > 0:
            mod_freq = freq
        elif freq == 0:
            mod_freq = self.freq_pulse
        else:
            raise ValueError('Number less than 0.')
        tm_mod = tm % self.freq_pulse

        match tm:
            case tm if tm_mod >= mod_freq / 2:
                return tm + (mod_freq - tm_mod)
            case tm if tm_mod < mod_freq / 2:
                return tm - tm_mod

    def clock_time_diff(self, tm1: list = None, tm2: float = None) -> list[list]:
        """Clock Time Delta
        Returns the difference between time 1 (clock_time) and last pulse(time 2).
        Positive means clock is fast.
        If the difference between the 2 times is greater than 12 hours 
        this will remove that difference (n*12) hours.

        param:
            clock: Clock Enum
            tm1 (list(float)): A list of float values in seconds since epoch.
            tm2 (float): A time in seconds since epoch.

        Raises:
            ValueError: When variable is not a number or list.

        Returns:
            list(int): Difference in minutes for each clock.
            list(int): Difference in seconds for each clock.
        """
        self.logger.log('debug', 'clock_time_diff')
        if not tm1:
            tm1 = self.clock_time
        elif type(tm1) not in (list, tuple):
            raise ValueError('tm1: Not a list or tuple.')
        for tm in tm1:
            if type(tm) not in (int, float):
                raise ValueError(f'Times in list not a number: {tm1}')

        if not tm2:
            tm2 = self.current_time
        elif type(tm2) not in (float, int):
            raise ValueError('tm2: Not a Number.')

        diff_secs = []
        for tm in tm1:
            diff_secs.append(tm - tm2)
        diff = [round(x / self.freq_pulse) for x in diff_secs]
        # print(diff)
        for idx, dt in enumerate(diff):
            if dt <= -(12 * self.freq_pulse) or dt >= (12 * self.freq_pulse):
                diff, diff_secs = self.larger_than_12_hours(diff, diff_secs, clock=idx + 1)
        # print(diff, (12 * self.freq_pulse))
        return [diff, diff_secs]

    def larger_than_12_hours(self, diff, diff_secs, clock):
        idx = clock - 1
        if diff[idx] <= -(12 * self.freq_pulse):
            while diff[idx] <= -(12 * self.freq_pulse):  # adds 12 hours
                self.logger.log('info', f'Larger than 12 hours: {diff} min')
                self.logger.log('debug', f'While Loop diff >= 12 hours: {diff} min or {diff_secs} secs')
                self.change_clock_time(12 * self.freq_pulse * 60, clock=clock)
                diff_secs[idx] += 12 * self.freq_pulse * 60
                diff[idx] += 12 * self.freq_pulse
        elif diff[idx] >= (12 * self.freq_pulse):
            while diff[idx] >= (12 * self.freq_pulse):  # Subtracts 12 hours
                self.logger.log('info', f'Larger than 12 hours: {diff} min')
                self.logger.log('debug', f'While Loop diff >= 12 hours: {diff} min or {diff_secs} secs')
                self.change_clock_time(-12 * self.freq_pulse * 60, clock=clock)
                diff_secs[idx] -= 12 * self.freq_pulse * 60
                diff[idx] -= 12 * self.freq_pulse
        
        return diff, diff_secs

    @property
    def clock_time(self) -> list:
        return [self._clock_time[0].clock_time,
                self._clock_time[1].clock_time]

    @clock_time.setter
    def clock_time(self, ct: list) -> None:
        self._clock_time[0].clock_time = ct[0]
        self._clock_time[1].clock_time = ct[1]

    @property
    def clock_local_time(self) -> list:
        return [self._clock_time[0].local_clock_time,
                self._clock_time[1].local_clock_time]

    @property
    def clock_asc_time(self) -> list:
        return [self._clock_time[0].asc_clock_time,
                self._clock_time[1].asc_clock_time]

    def change_clock_time(self, dt: int, clock: Clock | int = Clock.ALL) -> None:
        if clock in Clock.ALL.values:
            clock = Clock(int(clock))
        if type(clock) is not Clock:
            raise PulseError('Did not enter a valid Clock.')
        if clock == Clock.ALL:
            self._clock_time[0].clock_time = self._clock_time[0].clock_time + dt
            self._clock_time[1].clock_time = self._clock_time[1].clock_time + dt
        elif clock == Clock.ONE:
            self._clock_time[0].clock_time = self._clock_time[0].clock_time + dt
        elif clock == Clock.TWO:
            self._clock_time[1].clock_time = self._clock_time[1].clock_time + dt
        self.logger.log("debug", repr(self), name='Pulse')


if __name__ == '__main__':
    pass
