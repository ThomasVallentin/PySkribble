from PySide2 import QtWidgets, QtCore, QtGui

import os
import random

from constants import AVATARS
from gui.components.framelessWindow import FramelessWindowMixin
from gui.components.iconButton import IconButton
from gui import utils as gui_utils

from constants import RESSOURCES_DIR


class ConnectDialog(FramelessWindowMixin, QtWidgets.QDialog):
    style = "ConnectWidget{border-radius: 8px;}"

    def __init__(self, client, parent=None):
        super(ConnectDialog, self).__init__(parent=parent)
        self.client = client

        self.result = None

        self._avatar_pixmaps = []
        self._avatar_id = 0

        self.setup_ui()
        self.make_connections()

        self.load_avatars()
        self.set_avatar(random.randint(0, len(AVATARS) - 1))

        self.name_lne.setFocus(QtCore.Qt.MouseFocusReason)

    def setup_ui(self):
        super(ConnectDialog, self).setup_ui()

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(650, 400)
        self.setProperty("elevation", "low")

        self.content_lyt = QtWidgets.QHBoxLayout()
        self.content_lyt.setSpacing(16)
        self.lyt.addLayout(self.content_lyt)

        self.left_wid = QtWidgets.QWidget(self)
        self.content_lyt.addWidget(self.left_wid)

        self.left_lyt = QtWidgets.QVBoxLayout(self.left_wid)
        self.left_lyt.setContentsMargins(0, 0, 0, 0)

        self.logo_lbl = QtWidgets.QLabel(self)
        self.logo_lbl.setPixmap(QtGui.QPixmap(os.path.join(RESSOURCES_DIR, "connect_title.png")))
        # self.logo_lbl.setText('<p style="line-height: 0.7; font: 32pt Arial black">BETTER<br>SKRIBBL</p>')
        # self.logo_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_lbl.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                          QtWidgets.QSizePolicy.Expanding))
        self.left_lyt.addWidget(self.logo_lbl)

        self.name_lyt = QtWidgets.QVBoxLayout()
        self.name_lyt.setContentsMargins(0, 0, 0, 0)
        self.name_lyt.setSpacing(8)
        self.left_lyt.addLayout(self.name_lyt)

        self.name_lne = QtWidgets.QLineEdit(self)
        self.name_lne.setPlaceholderText("Enter your name")
        self.name_lne.setFont(QtGui.QFont("Arial", 11))
        self.name_lyt.addWidget(self.name_lne)

        self.join_btn = QtWidgets.QPushButton("Join !", self)
        self.join_btn.setFixedHeight(50)
        self.join_btn.setProperty("importance", "primary")
        self.join_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.join_btn.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.name_lyt.addWidget(self.join_btn)

        self.status_line = QtWidgets.QLabel(self)
        self.status_line.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                             QtWidgets.QSizePolicy.Minimum))
        self.status_line.setStyleSheet("color: red;")
        self.status_line.setWordWrap(True)
        # self.status_line.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.name_lyt.addWidget(self.status_line)

        self.avatar_wid = QtWidgets.QWidget(self)
        self.avatar_wid.setProperty("elevation", "medium")
        self.avatar_wid.setStyleSheet("border-radius: 12px;")
        self.content_lyt.addWidget(self.avatar_wid)

        self.avatar_lyt = QtWidgets.QVBoxLayout(self.avatar_wid)

        self.avatar_lbl = QtWidgets.QLabel(self)
        self.avatar_lbl.setFixedWidth(300)
        self.avatar_lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.avatar_lyt.addWidget(self.avatar_lbl)

        self.avatar_choice_lyt = QtWidgets.QHBoxLayout()
        self.avatar_lyt.addLayout(self.avatar_choice_lyt)

        self.prev_avatar_btn = IconButton(("fa5s.chevron-circle-left", "#FF0058"), parent=self)
        self.prev_avatar_btn.setStyleSheet("background-color: transparent;")
        self.prev_avatar_btn.setFixedSize(32, 32)
        self.prev_avatar_btn.setIconSize(QtCore.QSize(32,32))
        self.prev_avatar_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.avatar_choice_lyt.addWidget(self.prev_avatar_btn)

        self.avatar_name_lbl = QtWidgets.QLabel()
        self.avatar_name_lbl.setFixedWidth(150)
        self.avatar_name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.avatar_name_lbl.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.avatar_choice_lyt.addWidget(self.avatar_name_lbl)

        self.next_avatar_btn = IconButton(("fa5s.chevron-circle-right", "#FF0058"), parent=self)
        self.next_avatar_btn.setStyleSheet("background-color: transparent;")
        self.next_avatar_btn.setFixedSize(32, 32)
        self.next_avatar_btn.setIconSize(QtCore.QSize(32,32))
        self.next_avatar_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.avatar_choice_lyt.addWidget(self.next_avatar_btn)

    def make_connections(self):
        super(ConnectDialog, self).make_connections()
        self.prev_avatar_btn.clicked.connect(lambda: self.set_avatar(self._avatar_id - 1))
        self.next_avatar_btn.clicked.connect(lambda: self.set_avatar(self._avatar_id + 1))
        self.join_btn.clicked.connect(self.connect_to_socket)

    def load_avatars(self):
        for avatar, image_path in AVATARS:
            pix = QtGui.QPixmap(image_path)
            pix = pix.scaledToHeight(250, QtCore.Qt.SmoothTransformation)
            self._avatar_pixmaps.append(pix)

    def set_avatar(self, index):
        index = index % len(AVATARS)
        self.avatar_lbl.setPixmap(self._avatar_pixmaps[index])
        self.avatar_name_lbl.setText(AVATARS[index][0])

        self._avatar_id = index

    def connect_to_socket(self):
        self.client._name = self.name_lne.text()
        self.client._avatar_id = self._avatar_id

        with gui_utils.BusyCursor():
            connection_error = self.client.start()

        if connection_error:
            self.status_line.setText(str(connection_error))
        else:
            self.accept()

    def accept(self):
        self.result = True
        super(ConnectDialog, self).accept()
    
    def reject(self):
        self.result = False
        super(ConnectDialog, self).reject()

    def exec_(self):
        super(ConnectDialog, self).exec_()

        return self.result

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.connect_to_socket()

        elif event.key() == QtCore.Qt.Key_Escape:
            self.reject()
