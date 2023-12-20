
import socket


class tcp_server():
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_address = (host,port);
        self.server_socket.bind(self.server_address);
        self.server_socket.listen(1);
        client_socket, address = self.server_socket.accept();
        self.client_socket = client_socket;
        self.client_address = address;
        print("Connected to client address " + str(self.client_address));

    def read_from_client(self):
        data = self.client_socket.recv(1024);
        return data.decode();

    def sent_to_client(self,data):
        self.client_socket.sendall(data.encode());

    def disconnect(self):
        self.client_socket.close();


class tcp_client():
    def __init__(self, host, port):
        self.client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_address = (host,port);
        self.client_socket.connect(self.server_address);
        print("Connect to server address " + str(self.server_address));

    def read_from_server(self):
        data = self.client_socket.recv(1024);
        return data.decode();

    def sent_to_server(self,data):
        self.client_socket.sendall(data.encode());

    def disconnect(self):
        self.client_socket.close();
