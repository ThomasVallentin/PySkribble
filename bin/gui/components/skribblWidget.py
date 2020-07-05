from PySide2 import QtWidgets, QtCore, QtGui

from constants import *

from gui.components import playersWidget as plywid
from gui.components import chatWidget as chtwid
from gui.components import paintWidget as pntwid
from gui.components import choiceWidget as chcdial

from gui.components.iconButton import IconButton
from gui.components import historyTextBar as textbar
from gui.components.framelessWindow import FramelessWindowMixin


class SkribblWidget(FramelessWindowMixin, QtWidgets.QWidget):
    guess_made = QtCore.Signal(str)
    choice_made = QtCore.Signal(int)
    message_sent = QtCore.Signal(str)
    start_requested = QtCore.Signal()

    def __init__(self, client, parent=None):
        """
        :param bin.app.Skribble client: the client linked to this instance
        :param QtWidgets.QObject parent:
        """
        super(SkribblWidget, self).__init__(parent=parent)

        self.client = client
        self._progress = 0

        self.players_wid = None
        self.paint_wid = None
        self.chat_wid = None
        self.choice_dial = None
        self.progress_animation = None

        self.setup_ui()
        self.make_connections()

    def get_progress(self):
        return self._progress

    def set_progress(self, value):
        self._progress = value
        self.time_progressbar.setValue(value)

    progress = QtCore.Property(int, get_progress, set_progress)

    def setup_ui(self):
        super(SkribblWidget, self).setup_ui()

        self.setWindowTitle("BETTER SKRIBBL v0.0.1")
        self.setObjectName("SkribblWidget")
        self.setProperty("elevation", "lowest")

        self.title_lbl = QtWidgets.QLabel(self)
        self.title_lbl.setStyleSheet("margin: 0; padding:0;")
        self.title_lbl.setPixmap(QtGui.QPixmap(os.path.join(RESSOURCES_DIR, "game_header.png")))
        self.lyt.addWidget(self.title_lbl)

        self.main_wid = QtWidgets.QWidget(self)
        self.main_wid.setObjectName("main_wid")
        self.main_wid.setProperty("elevation", "low")

        self.main_wid_lyt = QtWidgets.QVBoxLayout(self.main_wid)
        self.main_wid_lyt.setSpacing(16)
        self.main_wid_lyt.setObjectName("main_wid_lyt")
        self.main_wid_lyt.setContentsMargins(16, 16, 16, 16)

        self.time_progress_wid = QtWidgets.QWidget(self.main_wid)
        self.time_progress_wid.setObjectName("time_progress_wid")

        self.time_progress_wid_lyt = QtWidgets.QHBoxLayout(self.time_progress_wid)
        self.time_progress_wid_lyt.setObjectName("time_progress_wid_lyt")
        self.time_progress_wid_lyt.setContentsMargins(0, 0, 0, 0)

        self.time_progressbar = QtWidgets.QProgressBar(self.time_progress_wid)
        self.time_progressbar.setObjectName("time_progressbar")
        self.time_progressbar.setStyleSheet("color: white;")
        self.time_progressbar.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        self.time_progressbar.setFixedHeight(36)
        self.time_progressbar.setMaximum(10000)
        self.time_progressbar.setAlignment(QtCore.Qt.AlignCenter)

        self.time_progress_wid_lyt.addWidget(self.time_progressbar)
        self.main_wid_lyt.addWidget(self.time_progress_wid)

        self.game_wid = QtWidgets.QWidget(self.main_wid)
        self.game_wid.setObjectName("game_wid")

        self.game_wid_lyt = QtWidgets.QHBoxLayout(self.game_wid)
        self.game_wid_lyt.setSpacing(16)
        self.game_wid_lyt.setObjectName("game_wid_lyt")
        self.game_wid_lyt.setContentsMargins(0, 0, 0, 0)

        self.players_wid_cont = QtWidgets.QWidget(self.game_wid)
        self.players_wid_cont.setObjectName("players_wid_container")
        self.players_wid_cont.setProperty("elevation", "medium")
        self.players_wid_cont.setLayout(QtWidgets.QVBoxLayout())

        self.game_wid_lyt.addWidget(self.players_wid_cont)

        self.players_wid = plywid.PlayersWidget(self.players_wid_cont)
        # self.players_wid.setObjectName("players_wid")

        self.players_wid_cont.layout().addWidget(self.players_wid)

        self.paint_and_guess_wid = QtWidgets.QWidget(self.game_wid)
        self.paint_and_guess_wid.setObjectName("paint_and_guess_wid")
        self.paint_and_guess_wid.setProperty("elevation", "medium")

        self.paint_and_guess_wid_lyt = QtWidgets.QVBoxLayout(self.paint_and_guess_wid)
        self.paint_and_guess_wid_lyt.setObjectName("paint_and_guess_wid_lyt")
        self.paint_and_guess_wid_lyt.setContentsMargins(16, 16, 16, 16)

        self.paint_wid = pntwid.PaintWidget(self.paint_and_guess_wid)
        self.paint_wid.setObjectName("paint_wid")

        self.paint_and_guess_wid_lyt.addWidget(self.paint_wid)

        self.paint_wid_lyt = QtWidgets.QVBoxLayout(self.paint_wid.paint_view)

        self.start_btn = QtWidgets.QPushButton("Start game !", self)
        self.start_btn.setProperty("importance", "secondary")
        self.start_btn.setStyleSheet("QPushButton{padding: 16px;background-color: rgb(255, 0, 88)} "
                                     "QPushButton:hover{background: rgb(255, 51, 121)}"
                                     "QPushButton:pressed{background: rgb(0, 0, 0)}")
        self.start_btn.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.start_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.start_btn.setFixedWidth(250)

        self.paint_wid_lyt.addWidget(self.start_btn, 0, QtCore.Qt.AlignCenter)

        self.guess_was_right_lbl = QtWidgets.QLabel("You found it !", self.paint_wid)
        self.guess_was_right_lbl.setStyleSheet("background-color: transparent; color: #1E90FF")
        self.guess_was_right_lbl.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Black))
        self.guess_was_right_lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.guess_was_right_lbl.hide()
        self.paint_wid_lyt.addWidget(self.guess_was_right_lbl, 0, QtCore.Qt.AlignCenter)

        self.guess_lyt = QtWidgets.QHBoxLayout()
        self.guess_lyt.setObjectName("guess_lyt")

        self.guess_lbl = QtWidgets.QLabel(self.paint_and_guess_wid)
        self.guess_lbl.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Black))
        self.guess_lbl.setObjectName("guess_lbl")
        self.guess_lbl.setText("Make a guess !")

        self.guess_lyt.addWidget(self.guess_lbl)

        self.guess_lne = textbar.HistoryTextBar(self.paint_and_guess_wid)
        self.guess_lne.setObjectName("guess_lne")
        self.guess_lne.setFont(QtGui.QFont("SansSerif", 11))
        self.guess_lne.setPlaceholderText("Ex: Pierre qui roule n'amasse pas mousse")

        self.guess_lyt.addWidget(self.guess_lne)
        self.paint_and_guess_wid_lyt.addLayout(self.guess_lyt)
        self.game_wid_lyt.addWidget(self.paint_and_guess_wid)

        self.chat_wid = chtwid.ChatWidget(self.game_wid)
        self.chat_wid.setObjectName("chat_wid")
        self.chat_wid.setProperty("elevation", "medium")

        self.game_wid_lyt.addWidget(self.chat_wid)
        self.main_wid_lyt.addWidget(self.game_wid)
        self.lyt.addWidget(self.main_wid)

    def make_connections(self):
        super(SkribblWidget, self).make_connections()
        self.start_btn.clicked.connect(self.start_requested.emit)
        self.guess_lne.text_sent.connect(self.make_guess)

    def on_close(self):
        self.client.close()

    def update_players_from_game(self, game):
        self.players_wid.update_from_game(game)

    def clear_choice_dialog(self):
        if self.choice_dial:
            self.choice_dial.hide()
            self.choice_dial.deleteLater()
            self.choice_dial = None

    def start_choosing(self, choices, time):
        # Conforming the window state
        self.start_btn.hide()

        self.choice_dial = chcdial.ChoiceWidget(self)
        rect = QtCore.QRect(0, 64, self.width(), self.height() - 64)

        self.choice_dial.setGeometry(rect)
        self.choice_dial.load_choices(choices)
        self.choice_dial.choice_made.connect(self.choice_made.emit)

        self.choice_dial.show()

        self.start_progress_timer(time)

    def wait_for_choice(self, time):
        # Conforming the window state
        self.start_btn.hide()
        self.paint_wid.lock()

        self.start_progress_timer(time)

    def start_drawing(self, word, time):
        # Conforming the window state
        self.start_btn.hide()
        self.clear_choice_dialog()
        self.paint_wid.paint_view.clear()
        self.paint_wid.unlock()

        self.set_current_word(word)
        self.start_progress_timer(time)

    def start_guessing(self, preview, time):
        # Conforming the window state
        self.start_btn.hide()
        self.paint_wid.lock()
        self.paint_wid.paint_view.clear()

        self.set_current_word(preview)
        self.start_progress_timer(time)

    def set_current_word(self, word):
        self.time_progressbar.setFormat(word)

    def start_game(self):
        self.start_btn.hide()

    def start_round(self):
        self.guess_was_right_lbl.hide()

    def make_guess(self):
        self.guess_made.emit(self.guess_lne.text())
        self.guess_lne.clear()

    def guess_was_right(self):
        self.guess_was_right_lbl.show()

    def set_player_has_found(self, player_id):
        self.players_wid.set_player_has_found(player_id)

    def set_drawing_player(self, player_id):
        self.players_wid.set_drawing_player(player_id)

    def start_progress_timer(self, time):
        if self.progress_animation:
            self.progress_animation.stop()

        self.progress_animation = QtCore.QPropertyAnimation(self, b"progress")
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(10000)
        self.progress_animation.setDuration(time)
        self.progress_animation.start()
