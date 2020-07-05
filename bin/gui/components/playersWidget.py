from PySide2 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from constants import *


class PlayersWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PlayersWidget, self).__init__(parent=parent)

        self.player_items = {}

        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(350)
        self.setObjectName("players_widget")

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

        self.player_list_wid = QtWidgets.QListWidget(self)
        self.player_list_wid.setSpacing(4)
        self.player_list_wid.setStyleSheet("padding: 4px; border: none;")
        self.player_list_wid.setObjectName(u"player_list_wid")
        self.player_list_wid.setProperty("elevation", "low")

        self.player_list_wid_lyt = QtWidgets.QVBoxLayout(self.player_list_wid)
        self.player_list_wid_lyt.setSpacing(2)
        self.player_list_wid_lyt.setObjectName(u"player_list_wid_lyt")
        self.player_list_wid_lyt.setContentsMargins(8, 8, 8, 8)

        self.lyt.addWidget(self.player_list_wid)

    def set_player_has_found(self, player_id):
        self.player_items[player_id].widget.setStyleSheet("color: #1E90FF;")

    def set_drawing_player(self, player_id):
        for item in self.player_items.values():
            if player_id == item.widget.player.id:
                item.widget.player.is_drawing = True
                item.widget.setStyleSheet("color: gold;")
            else:
                item.widget.player.is_drawing = False
                item.widget.setStyleSheet("")

    def add_player(self, player):
        item = QtWidgets.QListWidgetItem()
        widget = PlayerWidget(player, self)

        item.widget = widget
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setSizeHint(QtCore.QSize(0, 80))

        self.player_items[player.id] = item

        self.player_list_wid.addItem(item)
        self.player_list_wid.setItemWidget(item, widget)

    def remove_player(self, player_id):
        item = self.player_items[player_id]
        self.player_list_wid.takeItem(self.player_list_wid.row(item))

        del self.player_items[player_id]
        item.widget.deleteLater()

    def update_from_game(self, game):
        players = game.players.copy()
        to_remove = []
        for id, item in self.player_items.items():
            # If the player widget exists and is still in the game, update it
            if id in players:
                player = players.pop(id)
                item.widget.update_player(player)

            # If the player widget and is not in the game, remove it
            else:
                to_remove.append(id)

        # Remove is made separately to avoid dictionnary poping while looping over it
        for id in to_remove:
            self.remove_player(id)

        # All remaining players are the new ones, add a widget for each one of them
        for player in players.values():
            self.add_player(player)


class PlayerWidget(QtWidgets.QFrame):
    def __init__(self, player, parent=None):
        super(PlayerWidget, self).__init__(parent=parent)

        self.player = player
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        self.setObjectName(u"player_wid")
        self.setProperty("elevation", "medium")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("PlayerWidget{padding: 8px;}"
                           "PlayerWidget:hover{background-color:#333333}")
        self.setFixedHeight(80)

        self.lyt = QtWidgets.QHBoxLayout(self)
        self.lyt.setSpacing(8)
        self.lyt.setObjectName(u"player_wid_lyt")
        self.lyt.setContentsMargins(0, 0, 0, 0)

        self.avatar_icon = QtWidgets.QLabel(self)
        self.avatar_icon.setObjectName(u"player_avatar_icon")
        self.avatar_icon.setPixmap(QtGui.QPixmap(os.path.join(RESSOURCES_DIR,
                                                              AVATARS[self.player.avatar_id][1]))
                                  .scaledToHeight(48, QtCore.Qt.SmoothTransformation))
        self.avatar_icon.setFixedSize(64, 64)
        self.avatar_icon.setAlignment(QtCore.Qt.AlignCenter)
        self.avatar_icon.setCursor(QtCore.Qt.PointingHandCursor)

        self.lyt.addWidget(self.avatar_icon)

        self.name_lbl = QtWidgets.QLabel(self.player.name, self)
        self.name_lbl.setObjectName(u"player_name_lbl")
        self.name_lbl.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))

        self.lyt.addWidget(self.name_lbl)

        self.ranks_lyt = QtWidgets.QVBoxLayout()
        self.ranks_lyt.setObjectName(u"player_ranks_lyt")
        self.ranks_lyt.setContentsMargins(8, 0, 8, 0)

        self.lyt.addLayout(self.ranks_lyt)

        self.score_lbl = QtWidgets.QLabel(self)
        self.score_lbl.setText(str(self.player.score))
        self.score_lbl.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.score_lbl.setAlignment(QtCore.Qt.AlignRight)
        self.score_lbl.setObjectName(u"player_score_lbl")

        self.ranks_lyt.addWidget(self.score_lbl)

        self.upnext_lbl = QtWidgets.QLabel(self)
        self.upnext_lbl.setObjectName(u"player_upnext_lbl")

        self.ranks_lyt.addWidget(self.upnext_lbl)

    def setup_menu(self):
        self.menu = QtWidgets.QMenu(self.player.name, self)
        self.menu.setContentsMargins(0, 0, 0, 0)
        self.menu.setStyleSheet("padding: 0;")

        action = QtWidgets.QAction(qta.icon("fa5s.comment-dots", color="#aaaaaa"), "Private message", self.menu)
        self.menu.addAction(action)

    def mousePressEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def update_player(self, player):
        self.player = player

        if self.player.has_found:
            self.setStyleSheet("color: #1E90FF")
        elif self.player.is_drawing:
            self.setStyleSheet("color: gold")
        else:
            self.setStyleSheet("")

        self.score_lbl.setText(str(self.player.score))


if __name__ == '__main__':
    import game
    app = QtWidgets.QApplication([])

    wid = PlayersWidget()
    player = game.Player()
    player.name = "Daexs"
    player.score = 123
    player.avatar_id = 3

    wid.show()

    wid.add_player(player)

    app.exec_()