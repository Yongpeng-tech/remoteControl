'''
shared variables between state machine and main_controller
'''
import logging
from exception_logger import *

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

'''
share variable regions
'''

state_variable = {
    "socket_connection_flag" : False,
    "port_connection_flag" : False,
    "io_connection_flag" : False,
    "current_connection_flag" : False,
    "alarm_connection_flag" : False,
    "devices_connection_flag" : False,
    "command_codes" : "read",
};

RS485_devices_reading = {
    "io_input" : [],
    "io_output" : [],
    "current" : -1
};

ui_commands = {
    "shutdown_signal" :False,
    "start_signal" :False
};


'''
tcp read json format information,
Format is:
        {conveyor_state:bool,
        robot_state:bool,
        temperature_sensors = [sensor1_value,sensor2_value,sensor3_value,sensor4_value],
        }
'''
tcp_read_json_information ={
    "conveyor_state":False,
    "robot_state":False,
    "temperature_sensors" : [],
};

shut_down_state = {
    "shutdown_stage_0":"shutdown_stage_0",
    "shutdown_stage_1": "shutdown_stage_2",
};
start_state = {
    "state_stage_0":"state_stage_1",
    "state_stage_1":"state_stage_2"
};

STOP_BIT = 1;
START_BIT = 0;