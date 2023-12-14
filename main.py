# This is a sample Python script.
import binascii

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from remote_control_alarm import Alarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
import logging
import numpy as np
import threading
import time


def main_controller_handler(alarm_controller: Alarm, io_controller: zhongsheng_io_relay_controller,
                            current_controller: fengkong_current_detector):
    flag = False;
    input_result = False;
    alarm_controller.setAlarmVolume(1);  # slience alarm
    print("main_controller_handler start");
    time.sleep(1);
    while True:
        current_result = current_controller.read_current();
        # print("current is :"+str(current_result)+ " A");
        input_result = io_controller.read_input_conditions(address=0, count=1);
        io_controller.switch_single_ouput(address=0, value=input_result[0]);

        if input_result[0] and not flag:
            print("Enter")
            alarm_controller.playAlarm();
            time.sleep(0.5);
            alarm_controller.stopAlarm();
            flag = True;
        if not input_result and flag:
            flag = False;
        time.sleep(0.5);


def io_controller_handler(io_controller: zhongsheng_io_relay_controller):
    print("io_controller_handler start");
    while True:
        result = io_controller.read_input_conditions(address=0, count=1);
        print(result);
        io_controller.switch_single_ouput(address=0, value=result[0]);
        time.sleep(0.5);


def tcp_handler():

    time.sleep();

if __name__ == '__main__':
    alarm = Alarm(serial_port="/dev/ttyUSB0", baud_rate=19200, unit=0x01);
    io_relay = zhongsheng_io_relay_controller(serial_port="/dev/ttyUSB0", baud_rate=19200, unit=2, timeout=0.1);
    current_detector = fengkong_current_detector(serial_port="/dev/ttyUSB0", baud_rate=19200, unit=3, timeout=0.1);
    threads = []
    thread = threading.Thread(target=main_controller_handler, args=(alarm, io_relay, current_detector));
    thread.start();
    threads.append(thread)
    # thread = threading.Thread(target= io_controller_handler,args = (io_relay,));
    # threads.append(thread)
    # thread.start();

    for thread in threads:
        thread.join();
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
