from PySide2 import QtWidgets, QtCore, QtGui

from gui.components.iconButton import IconButton
from gui.utils import SignalsBlocked


class FramelessWindowMixin(object):
    def __init__(self, parent=None):
        """
        :param bin.app.Skribble client: the client linked to this instance
        :param QtWidgets.QObject parent:
        """
        super(FramelessWindowMixin, self).__init__(parent=parent)

        self.is_dragged = False
        self._drag_start_pos = None

        self.lyt = None
        self.menu_lyt = None
        self.close_btn = None

    def setup_ui(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.lyt = QtWidgets.QVBoxLayout(self)
        self.lyt.setSpacing(16)
        self.lyt.setObjectName(u"lyt")
        self.lyt.setContentsMargins(16, 16, 16, 16)

        self.menu_lyt = QtWidgets.QHBoxLayout()
        self.lyt.addLayout(self.menu_lyt)

        self.close_btn = IconButton(("fa5s.times-circle", "#ff3333"), parent=self)
        self.close_btn.setStyleSheet("background-color: transparent;")
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setIconSize(QtCore.QSize(32, 32))
        self.menu_lyt.addWidget(self.close_btn, 0, QtCore.Qt.AlignRight)

    def make_connections(self):
        self.close_btn.clicked.connect(self.on_close)

    def on_close(self):
        self.close()

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.y() < 56:
            self.is_dragged = True

        self._drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.is_dragged:
            return

        new_pos = self.pos() + event.pos() - self._drag_start_pos

        self.move(new_pos)

    def mouseReleaseEvent(self, event):
        self.is_dragged = False
