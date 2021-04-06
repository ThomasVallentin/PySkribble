import pickle

from lib.client import Client
from lib.server import recv_msg
from network.constants import *


class SkribbleClient(Client):
    def __init__(self, name=None, ip=None, port=None):
        super(SkribbleClient, self).__init__(ip=ip, port=port)

        self.name = name
        self.avatar = bytearray()
        self.id = None

        self._game_data = None
        self._paint_buffer = []

    @property
    def player(self):
        return self.game_data.players[self.id]

    @property
    def game_data(self):
        return self._game_data

    def start(self):
        if not self.name:
            return ValueError("You have to set a name to start the client.")

        try:
            self.connect()
        except Exception as e:
            return e

        self.send_player()

    def send_message(self, typ, data):
        self.send(pickle.dumps((typ, data)))

    def send_player(self):
        self.send_message(ADD_PLAYER, (self.name, self.avatar))
        self.id = pickle.loads(recv_msg(self.socket))
        self._paint_buffer = pickle.loads(recv_msg(self.socket))

    def send_guess(self, guess):
        self.send_message(GUESS, guess)

    def send_choice(self, choice):
        self.send_message(CHOICE, choice)

    def send_paint(self, paint_info):
        self.send_message(PAINT, paint_info)

    def start_game(self, config_dict):
        self.send_message(START_GAME, config_dict)

    def update_game(self, game):
        self._game_data = game

    def process_message(self, typ, data):
        super(SkribbleClient, self).process_message(typ, data)

        if typ == GAME_DATA:
            self.update_game(data)


if __name__ == '__main__':
    from PySide2 import QtCore
    app = QtCore.QCoreApplication([])

    client = SkribbleClient()
    client.start()

    app.exec_()
