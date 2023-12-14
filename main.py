# This is a sample Python script.
import binascii

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder , BinaryPayloadDecoder
import time
from pymodbus.constants import Endian
import serial
from remote_control_alarm import Alarm
from remote_control_IO import zhongsheng_IO_relay_controller
from remote_detect_current import fengkong_current_detector
# Press the green button in the gutter to run the script.

import numpy as np
def control_switches( open_switch_list, close_switch_list,test):

    original_switches_conditions = [];

    for i, value in enumerate(test):
        temp = bin(test[i])[2:];
        fixed_length_binary = list('0'*(16-len(temp)) + temp);
        fixed_length_binary.reverse();
        original_switches_conditions = original_switches_conditions + fixed_length_binary;
    #print(original_switches_conditions)
    new_switches_conditions = original_switches_conditions;
    # print("change before:")
    # print(new_switches_conditions[0:16])
    # print(new_switches_conditions[16:32])
    # print(new_switches_conditions[32:48])
    for value in open_switch_list:
        new_switches_conditions[value-1] = '1';
    for value in close_switch_list:
        new_switches_conditions[value-1] = '0';
    # print("change after:")
    # print(new_switches_conditions[0:16])
    # print(new_switches_conditions[16:32])
    # print(new_switches_conditions[32:48])

    values = np.zeros(3)
    new_switches_conditions = np.array(new_switches_conditions,dtype=int);
    low_2bytes = new_switches_conditions[0:16];
    mid_2bytes = new_switches_conditions[16:32];
    high_2bytes = new_switches_conditions[32:48];
    #low_2bytes = low_2bytes[::-1]
    #mid_2bytes = mid_2bytes[::-1]
    #high_2bytes = high_2bytes[::-1]
    # print(low_2bytes)
    # print(mid_2bytes)
    # print(high_2bytes)
    values[0] = convert_16bits_integer(low_2bytes);
    values[1] = convert_16bits_integer(mid_2bytes);
    values[2] = convert_16bits_integer(high_2bytes);
    # print(values);
    return values;


def convert_16bits_integer(np_binary_array):
    low_8bits = np.packbits(np_binary_array[:8]);
    high_8bits = np.packbits(np_binary_array[8:]);
    print(low_8bits)
    print(high_8bits);
    return high_8bits << 8 | low_8bits;


if __name__ == '__main__':
    """
    test alarm region
    """
    # alarm = Alarm(serial_port="/dev/ttyUSB0", baud_rate= 9600,unit = 0x01);
    # alarm.setAlarmVolume(volume=5)
    # alarm.playAlarm();
    # time.sleep(1);
    # alarm.stopAlarm();
    # exit(0);


    """
    test IO_relay region 
    """
    IO_relay = zhongsheng_IO_relay_controller(serial_port="/dev/ttyUSB0", baud_rate= 38400,unit = 1,timeout=0.1);
    # result = IO_relay.read_input_conditions(address= 0x0000,count = 1);
    # print(result);
    # result = IO_relay.read_single_coil(address= 0x0000);
    # print(result);
    # time.sleep(1);
    # result = IO_relay.switch_single_ouput(address=0x0000, value=True);
    # print(result);
    # time.sleep(1);
    # result = IO_relay.switch_single_ouput(address=0x0000, value=False);

    '''
        cant work for 4 output IO_Relay device; maybe work for higher number of output 
    '''
    open_switch_list = [1];
    close_switch_list = [];
    result = IO_relay.control_switches(open_switch_list=open_switch_list,close_switch_list=close_switch_list);
    print(result);
    open_switch_list = [];
    close_switch_list = [1];
    result = IO_relay.control_switches(open_switch_list=open_switch_list, close_switch_list=close_switch_list);
    print(result);

    '''
    test fengkong current controller
    '''
    current_detector = fengkong_current_detector(serial_port="/dev/ttyUSB0", baud_rate= 9600,unit = 1,timeout=0.1);
    result = current_detector.read_current();
    print(str(result) + " A")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/