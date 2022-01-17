import time
from logging import exception
from multiprocessing import Event, Process, Queue, current_process

import i2c_LCD.I2CLCD1602 as LCD

import Town_Clock.clock_enums_exceptions as CEE
import Town_Clock.clock_logging as c_log
from Town_Clock.clock_data import ClockTime
from Town_Clock.clock_logging import Listener, Worker, log_queue
from Town_Clock.clock_mechanism import ClockTower
from Town_Clock.location_sunrise_sunset import find_sunrise_sunset_times, timezone_finder


class Controller:
    def __init__(self, clock_1_pin, clock_2_pin, led_pin, lat, long, alt) -> None:
        self.all_processes: dict(Process) = {}
        self.all_queues: dict(Queue) = {}
        self.all_events: dict(Event) = {}

        self.setup_logger = c_log.Setup_Log()
        self.listener = Listener()
        self.all_processes['listener_process'] = self.listener.lp
        self.listener.logger.log('info','Listener Started')
        self.all_queues['log_queue'] = log_queue

        self.all_queues['clock_data_queue'] = Queue()
        self.all_events['clock_data_event'] = Event()

        self.all_queues['input_queue'] = Queue()
        self.all_events['input_event'] = Event()
        self.all_processes['input_process'] = Process(target = LCD.main,
                                                      name = 'Screen',
                                                      args = (self.all_queues['input_queue'], 
                                                              self.all_events['input_event'],
                                                              Worker('LCD', None)
                                                             ),
                                                      daemon = False
                                                     )

        self.clock_time = ClockTime(freq_pulse = 60, 
                                    folder_path = self.setup_logger.folder_path)
        self.clock_time.logger.log('info','Clock Data Started')

        self.clock_tower = ClockTower(clock_pins = (clock_1_pin, clock_2_pin), led_pin = led_pin)
        self.clock_tower.logger.log('info', 'Tower Started')
        
        self.position = {'latitude': lat, 'longitude': long, 'altitude': alt}
        self.next_sunset_sunrise_times = find_sunrise_sunset_times(**self.position)
        for t in self.next_sunset_sunrise_times:
            self.next_sunset_sunrise_times[t] = self.clock_time.mod_freq(self.next_sunset_sunrise_times[t])
        print(self.next_sunset_sunrise_times)
        self.timezone = timezone_finder(**self.position)
        self.clock_tower.logger.log('info', f'{self.timezone}, {self.next_sunset_sunrise_times}')

        for p in self.all_processes:
            if self.all_processes[p].is_alive(): continue
            self.all_processes[p].start()


    def main(self):
        time.sleep(0.1)
        while True:
            try:
                if self.all_events['input_event'].is_set():
                    input_diff = self.all_queues['input_queue'].get()

                tm = time.time()
                if int(tm%self.clock_time.freq_pulse) == 0:
                    tp_0 = time.perf_counter()

                    self.clock_time.logger.log('debug',f'{tm}')
                    self.clock_time.current_time = tm
                    self.clock_tower.pulse(self.clock_time, clock = CEE.Clock.ALL)

                    self.clock_time.logger.log('info',f'Loop Clocktime: {self.clock_time}')
                    tp_1 = time.perf_counter()
                    self.clock_tower.check_time_accuracy(clocktime = self.clock_time, clock = CEE.Clock.ALL)
                    self.listener.logger.log('info',f'Time Taken: {(tp_1-tp_0)*1000-1000:.2f} ms')
                    
                    
                    
                    time.sleep(1.0001)
                    
                    # Fetching next local sunset and sunrise at midday.
                    if not self.clock_time.local_clock_time.tm_min == 0: continue
                    elif self.clock_time.local_clock_time.tm_hour == 12:
                        self.next_sunset_sunrise_times = find_sunrise_sunset_times(**self.position)
                        for t in self.next_sunset_sunrise_times:
                            self.next_sunset_sunrise_times[t] = self.clock_time.mod_freq(self.next_sunset_sunrise_times[t])
                        print(self.next_sunset_sunrise_times)
                
                time.sleep(0.009)


            except KeyboardInterrupt:
                self.destroy()
            except Exception as e:
                self.listener.logger.log('error', e)

    def destroy(self) -> exit:
        self.listener.logger.log('critical', 'Progam being destroyed')
        self.listener.stop_event.set()
        for p in self.all_processes:
            self.all_processes[p].join()
        for q in self.all_queues:
            self.all_queues[q].close()

        print('\nbye....')
        exit(0)
