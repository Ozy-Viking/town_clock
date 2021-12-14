import time
from logging import exception
from multiprocessing import Event, Process, Queue, current_process

import i2c_LCD.I2CLCD1602 as LCD

import Town_Clock.clock_enums_exceptions as CEE
import Town_Clock.clock_logging as c_log
from Town_Clock.clock_data import ClockTime
from Town_Clock.clock_logging import Listener, Worker, log_queue
from Town_Clock.clock_mechanism import ClockTower


class Controller:
    def __init__(self, clock_1_pin, clock_2_pin) -> None:
        self.setup_logger = c_log.Setup_Log()
        self.listener = Listener()
        self.listener.logger.log('info','Listener Started')
        self.log_queue = log_queue

        self.clock_data_queue = Queue()
        self.clock_data_event = Event()

        self.input_queue = Queue()
        self.input_event = Event()
        self.input_process = Process(target = LCD.main, 
                                     name = 'Screen',
                                     args = (self.input_queue, 
                                             self.input_event,
                                             Worker('LCD', None)
                                             ),
                                     daemon = False
                                     )

        self.clock_time = ClockTime(freq_pulse = 60, 
                                    folder_path = self.setup_logger.folder_path)
        self.clock_time.logger.log('info','Clock Data Started')

        self.clock_tower = ClockTower(pins = (clock_1_pin, clock_2_pin))
        self.clock_tower.logger.log('info', 'Tower Started')
        self.input()

    def input(self):
        try:
            self.input_process.start()
            while True:
                time.sleep(0.01)
                self.input_event.wait()
                input_diff = self.input_queue.get()
                diff = int((input_diff[1]-input_diff[0])//60)

        except KeyboardInterrupt:
            self.destroy()
        except Exception as e:
            LCD.destroy()
            self.input_process.join()

    def destroy(self) -> exit:
        self.listener.logger.log('critical', 'Progam being destroyed')
        self.listener.stop_event.set()
        self.listener.lp.join()
        print('\nbye....')
        exit(0)

clock_1_pin, clock_2_pin = 20, 21
cont = Controller(clock_1_pin, clock_2_pin)
