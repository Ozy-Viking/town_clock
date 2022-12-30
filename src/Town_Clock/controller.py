import os
import time
from multiprocessing import Event, Process, Queue, active_children
from typing import Any  # type: ignore

from Town_Clock import *


class Controller:
    def __init__(
        self,
        clock_pins: tuple[int, int],
        led_pin: int,
        common_pin: int,
        lat: float,
        long: float,
        alt: float,
        mode: Mode = Mode.TEST,
    ) -> None:
        print(mode)
        self.mode = mode

        self.all_processes: dict[str, Process] = {}
        self.all_queues: dict[str, Queue[Any]] = {}
        self.all_events: dict[str, Any] = {}  # type: ignore

        self.setup_logger = Setup_Log()
        self.listener = Listener()
        self.all_processes["listener_process"] = self.listener.lp
        self.listener.logger.log("critical", "CLOCK POWERED ON")
        self.listener.logger.log("info", "Listener Started")
        self.all_queues["log_queue"] = LOG_QUEUE
        self.temperature = Worker(name="Temperature", clock=None)

        self.all_queues["clock_data_queue"] = Queue()
        self.all_events["clock_data_event"] = Event()

        self.all_queues["input_queue"] = Queue()
        self.all_events["input_event"] = Event()
        if self.mode == Mode.ACTIVE:
            import Town_Clock.input_screen as lcd

            self.all_processes["input_process"] = Process(
                target=lcd.lcd_main,  # type: ignore
                name="Screen",
                args=(
                    self.all_queues["input_queue"],
                    self.all_events["input_event"],
                    Worker("lcd", None),
                ),
                daemon=False,
            )

        self.clock_time = ClockTime(
            freq_pulse=60,
            folder_path=self.setup_logger.folder_path,
            mode=self.mode,
        )
        self.clock_time.logger.log("info", "Clock 1 Data Started")

        self.position = {"latitude": lat, "longitude": long, "altitude": alt}
        self.clock_tower = ClockTower(
            clock_time=self.clock_time,
            clock_pins=clock_pins,
            led_pin=led_pin,
            common_pin=common_pin,
            position=self.position,
            mode=self.mode,
        )
        self.clock_tower.logger.log("info", "Tower Started")

        for p in self.all_processes:
            if not self.all_processes[p].is_alive():
                self.all_processes[p].start()
        self.listener.logger.log("info", f"Alive Child Processes: {active_children()}")
        self.input_diff = 0
        self.input_diff_sec = 0

    def main(self) -> None:
        time.sleep(0.1)
        while True:
            try:
                if self.all_events["input_event"].is_set():
                    self.clock_time.logger.log("debug", "Input_event is set")
                    clock, self.input_diff = self.all_queues["input_queue"].get()
                    self.input_diff_sec = self.input_diff * 60
                    if self.input_diff != 0:
                        self.listener.logger.log(
                            "info",
                            f"Received diff of {self.input_diff_sec} secs for clock {clock} from LCD.",
                        )
                        self.clock_time.change_clock_time(
                            dt=self.input_diff_sec, clock=clock
                        )
                    self.input_diff = 0
                    self.input_diff_sec = 0
                    self.all_events["input_event"].clear()

                tm = time.time()
                if int(tm % self.clock_time.freq_pulse) == 0:
                    tp_0 = time.time()

                    self.clock_time.logger.log("debug", f"{tm = }")
                    self.clock_time.current_time = tm
                    try:
                        (
                            self.clock_time.diff,
                            self.clock_time.diff_secs,
                        ) = self.clock_time.clock_time_diff()
                        self.listener.logger.log(
                            "info",
                            f"Clock_time_diff: {self.clock_time.diff}, "
                            f"{time.asctime(time.localtime(tm))}, "
                            f"Clock 1 Time: "
                            f"{time.asctime(time.localtime(self.clock_time.clock_time[0]))}, "
                            f"Clock 2 Time: "
                            f"{time.asctime(time.localtime(self.clock_time.clock_time[1]))}",
                        )
                    except ValueError as error:
                        self.listener.logger.log(
                            "error", f"Main clock_time_diff: {error}"
                        )

                    clock_pulses: list[int] = list()
                    if self.clock_time.diff != [0, 0]:
                        for c_diff in self.clock_time.diff:
                            if c_diff >= 0:
                                clock_pulses.append(0)
                            else:
                                clock_pulses.append(abs(c_diff))

                        self.clock_tower.pulse(
                            ct=self.clock_time, clock_pulses=clock_pulses
                        )

                    self.clock_time.logger.log(
                        "info", f"Loop Clocktime: {self.clock_time}"
                    )
                    tp_1 = time.time()
                    self.listener.logger.log(
                        "info", f"Time Taken: {(tp_1 - tp_0) * 1000 - 1000:.2f} ms"
                    )
                    if get_cpu_temp() > 80:
                        self.temperature.log("error", f"{get_cpu_temp():.2f}")
                    else:
                        self.temperature.log("info", f"{get_cpu_temp():.2f}")

                    time.sleep(1.0001)

                    self.clock_tower.check_if_night(tm)
                    self.restart(self.clock_tower.clock_time.clock_local_time[0])

                time.sleep(0.009)

            except KeyboardInterrupt:
                self.destroy()
            except Exception as e:
                self.listener.logger.log("error", f"{e}")
                time.sleep(1)

    def destroy(self, restart: bool = False) -> None:
        self.listener.logger.log("critical", "Program being destroyed")
        self.listener.stop_event.set()
        for p in self.all_processes:
            self.all_processes[p].join()
        for q in self.all_queues:
            self.all_queues[q].close()

        if not restart:
            print("\nbye....")
            exit(0)

    def restart(self, local_time: time.struct_time) -> None:
        """
        Restart Computer at 2am every day.
        """
        if local_time.tm_hour == 2 and local_time.tm_min == 0:
            self.destroy()
            os.system("init 6")  # "shutdown /r /t 1")


def get_cpu_temp() -> float:
    with open("/sys/class/thermal/thermal_zone0/temp") as file:
        cpu = file.read()
    return float(cpu) / 1000
