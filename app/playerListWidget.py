from PySide2 import QtWidgets, QtCore


class PlayerListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PlayerListWidget, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.lyt = QtWidgets.QVBoxLayout(self)
        self.lyt.setObjectName(u"players_wid_lyt")
        self.lyt.setContentsMargins(8, 8, 8, 8)

        self.players_sorting_lyt = QtWidgets.QHBoxLayout()
        self.players_sorting_lyt.setObjectName(u"players_sorting_lyt")

        self.players_sorting_lbl = QtWidgets.QLabel(self)
        self.players_sorting_lbl.setObjectName(u"players_sorting_lbl")
        self.players_sorting_lbl.setFixedSize(QtCore.QSize(45, 25))
        self.players_sorting_lbl.setText("Sort by :")
        self.players_sorting_lbl.setStyleSheet(u"color: #aaaaaa;")

        self.players_sorting_lyt.addWidget(self.players_sorting_lbl)

        self.players_sorting_ranking_btn = QtWidgets.QPushButton(self)
        self.players_sorting_ranking_btn.setText("Ranking")
        self.players_sorting_ranking_btn.setObjectName(u"players_sorting_ranking_btn")

        self.players_sorting_lyt.addWidget(self.players_sorting_ranking_btn)

        self.players_sorting_upnext_btn = QtWidgets.QPushButton(self)
        self.players_sorting_upnext_btn.setObjectName(u"players_sorting_upnext_btn")
        self.players_sorting_upnext_btn.setText("Up next")

        self.players_sorting_lyt.addWidget(self.players_sorting_upnext_btn)
        self.lyt.addLayout(self.players_sorting_lyt)

        self.player_list_wid = QtWidgets.QWidget(self)
        self.player_list_wid.setObjectName(u"player_list_wid")
        self.player_list_wid.setProperty("elevation", "low")

        self.player_list_wid_lyt = QtWidgets.QVBoxLayout(self.player_list_wid)
        self.player_list_wid_lyt.setSpacing(2)
        self.player_list_wid_lyt.setObjectName(u"player_list_wid_lyt")
        self.player_list_wid_lyt.setContentsMargins(8, 8, 8, 8)

        self.lyt.addWidget(self.player_list_wid)


class PlayerWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(PlayerWidget, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName(u"player_wid")
        self.setProperty("elevation", "medium")
        self.setFixedHeight(64)

        self.lyt = QtWidgets.QHBoxLayout(self)
        self.lyt.setSpacing(0)
        self.lyt.setObjectName(u"player_wid_lyt")
        self.lyt.setContentsMargins(0, 0, 0, 0)

        self.player_avatar_btn = QtWidgets.QPushButton(self)
        self.player_avatar_btn.setObjectName(u"player_avatar_btn")
        self.player_avatar_btn.setFixedSize(64, 64)
        self.player_avatar_btn.setFlat(True)

        self.lyt.addWidget(self.player_avatar_btn)

        self.player_name_lbl = QtWidgets.QLabel(self)
        self.player_name_lbl.setObjectName(u"player_name_lbl")
        self.player_name_lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.lyt.addWidget(self.player_name_lbl)

        self.player_ranks_lyt = QtWidgets.QVBoxLayout()
        self.player_ranks_lyt.setObjectName(u"player_ranks_lyt")
        self.player_ranks_lyt.setContentsMargins(8, 0, 8, 0)

        self.lyt.addLayout(self.player_ranks_lyt)

        self.player_rank_lbl = QtWidgets.QLabel(self)
        self.player_rank_lbl.setObjectName(u"player_rank_lbl")

        self.player_ranks_lyt.addWidget(self.player_rank_lbl)

        self.player_upnext_lbl = QtWidgets.QLabel(self)
        self.player_upnext_lbl.setObjectName(u"player_upnext_lbl")

        self.player_ranks_lyt.addWidget(self.player_upnext_lbl)

