import time
import os
import pandas as pd
from collections import namedtuple
# import asyncio
from Town_Clock.Relay import ClockPulse
from Town_Clock.GPS import set_system_time


class ClockTime:    
    def __init__(self) -> None:
        self.current_time = time.localtime()
        self.current_epoch_secs = time.time()
        self.diff = 0
        self.full_path = self._get_or_create_output_folder()
        self.current_clocktime = self._get_last_time_from_file() # In epoch seconds
        self.ensure_stored_clocktime_is_rounded(self.current_clocktime)
        if self._time_diff(): self.change_time()

    # Log Storage
    def _get_or_create_output_folder(self) -> str:
        folder = 'clock_log'
        name = 'log'
        base_folder = os.path.dirname(__file__)
        folder_path = os.path.join(base_folder,folder)
        full_path = os.path.join(base_folder, folder, name + '.csv')
        if not os.path.exists(folder_path):    
            print(f'Creating new directory at {folder_path}')
            os.mkdir(folder_path)
        if not os.path.exists(full_path):
            print(f'Creating new file at {full_path}')
            self.current_clocktime = time.time()
            skeleton = pd.DataFrame(self._df_structure())
            skeleton.to_csv(full_path, index=False)
        return full_path

    def _get_last_time_from_file(self) -> float:
        data = pd.read_csv(self.full_path)
        try:
            clock_time = data.tail(1).get('Epoch').iat[0]
            return clock_time
        except Exception as e:
            print('failed to access time from csv')
            print(e)
            return time.time()

    def _df_structure(self) -> dict:
        ctime = self.current_time
        return {'String':[time.asctime(ctime)], 'Epoch': self.current_clocktime,
                'Error':self.current_epoch_secs%60, 'Time':[ctime],
                'Difference':[self.diff], 'DST':[ctime.tm_isdst]}
        
    def save_time(self) -> None:
        df = pd.DataFrame(self._df_structure())
        # df = df.append(pd.read_csv(self.full_path,index_col='ID'), ignore_index=True)
        df.to_csv(self.full_path, mode='a', index=False, header=False)
    
    # ----- main function --------
    def store_current_time(self, time: time.struct_time, secs: float) -> None:
        # use system time then set system time to gps time during the minute.
        self.diff = 0
        self.current_time = time # time.localtime()
        self.current_epoch_secs = secs # time.time()
        self.diff = self._diff_time(self.current_epoch_secs) 
        if self.diff: 
            print('Change the clock')
            self.change_time()   
        self.save_time()
        
    def set_current_time_on_clock(self, time: float) -> None:
        # TODO: move all clocktimes here
        self.current_clocktime = time
    
    def _time_diff(self) -> bool:
        # Compare current time to last time. TODO: GPS Time?
        self._gps_time_fetch()
        if self.gps_time: 
            self._diff_time(self.gps_time) 
            return True
        elif self.current_time: 
            print('GPS Time not available....')
            self._diff_time(time.mktime(self.current_time)) 
            return True
        return False

    def _diff_time(self, tm: float) -> None:
        if not tm:
            tm=time.time()
        self.diff_secs = self.current_clocktime - tm
        self.diff = round(self.diff_secs/60)
        while self.diff <= -720: # adds 12 hours
            self.diff_secs += 43200
            self.diff += 720
            self.current_clocktime += 43200
        
    def pulse(self) -> None:
        relay.pulse()
        self.current_clocktime += 60 # TODO: set to 60 seconds when done.
        ct = self.current_clocktime
        print(f'Pulse: {time.asctime(time.localtime(ct))} Epoch:{self.current_epoch_secs}'
            f' Error:{round(self.current_epoch_secs%60*1000)} ms Actual: {time.asctime()}\n')
        self.current_clocktime = self.ensure_stored_clocktime_is_rounded(ct)

    @staticmethod
    def ensure_stored_clocktime_is_rounded(ct: float) -> float:
        ctmod60 = (ct % 60)
        match ct:
            case ct if ctmod60 < 30: ct = ct - ctmod60
            case ct if ctmod60 >= 30: ct = ct + (60 - ctmod60)
        return ct

    def change_time(self) -> None:
        if self.diff > 0:       # Fast
            print("fast")
            self.fast()
        elif self.diff < 0:     # Slow
            print("slow")
            self.slow()
        print('Check system time')
        self.check_system_time()
    
    def fast(self) -> None:
        print(f'Sleep for {self.diff_secs} seconds')
        time.sleep(abs(self.diff_secs))
    
    def slow(self) -> None:
        print(f'Pulse: {abs(self.diff)} times')
        for _ in range(abs(self.diff)):
            self.pulse()
            # pulse()
            time.sleep(1)

    def check_system_time(self) -> None:
        if self._gps_time_fetch('sys'):
            print(f' System time now: {time.asctime()}')
            self.gps_diff = 0
    
    def _gps_time_fetch(self, clock:str='town') -> bool|float:
        """GPS Time
        Currently generator error to test whether clock can adjust
        TODO: set system time from gps time.
        """
        if clock == 'town':
            self.gps_time = None # Simulating no gps signal.
        elif clock == 'sys':
            set_system_time()


def main() -> None:
    while True:
        try:
            ct0 = time.time()
            ct = time.localtime(ct0)
            if ct.tm_sec % 60 == 0:
                clock_time.pulse()
                time.sleep(1.1)
                t0=time.time()
                clock_time.store_current_time(ct,ct0)
                t1=time.time()
                print(f'done in {round(t1-t0, 4)} secs')
                print()
            time.sleep(0.0001)
        except KeyboardInterrupt:
            print('bye...')
            relay.destroy()
            exit(0)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    Pins = [35, 36]
    relay = ClockPulse(Pins)
    clock_time = ClockTime()
    main()
