from PySide2 import QtWidgets, QtCore
import qtawesome as qta

from lib.gui import paintView


class PaintWidget(QtWidgets.QWidget):
    image_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(PaintWidget, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.lyt = QtWidgets.QVBoxLayout(self)

        self.paint_view = paintView.PaintView(self)
        self.lyt.addWidget(self.paint_view)

    def make_connections(self):
        self.paint_view.image_changed.connect(self.image_changed.emit)


class PaintToolButton(QtWidgets.QPushButton):
    def __init__(self, tool, parent=None):
        super(PaintToolButton, self).__init__(parent=parent)

        self.tool = tool
        self.setIcon(qta.icon(self.tool.icon))
