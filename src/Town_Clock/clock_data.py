import os
import time
import glob
from pandas import DataFrame, read_csv
from dataclasses import dataclass
import numpy as np

from Town_Clock.clock_enums_exceptions import Diff, Mode
from Town_Clock.clock_logging import Worker, Listener

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

    def __post_init__ (self):
        self.logger = Worker(name = 'Clock Time', clock = None)
        self.full_path = self._get_full_path()
        self.clock_time = self._get_last_time_from_file()
        self.logger.log('debug', repr(self))

    def _get_full_path(self) -> str:
        self.logger.log('debug','_get_full_path')
        folder_path = self.folder_path
        pulse_log = '*pulse*'
        full_path = os.path.join(folder_path, pulse_log)
        path = glob.glob(full_path)
        if not path: 
            self.logger.log('error', 'FAILED to get full path')
            self.logger.log('error', f'{path}')
        self.logger.log('debug', f'{path}')
        
        return path[0]

    def _get_last_time_from_file(self) -> float:
        self.logger.log('debug','_get_last_time_from_file')
        try:
            data = read_csv(self.full_path, sep = ';')
            if not data.size: return time.time()//60
            ct = data.tail(1).iat[0, 6]
            return int(ct)
        except Exception as e:
            self.logger.logger.error('Failed to access time from csv.')
            self.logger.logger.error(e)
            return time.time()

    def __str__(self):
        return f'Pulse: {self.asc_clock_time}, Error: {self._clock_time_error:.2f}ms'

    def __repr__(self) -> DataFrame:
        """Pandas DataFrame for Logging
        Returns a DataFrame containing data for logging.
        KEEP ACCURATE WITH df_structure and __df_structure.

        Returns:
            DataFrame: Structured dataframe for logging.
        """
        data = (f'{self._prog_start_time};{self._clock_time};{self._clock_time_error};'
               f'{self.local_clock_time};{self.local_clock_time.tm_isdst};'
               f'{self.GPS_Fix};{self.pulsed}')
        return data


    def mod_freq(self, tm: float|int, freq: float=0) -> float:
        """
        Mod Time to show clean minutes

        Args:
            tm (float): Input time in seconds.
            freq (float, optional): Frequency of pulses. Defaults to 0.

        Raises:
            ValueError: When a given variable is not a number.
            ValueError: When freq is less than 0.

        Returns:
            float: Seconds rounded to to the nearest minute. Unless freq is set.
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
            case tm if tm_mod >= mod_freq/2: return tm + (mod_freq - tm_mod)
            case tm if tm_mod < mod_freq/2: return tm - tm_mod

    @property
    def clock_time(self) -> float:
        """
        Returns clock time

        Returns:
            float: Current clocktime as a float in seconds since epoch.
        """
        self.logger.log('debug', 'clock_time getter')
        return self._clock_time

    @clock_time.setter
    def clock_time(self, tm: float = time.time()) -> property:
        """
        Sets Clock Time

        Args:
            tm (float, optional): Seconds since epoch at last pulse. Defaults to time.time().

        Sets: 
            self._clock_time_error: Error in ms at last pulse.
            self._clock_time: Cleaned version of seconds since epoch at last pulse.
                            Using a mod_freq() to round to closest minute
            self.local_clock_time: Converts clock time to structured time from the Time module.
            self.asc_clock_time: Converst clock time into an ascii string.
        """
        self.logger.log('debug', 'clock_time setter')
        self._clock_time_error = (tm%self.freq_pulse)*1000
        self._clock_time = self.mod_freq(tm)
        self.local_clock_time = time.localtime(self._clock_time)
        self.asc_clock_time = time.asctime(self.local_clock_time)

    def clock_time_diff(self, tm1: float = None, tm2: float = None) -> tuple:
        """Clock Time Delta
        Returns the difference between time 1 (clock_time) and last pulse(time 2).
        Postive means clock is fast.
        If the difference between the 2 times is greater than 12 hours 
        this will remove that difference (n*12) hours.

        Args:
            tm1 (float): A time in seconds since epoch.
            tm2 (float): A time in seconds since epoch.

        Raises:
            ValueError: When variable is not a number.

        Returns:
            tuple(float, float): Diffence in minutes, diffence in seconds.
        """
        self.logger.log('debug', 'clock_time_diff')
        if not tm1:
            tm1 = self.clock_time
        elif type(tm1) not in (float, int):
            raise ValueError('tm1: Not a Number.')
        if not tm2:
            tm2 = self.current_time
        elif type(tm2) not in (float, int):
            raise ValueError('tm2: Not a Number.')

        diff_secs = tm1 - tm2
        diff = round(diff_secs/self.freq_pulse)

        while diff <= -720: # adds 12 hours
            diff_secs += 12*self.freq_pulse*60
            diff += 12*self.freq_pulse

        return diff, diff_secs


if __name__ == '__main__':
    listener = Listener()
    time.sleep(2)
    clock_time = ClockTime()
    clock_time.logger.log('info', 'Is it really working?')
