import socket
import pickle
from PySide2 import QtCore
from network.constants import *


from lib import logger


class ListeningThread(QtCore.QThread):
    message_received = QtCore.Signal(tuple)

    def __init__(self, ip, port):
        super(ListeningThread, self).__init__()
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
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    print("Disconnected")
                    break

                self.process_data(data)

            except Exception as e:
                raise
                break

    def process_data(self, data):
        try:
            message = pickle.loads(data)

            if len(message) == 2:
                self.message_received.emit(message)
            else:
                self.message_received.emit((-1, message))
        except:
            pass


class Client(object):
    def __init__(self, ip=None, port=None):
        super(Client, self).__init__()
        self.logger = logger.Logger(self.__class__.__name__, logger.DEBUG)

        self.ip = ip or socket.gethostname()
        self.port = port or 5555

        self.socket = socket.socket()

        self.listening_thread = ListeningThread(self.ip, self.port)
        self.listening_thread.message_received.connect(self._process_message)

    @property
    def address(self):
        return self.ip, self.port

    def connect(self):
        self.listen()

        self.socket.connect(self.address)
        result = self.socket.recv(BUFFER_SIZE).decode()

        return result

    def send(self, byts):
        self.socket.send(byts)

    def start(self):
        self.connect()

    def listen(self):
        self.listening_thread.start()

    def _process_message(self, message):
        typ, data = message

        self.process_message(typ, data)

    def process_message(self, typ, data):
        self.logger.debug(f"{MESSAGE_NAMES.get(typ, MESSAGE_NAMES[-1])} : {data}")
