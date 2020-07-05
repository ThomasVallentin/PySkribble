from PySide2 import QtWidgets, QtCore, QtGui

import os
import sys

from lib import utils
from network import client
from constants import RESSOURCES_DIR
from network.constants import *
from gui.components import connectDialog, skribblWidget


class Skribble(client.SkribbleClient):
    def __init__(self):
        super(Skribble, self).__init__(ip="192.168.1.84", port=5555)

        self.game_widget = None

        with open(os.path.join(RESSOURCES_DIR, "style.qss"), "r") as qss:
            self.qss = (qss.read())

        self.connect_dial = connectDialog.ConnectDialog(self)
        self.connect_dial.setStyleSheet(self.qss + self.connect_dial.style)

    def send(self, *args, **kwargs):
        super(Skribble, self).send(*args, **kwargs)

    def launch(self):
        connected = self.connect_dial.exec_()

        if not connected:
            return self.close()

        self.launch_game_widget()

    def launch_game_widget(self):
        screen = QtWidgets.QApplication.screenAt(self.connect_dial.pos())

        self.game_widget = skribblWidget.SkribblWidget(self)
        self.game_widget.setStyleSheet(self.qss)
        self.game_widget.setGeometry(screen.geometry())

        self.game_widget.paint_wid.painted.connect(self.send_paint)
        self.game_widget.start_requested.connect(self.start_game)
        self.game_widget.choice_made.connect(self.send_choice)
        self.game_widget.guess_made.connect(self.send_guess)
        self.game_widget.show()

    def close(self):
        self.socket.close()

        self.connect_dial.close()

        if self.game_widget:
            self.game_widget.close()

        self.listening_thread.terminate()

        sys.exit(0)

    def update_game(self, game):
        super(Skribble, self).update_game(game)

        self.game_widget.update_players_from_game(self.game_data)

    def process_message(self, typ, data):
        if typ == PAINT:
            # TODO: Handle the case where I am the painter (skip the painting)
            self.game_widget.paint_wid.paint_from_message(*data)

        elif typ == CHOOSING_STARTED:
            pid, choices, time = data

            if pid == self.id:
                self.logger.debug("Starting to choose...")
                self.game_widget.start_choosing(choices, time)

            else:
                self.game_widget.wait_for_choice(time)

        elif typ == DRAWING_STARTED:
            pid, word, time = data
            if pid == self.id:
                self.game_widget.start_drawing(word, time)
            else:
                self.game_widget.start_guessing(utils.make_preview(word), time)

            self.game_widget.set_drawing_player(pid)

        elif typ == PLAYER_GUESSED:
            pid, rank = data
            if pid == self.id:
                self.game_widget.guess_was_right(rank)

            self.game_widget.set_player_has_found(pid)

        elif typ == ADD_PLAYER:
            pass

        elif typ == REMOVE_PLAYER:
            pass

        elif typ == ROUND_STARTED:
            self.game_widget.start_round()

        elif typ == GAME_STARTED:
            self.game_widget.start_game()

        super(Skribble, self).process_message(typ, data)
