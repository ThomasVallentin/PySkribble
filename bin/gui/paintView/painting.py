from gui.utils import PainterContext
from PySide2 import QtGui, QtCore


def paint_point(pixmap, pos, width, color):

    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        # Create and set pen
        pen = QtGui.QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint point
        painter.drawPoint(pos)

    return pixmap


def paint_line(pixmap, pos1, pos2, width, color):

    # Create painter
    with PainterContext(pixmap) as painter:
        # Set painter settings
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        # Create and set pen
        pen = QtGui.QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Paint line
        painter.drawLine(pos1, pos2)

    return pixmap
