
from datetime import datetime
from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
from share_variables import *
import os

class State:
    '''
    class state
    '''
    def __int__(self, name):
        self.name = name;

    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        pass;

class StateMachine:
    def __init__(self,initial_state:State,lock,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        self.current_state = initial_state;
        self.lock = lock;
        self.current_controller = current_controller;
        self.alarm_controller = alarm_controller;
        self.io_controller = io_controller;

    def run(self):
        while True:
            with self.lock:
                self.current_state = self.current_state.on_event(self.alarm_controller,
                                                                 self.io_controller,self.current_controller);


def check_exception():
    global RS485_devices_reading;
    global my_logger;
    global configurations;
    log_info = my_logger.read_json_information();
    if log_info and not log_info["debug_condition"]:
        my_logger.log_json_information(error_code=0x04, debug_condition=False, mark_condition=False);
        return False;
    elif tcp_read_json_information:
        if (tcp_read_json_information["temperature_sensors"] and
                max(tcp_read_json_information["temperature_sensors"]) > configurations["temperature_threshold"]):
            my_logger.log_json_information(error_code=0x05, debug_condition=False, mark_condition=False);
            return False;
        elif not tcp_read_json_information["robot_state"]:
            my_logger.log_json_information(error_code=0x06, debug_condition=False, mark_condition=False);
            return False;
        elif not tcp_read_json_information["conveyor_state"]:
            my_logger.log_json_information(error_code=0x07, debug_condition=False, mark_condition=False);
            return False;
    elif RS485_devices_reading != -1 and RS485_devices_reading["current"] < configurations["current_threshold"]:
        my_logger.log_json_information(error_code=0x08,debug_condition=False, mark_condition=False);
        return False;

    return True;

def check_connection():
    global state_variable;
    global my_logger;
    global configurations;
    if not state_variable["socket_connection_flag"]:
        my_logger.log_json_information(error_code=0x01,debug_condition=False,mark_condition=False);
        return False;
    elif not state_variable["port_connection_flag"]:
        my_logger.log_json_information(error_code=0x02,debug_condition=False,mark_condition=False);
        return False;
    elif not state_variable["devices_connection_flag"]:
        my_logger.log_json_information(error_code=0x03,debug_condition=False,mark_condition=False);
        return False;
    else:
        return True;



class system_waiting_state(State):
    '''
    system normal waiting state: system wait to start
    '''
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        print(f"The class name is:{self.__class__.__name__}")
        global ui_commands;
        global RS485_devices_reading;
        global configurations;
        io_controller.set_all_switches(STOP_BIT);
        result = io_controller.read_outputs(address = 0, count=8);
        if ui_commands["shutdown_signal"]:
            return system_shutdown_state();
        elif check_exception():
            if RS485_devices_reading["current"] < configurations["current_threshold"]:
                return system_shutdown_state();
            return system_waiting_state();
        elif RS485_devices_reading and RS485_devices_reading["io_input"][configurations["io_emergency_stop_port_num"]] == STOP_BIT:
            return system_waiting_state();
        elif ui_commands["start_signal"]:
            return system_start_state()
        else:
            return system_waiting_state();

class system_start_state(State):
    '''
    system is boosting, run all subsystems
    '''
    def __init__(self,state = "state_stage_0"):
        self.state = state;
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        global RS485_devices_reading;
        global ui_commands;
        if ui_commands["shutdown_signal"]:
            return system_shutdown_state();
        elif check_exception():
            return system_waiting_state();
        elif RS485_devices_reading and RS485_devices_reading["io_input"][configurations["io_emergency_stop_port_num"]] == STOP_BIT:
            return system_waiting_state();
        else:
            self.start_in_sequence(io_controller);
            return system_start_state(self.state);

    def start_in_sequence(self,io_controller: zhongsheng_io_relay_controller):
        global RS485_devices_reading;
        global start_state;
        global configurations;
        if start_state == "state_stage_0":
            if RS485_devices_reading["io_input"] and len(RS485_devices_reading["io_input"]) == 8:
                start_list = [START_BIT]*7;
                if(start_list == RS485_devices_reading["io_input"][:7]):
                    self.state = start_state[self.state];
        elif start_state == "state_stage_1":
            io_controller.set_all_switches(START_BIT);
            result = io_controller.read_outputs(address=0,count = 8);
            if result and len(result) == 8:
                start_list = [START_BIT]*8;
                if(result == start_list):
                    self.state = start_state[self.state];


class system_shutdown_state(State):
    '''
    system is shuting down
    '''
    def __init__(self,state = "shutdown_stage_0"):
        self.state = state;
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        print(f"The class name is:{self.__class__.__name__}")

        '''
        system shut down operation here
        '''
        self.shutdown_in_sequence(io_controller);
        return system_shutdown_state(self.state);


    def shutdown_in_sequence(self,io_controller: zhongsheng_io_relay_controller):
        global RS485_devices_reading;
        global shut_down_state;
        if self.state == "shutdown_stage_0":
            io_controller.set_all_switches(STOP_BIT);
            result = io_controller.read_outputs(address=0,count=8);
            if result and len(result) != 8:
                self.state = "shutdown_stage_0";
            else:
                stop_list = [STOP_BIT]*7;
                if result == stop_list:
                    self.state = shut_down_state[self.state];
                else:
                    self.state = "shutdown_stage_0";
        elif self.state == "shutdown_stage_1":
            '''
            wait user to shutdown the physical relays
            '''
            io_input = RS485_devices_reading["io_input"];
            stop_list = [STOP_BIT]*7;
            if io_input[:7] == stop_list:
                self.state = shut_down_state[self.state];

        elif self.state == "shutdown_stage_2":
            io_controller.set_all_switches(START_BIT);
            result = io_controller.read_outputs(address=0, count=8);
            start_list = [START_BIT] * 8;
            if result and len(result) == 8:
                if result == start_list:
                    print("system should be shutdown here")
                    #os.system("shutdown now");


