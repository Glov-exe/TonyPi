#!/usr/bin/python3
# coding=utf8
import time
import VL53L0X
import threading
import hiwonder.ActionGroupControl as AGC

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()

# Start ranging
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

timing = tof.get_timing()
if (timing < 20000):
    timing = 20000
print ("Timing %d ms" % (timing/1000))

AGC.runActionGroup('stand')  # 初始姿态

distance = None
last_distance = 999

#执行动作组线程
def move():
    global distance, last_distance
    while True:
        if distance is not None:
            if distance > 350: # 检测距离大于350mm时               
                if last_distance <= 350: # 如果上次距离大于350mm, 说明是刚转到检测不到障碍物，但是没有完全转正
                    last_distance = distance
                    AGC.runActionGroup('turn_right', 3)  # 右转3次
                else:
                    last_distance = distance
                    AGC.runActionGroup('go_forward')  # 直走
            elif 150 < distance <= 350: # 检测距离在150-350mm时
                last_distance = distance
                AGC.runActionGroup('turn_right')  # 右转
            else:
                last_distance = distance
                AGC.runActionGroup('back_fast') # 后退
        else:
            time.sleep(0.01)
        
#启动动作的线程
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

while True:
    distance = tof.get_distance() # 获取测距
    if (distance > 0):
        print ("%d mm" % distance)
    time.sleep(timing/1000000.00)
tof.stop_ranging()  # 关闭测距
