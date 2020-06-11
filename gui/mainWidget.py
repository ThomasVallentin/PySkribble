from PySide2 import QtWidgets, QtCore, QtGui


class SkribblWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SkribblWidget, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.lyt = QtWidgets.Q