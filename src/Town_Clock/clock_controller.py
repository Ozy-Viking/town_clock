import time
from logging import exception
from multiprocessing import Event, Process, Queue, current_process, active_children

import Town_Clock.clock_enums_exceptions as CEE
import Town_Clock.clock_input_screen as LCD
import Town_Clock.clock_logging as c_log
from Town_Clock.clock_data import ClockTime
from Town_Clock.clock_logging import Listener, Worker, log_queue
from Town_Clock.clock_mechanism import ClockTower
from Town_Clock.clock_enums_exceptions import PulseError

class Controller:
    def __init__(self, clock_pins, led_pin, common_pin, lat, long, alt) -> None:
        self.all_processes: dict(Process) = {}
        self.all_queues: dict(Queue) = {}
        self.all_events: dict(Event) = {}

        self.setup_logger = c_log.Setup_Log()
        self.listener = Listener()
        self.all_processes['listener_process'] = self.listener.lp
        self.listener.logger.log('critical','CLOCK POWERED ON')
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
        self.clock_time.logger.log('info','Clock 1 Data Started')
        
        self.position = {'latitude': lat, 'longitude': long, 'altitude': alt}
        self.clock_tower = ClockTower(clock_time = self.clock_time,
                                      clock_pins = (clock_pins), 
                                      led_pin = led_pin, 
                                      common_pin = common_pin,
                                      position = self.position)
        self.clock_tower.logger.log('info', 'Tower Started')

        for p in self.all_processes:
            if self.all_processes[p].is_alive(): continue
            self.all_processes[p].start()
        self.listener.logger.log('info', f'Alive Processes: {active_children()}')
        self.input_diff = 0


    def main(self):
        time.sleep(0.1)
        while True:
            try:
                if self.all_events['input_event'].is_set():
                    clk, self.input_diff = self.all_queues['input_queue'].get() # Tuple
                    if self.input_diff != 0:
                        self.clock_time.change_clock_time(dt = self.input_diff, clk = clk)
                    self.input_diff = 0
                    self.all_events['input_event'].clear()
                
                tm = time.time()
                if int(tm%self.clock_time.freq_pulse) == 0:
                    tp_0 = time.time()

                    self.clock_time.logger.log('debug',f'{tm = }')
                    self.clock_time.current_time = tm
                    try:
                        self.clock_time.diff, self.clock_time.diff_secs = self.clock_time.clock_time_diff()
                    except ValueError as error:
                        self.listener.logger.log('error',f'clock_time_diff: {error}')
                    
                    clock_pulses = []
                    if self.clock_time.diff == [0, 0]: continue
                    else:
                        for c_diff in self.clock_time.diff:
                            if c_diff >= 0:
                                clock_pulses.append(0)
                            else:
                                clock_pulses.append(abs(c_diff))

                        self.clock_tower.pulse(ct = self.clock_time, clock_pulses = clock_pulses)
                        
                    self.clock_time.logger.log('info',f'Loop Clocktime: {self.clock_time}')
                    tp_1 = time.time()
                    self.listener.logger.log('info',f'Time Taken: {(tp_1-tp_0)*1000-1000:.2f} ms')

                    time.sleep(1.0001)

                    self.clock_tower.check_if_night(tm)
                
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
