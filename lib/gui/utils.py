from PySide2 import QtWidgets, QtCore, QtGui
from lib import contextDecorators as ctx


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
        print(widget)
        if isinstance(widget, QtWidgets.QWidget):
            print("hide")
            widget.hide()
        else:
            print("recurse")
            for child in widget.children():
                ColorDialog.hide_recursive(child)


if __name__ == '__main__':
    col = QtGui.QColor("#45a658")
    print(col.value())
    print(col.toHsl())
    print(col.toHsv())