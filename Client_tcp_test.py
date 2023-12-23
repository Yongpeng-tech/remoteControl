
from socket_tcp import *
from share_variables import *
from datetime import datetime
import time
if __name__ == '__main__':
    global configurations;
    tcp_cl = tcp_client(configurations["host"], configurations["port"]);
    result = tcp_cl.connect_client();

    data = {}
    if result:
        print("Connected to host")
    while result:
        user_input = input("Enter command:Start/Stop");
        if(user_input == "Start"):
            command_code = 1;
        elif user_input == "Stop":
            command_code = 0;
        else:
            command_code = -1;
        cur = datetime.now();
        date = cur.strftime("%d/%m/%Y-%H:%M:%S");
        data = {"date":date,"command":command_code}
        tcp_cl.sent_to_server(data);
        result = tcp_cl.read_from_server();
        for key in result:
            print(key + ": " + str(result[key]));
        time.sleep(0.1);