from PySide2 import QtCore

import socket
import struct
import threading

from lib import logger


class Connection(QtCore.QThread):
    connection_ended = QtCore.Signal(object)

    def __init__(self, socket, server, parent=None):
        super(Connection, self).__init__(parent)
        self.logger = logger.Logger(self.__class__.__name__, logger.INFO)

        self.socket = socket
        self.server = server

        self.thread = None

    def send(self, byts):
        send_msg(self.socket, byts)

    def run(self):
        self.thread_loop()
        self.connection_ended.emit(self)

    def answer_to_connection(self):
        self.send(b"1")

    def thread_loop(self):
        self.answer_to_connection()

        while True:
            try:
                data = recv_msg(self.socket)

                if not data:
                    self.logger.info("Disconnected")
                    break

                self.process_data(data)

            except Exception as e:
                self.logger.debug(e)
                break

        self.logger.info(f"Connection lost : {self.socket.getsockname()}")
        self.socket.close()

    def process_data(self, data):
        pass


class Server(QtCore.QThread):
    CONNECTION_CLASS = Connection
    BUFFER_SIZE = 2048

    def __init__(self, ip="", port=5555):
        super(Server, self).__init__()
        self.logger = logger.Logger(self.__class__.__name__)

        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connections = []

    @property
    def address(self):
        return self.ip, self.port

    def process_connection(self, conn_socket):
        connection = self.CONNECTION_CLASS(conn_socket, self)
        self.connections.append(connection)

        connection.connection_ended.connect(self.connection_ended)

        connection.start()

        return connection

    def connection_ended(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def run(self):
        self.socket.bind(self.address)
        print(self.socket.getsockname())
        self.socket.listen(2)

        self.logger.info(f"{self.__class__.__name__} started and running on {threading.current_thread().getName()}")
        self.logger.info("Waiting for a connection...")

        while True:
            conn_socket, address = self.socket.accept()
            self.logger.info(f"Incoming connection from {address}")

            self.process_connection(conn_socket)


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


class EchoConnection(Connection):
    def process_message(self, msg):
        data = msg.decode()

        print("Received :", data)

        self.send(msg)


class EchoServer(Server):
    CONNECTION_CLASS = EchoConnection


if __name__ == '__main__':
    server = EchoServer()
    server.start()
