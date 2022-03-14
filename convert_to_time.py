from dataclasses import dataclass
import time

c1h = int(input('Clock 1 Hour: '))
c1m = int(input('Clock 1 Minute: '))
c2h = int(input('Clock 2 Hour: '))
c2m = int(input('Clock 2 Minute: '))
tm = [(c1h, c1m), (c2h, c2m)]

@dataclass
class Struct_Time:
    tm_year: int = time.localtime().tm_year
    tm_mon: int = time.localtime().tm_mon
    tm_mday: int = time.localtime().tm_mday
    tm_hour: int = time.localtime().tm_hour
    tm_min: int = time.localtime().tm_min
    tm_sec: int = time.localtime().tm_sec
    tm_wday: int = time.localtime().tm_wday
    tm_yday: int = time.localtime().tm_yday
    tm_isdst: int = time.localtime().tm_isdst
    
    def mktime(self):
        return time.mktime((self.tm_year, self.tm_mon, self.tm_mday, self.tm_hour,
                self.tm_min, self.tm_sec, self.tm_wday, self.tm_yday,
                self.tm_isdst))

struct_time1 = Struct_Time(tm_hour = c1h, tm_min = c1m)
struct_time2 = Struct_Time(tm_hour = c2h, tm_min = c2m)

input_time = [struct_time1.mktime(), 
              struct_time2.mktime()]
print(input_time)
# 1646927736.0; 1646927736.0