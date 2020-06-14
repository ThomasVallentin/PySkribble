from PySide2 import QtWidgets, QtCore
import qtawesome as qta

from app import paintWidget as pntwid
from app import playerListWidget as plywid
from app import chatWidget as chtwid


class SkribblWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SkribblWidget, self).__init__(parent=parent)

        self.players_wid = None
        self.paint_wid = None
        self.chat_wid = None

        self.setup_ui()

        with open(r"lib\gui\style.qss", "r") as style:
            self.setStyleSheet(style.read())

    def setup_ui(self):
        self.setObjectName(u"SkribblWidget")
        self.setProperty("elevation", "lowest")

        self.lyt = QtWidgets.QVBoxLayout(self)
        self.lyt.setSpacing(8)
        self.lyt.setObjectName(u"lyt")
        self.lyt.setContentsMargins(8, 8, 8, 8)

        self.title_bar = QtWidgets.QWidget(self)
        self.title_bar.setObjectName(u"title_bar")
        self.title_bar.setProperty("elevation", "low")

        self.title_bar_lyt = QtWidgets.QHBoxLayout(self.title_bar)
        self.title_bar_lyt.setObjectName(u"title_bar_lyt")
        self.title_bar_lyt.setContentsMargins(8, 8, 8, 8)

        self.title_lbl = QtWidgets.QLabel(self.title_bar)
        self.title_lbl.setObjectName(u"title_lbl")
        self.title_lbl.setText("BETTER SKRIBBL v0.0.1")

        self.title_bar_lyt.addWidget(self.title_lbl)
        self.lyt.addWidget(self.title_bar)

        self.main_wid = QtWidgets.QWidget(self)
        self.main_wid.setObjectName(u"main_wid")
        self.main_wid.setProperty("elevation", "low")

        self.main_wid_lyt = QtWidgets.QVBoxLayout(self.main_wid)
        self.main_wid_lyt.setSpacing(8)
        self.main_wid_lyt.setObjectName(u"main_wid_lyt")
        self.main_wid_lyt.setContentsMargins(8, 8, 8, 8)

        self.time_progress_wid = QtWidgets.QWidget(self.main_wid)
        self.time_progress_wid.setObjectName(u"time_progress_wid")

        self.time_progress_wid_lyt = QtWidgets.QHBoxLayout(self.time_progress_wid)
        self.time_progress_wid_lyt.setObjectName(u"time_progress_wid_lyt")
        self.time_progress_wid_lyt.setContentsMargins(0, 0, 0, 0)

        self.time_progressbar = QtWidgets.QProgressBar(self.time_progress_wid)
        self.time_progressbar.setObjectName(u"time_progressbar")
        self.time_progressbar.setStyleSheet(u"font-weight: bold; color: white;")
        self.time_progressbar.setAlignment(QtCore.Qt.AlignCenter)

        self.time_progress_wid_lyt.addWidget(self.time_progressbar)
        self.main_wid_lyt.addWidget(self.time_progress_wid)

        self.game_wid = QtWidgets.QWidget(self.main_wid)
        self.game_wid.setObjectName(u"game_wid")

        self.game_wid_lyt = QtWidgets.QHBoxLayout(self.game_wid)
        self.game_wid_lyt.setSpacing(8)
        self.game_wid_lyt.setObjectName(u"game_wid_lyt")
        self.game_wid_lyt.setContentsMargins(0, 0, 0, 0)

        self.players_wid = plywid.PlayerListWidget(self.game_wid)
        self.players_wid.setObjectName(u"players_wid")
        self.players_wid.setProperty("elevation", "medium")

        self.game_wid_lyt.addWidget(self.players_wid)

        self.point_and_guess_widget = QtWidgets.QWidget(self.game_wid)
        self.point_and_guess_widget.setObjectName(u"point_and_guess_widget")
        self.point_and_guess_widget.setProperty("elevation", "medium")

        self.point_and_guess_widget_lyt = QtWidgets.QVBoxLayout(self.point_and_guess_widget)
        self.point_and_guess_widget_lyt.setObjectName(u"point_and_guess_widget_lyt")
        self.point_and_guess_widget_lyt.setContentsMargins(8, 8, 8, 8)

        self.game_paint_view = pntwid.PaintWidget(self.point_and_guess_widget)
        self.game_paint_view.setObjectName(u"game_paint_view")

        self.point_and_guess_widget_lyt.addWidget(self.game_paint_view)

        self.paint_toolbox = QtWidgets.QWidget(self.point_and_guess_widget)
        self.paint_toolbox.setObjectName(u"paint_toolbox")

        self.paint_toolbox_lyt = QtWidgets.QHBoxLayout(self.paint_toolbox)
        self.paint_toolbox_lyt.setObjectName(u"paint_toolbox_lyt")
        self.paint_toolbox_lyt.setContentsMargins(0, 0, 0, 0)

        self.point_and_guess_widget_lyt.addWidget(self.paint_toolbox)

        self.guess_lyt = QtWidgets.QHBoxLayout()
        self.guess_lyt.setObjectName(u"guess_lyt")

        self.guess_lbl = QtWidgets.QLabel(self.point_and_guess_widget)
        self.guess_lbl.setObjectName(u"guess_lbl")
        self.guess_lbl.setText("Make a guess !")

        self.guess_lyt.addWidget(self.guess_lbl)

        self.guess_lne = QtWidgets.QLineEdit(self.point_and_guess_widget)
        self.guess_lne.setObjectName(u"guess_lne")
        self.guess_lne.setPlaceholderText("Ex: Pierre qui roule n'amasse pas mousse")

        self.guess_lyt.addWidget(self.guess_lne)
        self.point_and_guess_widget_lyt.addLayout(self.guess_lyt)
        self.game_wid_lyt.addWidget(self.point_and_guess_widget)

        self.chat_wid = chtwid.ChatWidget(self.game_wid)
        self.chat_wid.setObjectName(u"chat_wid")
        self.chat_wid.setProperty("elevation", "medium")

        self.game_wid_lyt.addWidget(self.chat_wid)
        self.main_wid_lyt.addWidget(self.game_wid)
        self.lyt.addWidget(self.main_wid)
