from PySide2 import QtWidgets, QtCore, QtGui


class ScoreBoard(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ScoreBoard, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ScoreBoard")
        self.setStyleSheet("ScoreBoard{background-color: rgba(0, 0, 0, 180)}")
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                 QtWidgets.QSizePolicy.Expanding))
        self.lyt = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setFixedWidth(620)
        self.table.setColumnCount(3)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("QWidget{"
                                 "background-color: transparent;"
                                 "color: white;"
                                 "}")
        self.table.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Black))

        self.table.setHorizontalHeaderLabels(("PLAYER", "ROUND SCORE", "GLOBAL SCORE"))
        self.table.horizontalHeader().setFont(QtGui.QFont("Arial", 14))
        self.table.horizontalHeader().setDefaultSectionSize(200)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section{"
                                                    "background-color:transparent;"
                                                    "color: #1E90FF;}")
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(50)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)

        self.lyt.addWidget(self.table, 0, QtCore.Qt.AlignCenter)

    def add_player_score(self, player):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, text in enumerate((player.name, player.round_score, player.score)):
            item = QtWidgets.QTableWidgetItem(str(text))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, col, item)

    def update_from_game(self, game):
        for i in range(self.table.rowCount()):
            self.table.removeRow(0)

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
