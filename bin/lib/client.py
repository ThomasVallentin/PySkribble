import socket
import pickle
from PySide2 import QtCore
from network.constants import *


from lib import logger, server


class ListeningThread(QtCore.QThread):
    message_received = QtCore.Signal(tuple)

    def __init__(self, ip, port):
        super(ListeningThread, self).__init__()
        self.logger = logger.Logger("ListeningThread", logger.INFO)
        self.ip = ip
        self.port = port

        self.socket = socket.socket()

    @property
    def address(self):
        return self.ip, self.port

    def run(self):
        self.socket.connect(self.address)

        while True:
            try:
                data = server.recv_msg(self.socket)

                if not data:
                    print("Disconnected")
                    break

                self.process_data(data)

            except Exception as e:
                raise e
                break

    def process_data(self, data):
        try:
            message = pickle.loads(data)

            if len(message) == 2:
                self.message_received.emit(message)
            else:
                self.message_received.emit((-1, message))
        except Exception as e:
            self.logger.debug(e)


class Client(object):
    def __init__(self, ip=None, port=None):
        super(Client, self).__init__()
        self.logger = logger.Logger(self.__class__.__name__, logger.INFO)

        self.host = ip or socket.gethostname()
        self.port = port or 5555

        self.socket = socket.socket()

        self.listening_thread = ListeningThread(self.host, self.port)
        self.listening_thread.message_received.connect(self._process_message)

    @property
    def address(self):
        return self.host, self.port

    def connect(self):
        self.listen()

        self.socket.connect(self.address)
        result = server.recv_msg(self.socket).decode()

        return result

    def send(self, byts):
        server.send_msg(self.socket, byts)

    def start(self):
        self.connect()

    def listen(self):
        self.listening_thread.start()

    def _process_message(self, message):
        typ, data = message

        self.process_message(typ, data)

    def process_message(self, typ, data):
        pass
        # self.logger.debug(f"{MESSAGE_NAMES.get(typ, MESSAGE_NAMES[-1])} : {data}")
