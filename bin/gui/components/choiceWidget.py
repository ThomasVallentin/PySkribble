from PySide2 import QtWidgets, QtCore, QtGui

from functools import partial


class ChoiceWidget(QtWidgets.QFrame):
    choice_made = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(ChoiceWidget, self).__init__(parent=parent)

        self.result = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ChoiceWidget")
        self.setStyleSheet("ChoiceWidget{background-color: rgba(0, 0, 0, 120);}")

        self.lyt = QtWidgets.QVBoxLayout(self)

        dummy = QtWidgets.QWidget(self)
        self.lyt.addWidget(dummy)

        self.title_lbl = QtWidgets.QLabel("Pick a word and start drawing it !", self)
        self.title_lbl.setFont(QtGui.QFont("Arial", 32, QtGui.QFont.Black))
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setStyleSheet("color: white")
        self.title_lbl.setFixedHeight(60)

        self.lyt.addWidget(self.title_lbl)

        self.choices_lyt = QtWidgets.QHBoxLayout(self)
        self.choices_lyt.setContentsMargins(128, 64, 128, 64)
        self.choices_lyt.setSpacing(32)

        self.lyt.addLayout(self.choices_lyt)

        dummy = QtWidgets.QWidget(self)
        self.lyt.addWidget(dummy)

    def load_choices(self, choices):
        for i, choice in enumerate(choices):
            choice_btn = QtWidgets.QPushButton(choice, self)
            choice_btn.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
            choice_btn.setFixedHeight(64)
            choice_btn.setCursor(QtCore.Qt.PointingHandCursor)
            choice_btn.setProperty("importance", "primary")
            choice_btn.index = i
            choice_btn.clicked.connect(partial(self.choice_made.emit, i))

            self.choices_lyt.addWidget(choice_btn)

    def mousePressEvent(self, event):
        return False
