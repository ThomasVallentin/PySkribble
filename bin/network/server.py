from PySide2 import QtCore

from bin import game
import pickle

from lib.server import Server, Connection
from network.constants import *
from constants import AVATARS


class SkribbleConnection(Connection):

    def __init__(self, socket, server, parent=None):
        super(SkribbleConnection, self).__init__(socket, server, parent=parent)

        self.player = None

    def send_message(self, typ, data):
        self.socket.send(pickle.dumps((typ, data)))

    def send_data(self, data):
        self.socket.send(pickle.dumps(data))

    @property
    def game(self):
        """
        :return: game.GameLogic
        """
        return self.server.game

    @property
    def game_data(self):
        """
        :return: game.GameData
        """
        return self.server.game.game_data

    def process_data(self, data):
        try:
            message = pickle.loads(data)

            if len(message) == 2:
                self.process_message(*message)
            else:
                self.process_message(-1, message)

        except pickle.PickleError as e:
            self.logger.exception(e)

    def process_message(self, typ, data):
        self.logger.debug(f"Received message from {self.socket.getsockname()}"
                          f" : {MESSAGE_NAMES.get(typ, MESSAGE_NAMES[-1] + str(typ))} {data}")

        if typ == PAINT:
            self.server.send_message_to_listeners(PAINT, data)
            return True

        elif typ == GUESS:
            self.server.guess_received.emit(self.player, data)

            self.server.send_message_to_listeners(GAME_DATA, self.game_data)
            return True

        elif typ == CHOICE:
            self.server.choice_received.emit(self.player, data)
            return True

        elif typ == ADD_PLAYER:
            self.add_player(*data)

            self.logger.info(f'Player "{data[0]}" just joined the party !')

            self.send_data(self.player.id)
            self.server.send_message_to_listeners(GAME_DATA, self.game_data)
            return True

        elif typ == REMOVE_PLAYER:
            self.remove_player()

            self.logger.info(f"Player {self.player.name} picked the avatar {AVATARS[data][0]} !")

            return True

        elif typ == START_GAME:
            self.logger.info(f'Player "{self.player.name}" just requested the game to start !')
            self.server.start_game_requested.emit(self.player)
            return True

        elif typ == ECHO:
            print(f"Echoing from {self.socket.getsockname()} : {data}")
            return True

        return True

    def add_player(self, name, avatar_id):
        self.player = self.game.create_player()
        self.player.name = name
        self.player.avatar_id = avatar_id
        self.logger.debug(f"Creating a new player {name} for connection "
                          f"{self.socket.getsockname()}")

    def remove_player(self):
        if self.player:
            self.game.remove_player(self.player.id)
            self.logger.debug(f"Removing player {self.player.name}...")


class SkribbleServer(Server):
    CONNECTION_CLASS = SkribbleConnection

    guess_received = QtCore.Signal(game.Player, str)
    choice_received = QtCore.Signal(game.Player, int)
    start_game_requested = QtCore.Signal(game.Player)

    def __init__(self):
        super(SkribbleServer, self).__init__()
        self.game = game.GameLogic()

        self.connect_game()

    def connect_game(self):
        self.choice_received.connect(self.game.make_choice)
        self.guess_received.connect(self.game.make_guess)
        self.start_game_requested.connect(self.game.start)

        self.game.game_started.connect(self.send_game_started)
        self.game.choosing_started.connect(self.send_choosing_started)
        self.game.drawing_started.connect(self.send_drawing_started)
        self.game.round_ended.connect(self.send_game_data)

    def connection_ended(self, connection):
        if connection.player:
            connection.remove_player()
            self.send_message_to_listeners(GAME_DATA, self.game.game_data)

        super(SkribbleServer, self).connection_ended(connection)

    def send_game_started(self):
        self.send_message_to_listeners(GAME_STARTED, True)

    def send_game_data(self):
        self.send_message_to_listeners(GAME_DATA, self.game.game_data)

    def send_choosing_started(self, player, choices, time):
        self.send_message_to_listeners(CHOOSING_STARTED, (player, choices, time))

    def send_drawing_started(self, player, word, time):
        self.send_message_to_listeners(DRAWING_STARTED, (player, word, time))

    def send_message_to_listeners(self, typ, data):
        for connection in self.connections:
            if not connection.player:
                connection.send_message(typ, data)
