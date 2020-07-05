from PySide2 import QtWidgets, QtCore, QtGui
from lib import contextDecorators as ctx


class BusyCursor(ctx.ContextDecorator):
    def __enter__(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        QtWidgets.QApplication.restoreOverrideCursor()


class SignalsBlocked(ctx.ContextDecorator):
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        self.widget.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)


class PainterContext(ctx.ContextDecorator):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.painter = None

    def __enter__(self):
        self.painter = QtGui.QPainter(*self.args, **self.kwargs)

        return self.painter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.painter.end()


class ColorDialog(QtWidgets.QColorDialog):
    def __init__(self, parent=None):
        super(ColorDialog, self).__init__(parent=parent)

        self.setOptions(self.NoButtons)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.setWindowFlags(QtCore.Qt.Popup)
        self.setStyleSheet("QWidget{"
                           "  background-color: #333333; "
                           "  color: #aaaaaa; "
                           "  border: none; "
                           "  border-radius: 2px;}"
                           ""
                           "QLineEdit,QSpinBox{"
                           "  background-color: #222222;"
                           "}")
        self.layout().children()[0].takeAt(0)
        for i in range(1, 8):
            self.children()[i].hide()

    @staticmethod
    def hide_recursive(widget):
        if isinstance(widget, QtWidgets.QWidget):
            widget.hide()
        else:
            for child in widget.children():
                ColorDialog.hide_recursive(child)


def pixmap_to_bytes(pixmap, save_type="PNG"):
    bytarr = QtCore.QByteArray()
    buf = QtCore.QBuffer(bytarr)
    buf.open(QtCore.QIODevice.WriteOnly)

    pixmap.save(buf, save_type)

    return bytarr.data()


if __name__ == '__main__':
    col = QtGui.QColor("#45a658")