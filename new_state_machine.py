import logging

from exception_logger import *
from datetime import datetime
from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector

'''
shared variables between state machine and main_controller
'''

configurations = load_configuration();
my_logger = LoggingSystem(logger_name=configurations["logger_name"],
                          filename=configurations["logging_path"],level=logging.ERROR);
latest_logging = my_logger.read_json_information();

check_exception_logging_flag = True;
if latest_logging is not None and latest_logging["mark_condition"]:
    check_exception_logging_flag = True;
elif latest_logging is not None and not latest_logging["mark_condition"]:
    check_exception_logging_flag = False;
else:
    check_exception_logging_flag = True;

io_input = [];
io_output = [];
current_result = 0;

shutdown_signal = False;
start_signal = False;

state_variable = {
    "socket_connection_flag" : False,
    "port_connection_flag" : False,
    "io_connection_flag" : False,
    "current_connection_flag" : False,
    "alarm_connection_flag" : False,
    "devices_connection_flag" : False,
    "command_codes" : "read",
};


tcp_data = {};


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
    
    return True;

def check_connection():

    return True;

def shutdown_in_sequence():

    return True;

class system_waiting_state(State):
    '''
    system normal waiting state: system wait to start
    '''
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal;
        global client_connection_flag;
        global check_exception_logging_flag;
        global io_input;
        global io_output;
        global state_variable;
        if shutdown_signal:
            return system_shutdown_state();
        elif check_exception():
            return system_waiting_state();
        else:
            return system_start_state;

class system_start_state(State):
    '''
    system is boosting, run all subsystems
    '''
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        global shutdown_signal;
        global client_connection_flag;
        global check_exception_logging_flag;
        global io_input;
        global io_output;
        global state_variable;
        if shutdown_signal:
            return system_shutdown_state();
        elif check_exception():
            return system_waiting_state();
        else:
            return system_start_state;

class system_shutdown_state(State):
    '''
    system is shuting down
    '''
    def on_event(self,alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller
                 ,current_controller: fengkong_current_detector):
        print(f"The class name is:{self.__class__.__name__}")
        global shutdown_signal;
        global _connection_flag;
        global check_exception_logging_flag;
        global io_input;
        global io_output;
        '''
        system shut down operation here
        '''
        if shutdown_in_sequence():
            #excute PC shutdown
            return True;
        else:
            return system_shutdown_state();


