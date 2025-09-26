import sys_bus
from usr.ui2 import *
import utime

lvglManager()
ret = sys_bus.sub_table()
print(ret)
sys_bus.publish("update_screen","init_screen")
utime.sleep(5)
while(1):
    sys_bus.publish("update_screen","open_eye_screen")
    print("open_eye_screen")
    utime.sleep(5)
    sys_bus.publish("update_screen","speaking_screen")
    print("speaking_screen")
    utime.sleep(5)
    sys_bus.publish("update_screen","listening_screen")
    print("listening_screen")
    utime.sleep(5)
    sys_bus.publish("update_screen","angry_screen")
    print("angry_screen")
    utime.sleep(5)
    sys_bus.publish("update_screen","sleeping_screen")
    print("sleeping_screen")
    utime.sleep(5)