# This is a sample Python script.
import binascii

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
import numpy as np
import threading
import time
from new_state_machine import *
from pymodbus import Framer
from datetime import datetime
from pymodbus.client import ModbusSerialClient
from socket_tcp import *
from commands_parse import execute_command
from share_variables import *

# def main_controller_handler(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
#                             current_controller: fengkong_current_detector):
#     global io_input
#     global io_output
#     global current_result;
#     global state_variable;
#     flag = False;
#     input_result = False;
#     print("main_controller_handler start");
#     while True:
#         '''
#         Read io input and output as well as current to monitor the system's
#         conditions
#         '''
#         if state_variable["command_codes"] == "shut_down":
#             current_result, io_input, io_output = execute_command(state_variable["command_codes"],alarm_controller
#                                                                   ,zhongsheng_io_relay_controller,current_controller)
#         elif state_variable["command_codes"] == "start":
#             result = execute_command(state_variable["command_codes"],alarm_controller,zhongsheng_io_relay_controller,
#                                      current_controller)
#         elif state_variable["command_codes"] == "read":
#             result = execute_command(state_variable["command_codes"], alarm_controller, zhongsheng_io_relay_controller,
#                                      current_controller)
#
#         time.sleep(0.5);


def io_controller_handler(io_controller: zhongsheng_io_relay_controller
                          ,current_detector:fengkong_current_detector,timeout,lock):
    '''
    Threading function to read io input and output as well as current.
    This function run a specific amount of time periodically
    :param io_controller: zhongsheng_io_relay_controller object
    :param current_detector: fengkong_current_detector object
    :return:
    '''

    print("io_controller_handler start");
    global RS485_devices_reading;

    while True:
        with ((((lock)))):
            result = execute_command("read",io_controller,current_detector);
            RS485_devices_reading["io_input"] = result[1];
            RS485_devices_reading["io_output"] = result[2];
            RS485_devices_reading["current"] = result[0];
        time.sleep(timeout);


def tcp_handler(server:tcp_server,timeout,lock):
    global tcp_data;
    global RS485_devices_reading;
    global ui_controller;
    while True:
        with lock:
            tcp_data = server.read_from_client();
            if(tcp_data != None):
                # for key in tcp_data:
                #     print(key,":",tcp_data[key])
                cur = datetime.now();
                date = cur.strftime("%Y-%m-%d %H:%M:%S");
                data = {"date":date}
                server.sent_to_client(data);
                if tcp_data["command"] == 1:
                    ui_commands["start_signal"] = True;
                elif tcp_data["command"] ==0:
                    ui_commands["stop_signal"] = True;
                # print(RS485_devices_reading)
        time.sleep(timeout);


if __name__ == '__main__':
    global state_variable;

    serial_client = ModbusSerialClient(
                method='rtu',
                Framer=Framer.RTU,
                port="/dev/ttyUSB0",
                baudrate=19200,
                parity='N',
                bytesize=8,
                stopbits=1,
                timeout=0.01,
                errorcheck="crc"
            )
    connection = serial_client.connect();
    if connection:
        port_connection_flag = True;

    '''
    initialize three devices
    '''
    modbusalarm = ModbusAlarm(serial_client,unit = 1)
    io_relay = zhongsheng_io_relay_controller(serial_client, unit=2, small_port = False)
    current_detector = fengkong_current_detector(serial_client, unit=3)


    '''
    check device connection, check 10 times to do connection with all devices
    '''
    times = 0;
    while times<10:
        #state_variable["alarm_connection_flag"] = modbusalarm.check_connection(addr = 1);
        state_variable["io_connection_flag"] = io_relay.check_connection(addr=0);
        time.sleep(0.1);
        state_variable["current_connection_flag"] = True if current_detector.read_current() else False;
        if (not state_variable["alarm_connection_flag"] or not state_variable["io_connection_flag"]
                or not state_variable["current_connection_flag"]):
            devices_connection_flag = False;
            times += 1;
        else:
            devices_connection_flag = True;
            break;
        time.sleep(0.1);
    print(state_variable["alarm_connection_flag"] ,  state_variable["io_connection_flag"],state_variable["current_connection_flag"] )
    '''
    wait client make tcp connection in specific amount of time 
    '''
    socket_server = tcp_server(host= configurations ["host"],port= configurations["port"],
                               time_out=configurations["connection_time_out"]);
    socket_connection_flag = socket_server.connect_client(waiting_time_out=configurations["waiting_time_out"]);


    '''
    Ready to run exception monitor system and read io and tcp devices 
    '''


    threads = []
    lock = threading.Lock(); #lock for shared data structure between socket and threading

    thread = threading.Thread(target=io_controller_handler, args=(io_relay, current_detector,0.1,lock));
    thread.start();
    threads.append(thread)

    thread = threading.Thread(target=tcp_handler, args=(socket_server,0.1,lock));
    thread.start();
    threads.append(thread)



    exception_handler_system = StateMachine(system_start_state(),lock,
                                            modbusalarm,io_relay,current_detector,
                                           1);
    exception_handler_system.run();
    for thread in threads:
        thread.join();


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
