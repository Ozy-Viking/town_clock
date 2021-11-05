import time
import os
import pandas as pd
# import asyncio


class ClockTime:
    """Main Class
    TODO: work out the actual effect or rounding. 
    
    """
    
    def __init__(self):
        self.current_time = time.localtime()
        self.epoch_secs = time.time()
        self.diff = 0
        self.current_clocktime = time.time()
        self.full_path = self._get_or_create_output_folder()
        self.current_clocktime = self._get_last_time_from_file() # In epoch seconds
        if self._time_diff(): self.change_time()
    
    # Log Storage
    def _get_or_create_output_folder(self):
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
            skeleton = pd.DataFrame(self._df_structure())
            skeleton.to_csv(full_path, index=False)
        return full_path
    
    def _get_last_time_from_file(self):
        data = pd.read_csv(self.full_path)
        try:
            clock_time = data.loc[data.shape[0]-1,'Epoch']
            return clock_time
        except Exception as e:
            print('failed to access time from csv')
            print(e)
            return time.time()
    
    def _df_structure(self):
        ctime = self.current_clocktime
        return {'Current_Epoch': self.epoch_secs, 'Clocktime':[time.asctime(time.localtime(ctime))], 
                'Epoch': self.epoch_secs, 'Time':ctime, 
                'Difference':[self.diff], 'DST':[time.localtime(ctime).tm_isdst]}
        
    def save_time(self):
        df = pd.DataFrame(self._df_structure())
        df.to_csv(self.full_path, mode='a', index=False, header=False)
    
    # ----- main function --------
    def store_current_time(self, time, secs):
        self._gps_time_fetch()
        self.diff = 0
        self.current_time = time
        self.epoch_secs = secs
        self.diff = self._diff_time(self.gps_time) # Assumption that this will occur close to the minute.
        self.save_time()
        if not (self.diff == 0): 
            self.change_time()   
        
    def current_time_on_clock(self, time):
        self._diff_time(time)
        self.current_clocktime = time
    
    def _time_diff(self):
        # Compare current time to last time.
        self._gps_time_fetch()
        if self.gps_time: 
            self._diff_time(self.gps_time) 
            return True
        elif self.current_time: 
            print('GPS Time not available....')
            self._diff_time(time.mktime(self.current_time)) 
            return True
        return False

    def _diff_time(self, time):
        self.diff_secs = self.current_clocktime - time
        self.diff = round(self.diff_secs/60)
        while self.diff <= -720: # adds 12 hours for long off periods (date doesn't matter)
            self.diff_secs += 43200
            self.diff += 720
            self.current_clocktime += 43200
    
    def _gps_time_fetch(self, clock='town'):
        """GPS Time
        Currently generator error to test whether clock can adjust
        TODO: set system time from gps time.
        """
        if clock == 'town':
            self.gps_time = time.time()
        elif clock == 'sys':
            diff = time.time() - time.time()
            return bool(diff)
        
    def pulse(self):
        self.current_clocktime += 60
        ct = self.current_clocktime
        print(f'Pulse: {time.asctime(time.localtime(ct))} Clocktime(secs):{ct} Actual: {time.asctime()}\n')
        self.save_time()

    def change_time(self):
        if not self.diff: pass 
        elif self.diff > 0:       # Fast
            print("fast")
            self.fast()
        elif self.diff < 0:     # Slow
            print("slow")
            self.slow()
        self.diff = 0
        self.check_system_time()
    
    def check_system_time(self):
        if self._gps_time_fetch('sys'):
            print(f'System time now: {time.asctime()}')
            self.gps_diff = 0
    
    def fast(self):
        print(f'Sleep for {self.diff_secs} seconds')
        time.sleep(abs(self.diff_secs))
    
    def slow(self):
        print(f'Pulse: {abs(self.diff)} times')
        for _ in range(abs(self.diff)):
            self.pulse()
            # pulse()
            time.sleep(1)


def main():
    # every minute (print time) on the minute.
    clock_time = ClockTime()
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
            exit(0)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
