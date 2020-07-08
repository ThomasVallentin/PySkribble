from PySide2 import QtWidgets, QtCore, QtGui


class ScoreBoard(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(ScoreBoard, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ScoreBoard")
        self.setFixedWidth(620)
        self.setColumnCount(3)
        self.setShowGrid(False)
        self.setStyleSheet("QWidget{"
                                 "background-color: transparent;"
                                 "color: white;"
                                 "}")
        self.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Black))

        self.setHorizontalHeaderLabels(("PLAYER", "ROUND SCORE", "GLOBAL SCORE"))
        self.horizontalHeader().setFont(QtGui.QFont("Arial", 14))
        self.horizontalHeader().setDefaultSectionSize(200)
        self.horizontalHeader().setStyleSheet("QHeaderView::section{"
                                                    "background-color:transparent;"
                                                    "color: #1E90FF;}")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setFixedHeight(50)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def add_player_score(self, player):
        row = self.rowCount()
        self.insertRow(row)
        for col, text in enumerate((player.name, player.round_score, player.score)):
            item = QtWidgets.QTableWidgetItem(str(text))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(row, col, item)

    def update_from_game(self, game):
        for i in range(self.rowCount()):
            self.removeRow(0)

        for player in sorted(game.players.values(),
                             key=lambda ply: (ply.round_score, ply.name),
                             reverse=True):
            self.add_player_score(player)


if __name__ == '__main__':
    import game

    app = QtWidgets.QApplication([])

    wid = ScoreBoard()
    player = game.Player()
    player.name = "Daexs"
    player.score = 123
    player.avatar_id = 3

    wid.show()

    wid.add_player_score(player)
    wid.add_player_score(player)
    wid.add_player_score(player)

    app.exec_()
