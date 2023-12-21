
import socket
import json

class tcp_server():
    def __init__(self, host, port,time_out = 60):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_address = (host,port);
        self.server_socket.bind(self.server_address);
        self.server_socket.settimeout(time_out);

        self.server_socket.listen(5);
        self.client_socket  = None;
        self.client_address = None;

    def connect_client(self,waiting_time_out):
        try:
            client_socket, address = self.server_socket.accept();
            self.client_socket = client_socket;
            self.client_address = address;
            self.server_socket.settimeout(waiting_time_out);
            print("Connected to client address " + str(self.client_address));
            return True;
        except Exception as e:
            print("Failure to accept client's connection", e);
            return False;

    def read_from_client(self):
        '''
        read predefined json format from client
        :return:
        '''
        data = self.client_socket.recv(1024);
        json_str = data.decode("utf-8");
        received_dict = json.loads(json_str);
        return received_dict

    def sent_to_client(self,data):
        '''
        send dictionary via json format
        :param data: dictionary to be send
        :return:
        '''
        json_data = json.dumps(data).encode();
        self.client_socket.sendall(json_data);

    def disconnect(self):
        self.client_socket.close();


class tcp_client():
    def __init__(self, host, port,time_out = 60):
        self.client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_address = (host,port);
        self.client_socket.settimeout(time_out);
        self.client_socket.connect(self.server_address);
        print("Connect to server address " + str(self.server_address));

    def connect_client(self,waiting_time_out = 0.1):
        try:
            self.client_socket.connect(self.server_address);
            self.client_socket.settimeout(waiting_time_out);
            print("Connected to client address " );
            return True;
        except Exception as e:
            print("Failure to accept client's connection", e);
            return False;

    def read_from_server(self):
        '''

        :return:
        '''
        received_dict = {};
        data = self.client_socket.recv(1024);
        json_str = data.decode("utf-8");
        received_dict = json.loads(json_str);
        return received_dict;

    def sent_to_server(self,data):
        '''

        :param data:
        :return:
        '''
        json_data = json.dumps(data).encode();
        self.client_socket.sendall(json_data);

    def disconnect(self):
        self.client_socket.close();
