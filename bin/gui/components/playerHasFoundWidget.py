from PySide2 import QtWidgets, QtCore, QtGui

import os

from constants import RESSOURCES_DIR
from gui.utils import PainterContext


class PlayerHasFoundWidget(QtWidgets.QLabel):
    _text_rect = QtCore.QRect(223, 326, 66, 66)

    dismiss = QtCore.Signal()

    def __init__(self, parent=None):
        super(PlayerHasFoundWidget, self).__init__(parent=parent)

        self.set_rank(0)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("PlayerHasFoundWidget")
        self.setStyleSheet("background-color: transparent")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self.setMask(self.pixmap().createMaskFromColor(QtCore.Qt.transparent,
                                                       QtCore.Qt.MaskInColor))

    def mousePressEvent(self, event):
        self.dismiss.emit()

    def set_rank(self, rank=0):
        pixmap = QtGui.QPixmap(os.path.join(RESSOURCES_DIR, "FoundSticker.png"))

        with PainterContext(pixmap) as painter:
            painter.setFont(QtGui.QFont("Arial", 36, QtGui.QFont.Black))
            painter.setPen(QtGui.QColor("white"))
            painter.setRenderHints(painter.Antialiasing)
            painter.drawText(self._text_rect, QtCore.Qt.AlignCenter, str(rank))

        self.setPixmap(pixmap)
