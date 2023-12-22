from remote_control_alarm import ModbusAlarm
from remote_control_IO import zhongsheng_io_relay_controller
from remote_detect_current import fengkong_current_detector
import time

def command_shutdown(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                            current_controller: fengkong_current_detector):

    io_controller.set_all_switches(0);
    result = io_controller.read_output_conditions(address=0, count=8);
    alarm_controller.stop_alarm();
    return result;

def command_start(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                            current_controller: fengkong_current_detector):
    io_controller.set_all_switches(1);
    result = io_controller.read_output_conditions(address=0, count=8);
    return result;

def command_read(io_controller: zhongsheng_io_relay_controller,
                            current_controller: fengkong_current_detector):
    current_result_temp = None
    io_input_temp = [];
    io_output_temp = [];
    result = current_controller.read_current();
    if result:
        current_result_temp = result;
    time.sleep(0.1);
    input_result_1to6 = io_controller.read_input_conditions(address=0, count=0x6);
    temp_7to8 = io_controller.read_input_conditions(address=6, count=0x2)
    if input_result_1to6 and temp_7to8:
        io_input_temp = input_result_1to6 + temp_7to8;
    time.sleep(0.1);
    result = io_controller.read_outputs(address=0, count=8);
    if result:
        io_output_temp = result;
    return (current_result_temp,io_input_temp,io_output_temp)

def command_error(alarm_controller: ModbusAlarm, io_controller: zhongsheng_io_relay_controller,
                            current_controller: fengkong_current_detector):
    result = command_shutdown(alarm_controller, io_controller,current_controller);
    alarm_controller.play_alarm();





command_functions = {
    "shut_down" : command_shutdown,
    "start":command_start,
    "read":command_read
}

def execute_command(command,*args):
    if command in command_functions:
        return command_functions[command](*args);
    else:
        print("invalid command");

