from PySide2 import QtWidgets, QtCore, QtGui

from gui.utils import ColorDialog
from gui.paintView.tools import Tool
from gui.paintView import painting as paint
from lib import logger as log

logger = log.Logger("PaintView", level=log.INFO)


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, view, width=1024, height=1024):
        super(Scene, self).__init__()
        self.view = view

        self.layers = []
        self.current_layer = None

        self.setSceneRect(0, 0, width, height)

        self.add_layer()
        self.set_current_layer(0)

    @property
    def pixmap(self):
        return self.layers[0].pixmap()

    def add_layer(self):
        pixmap = QtGui.QPixmap(self.width(), self.height())
        pixmap.fill(QtCore.Qt.transparent)

        item = self.addPixmap(pixmap)
        self.layers.append(item)

    def set_current_layer(self, index):
        self.current_layer = self.layers[index]

    def clear(self):
        pixmap = QtGui.QPixmap(self.width(), self.height())
        pixmap.fill(QtCore.Qt.transparent)

        self.current_layer.setPixmap(pixmap)


class PaintView(QtWidgets.QGraphicsView):
    painted = QtCore.Signal(tuple)
    color_changed = QtCore.Signal(QtGui.QColor)

    TOOLS = Tool.tools

    def __init__(self, parent=None, width=1024, height=1024):
        super(PaintView, self).__init__(parent=parent)

        self.scene = Scene(self, width, height)
        self.setScene(self.scene)

        self._locked = False

        # Colors
        self._color = None
        self.color = "black"

        self.color_dialog = ColorDialog()
        self.color_dialog.hide()
        self.color_dialog.currentColorChanged.connect(self.set_color)

        # Tools
        self.tools = {}
        self._tool = None

        self.install_tools(self.TOOLS)

        self.set_tool("BrushTool")

    @property
    def locked(self):
        return self._locked

    @property
    def pixmap(self):
        return self.scene.pixmap

    # == COLOR =====================================================================================

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, *args):
        self._color = QtGui.QColor(*args)
        self.color_changed.emit(self._color)

    def set_color(self, color):
        self.color = color

    # == TOOLS =====================================================================================

    def install_tool(self, name, cls):
        tool = cls(self)
        if tool.shortcut:
            # Create ShortCut
            shortcut = QtWidgets.QShortcut(tool.shortcut, self)
            shortcut.activated.connect(lambda: self.set_tool(tool))

        self.tools[name] = tool

    def install_tools(self, tools_dict):
        for name, tool_cls in tools_dict.items():
            self.install_tool(name, tool_cls)

    @property
    def tool(self):
        return self._tool

    def set_tool(self, tool):
        if not isinstance(tool, Tool):
            if tool not in self.tools:
                raise ValueError(f"Wrong tool : {tool}")

            tool = self.tools[tool]

        self._tool = tool

        self.setCursor(tool.cursor)

        logger.debug(f"Tool set to {tool.__class__.__name__}")

    def color_dialog_requested(self, global_pos):
        self.color_dialog.move(global_pos)

        return self.color_dialog.show()

    # == EVENTS ====================================================================================

    def mousePressEvent(self, event):
        # logger.debug("pressed " + str(event.pos()))

        if self.locked:
            return

        # Propagate event to the current tool
        self.tool.on_press(event)

        # If right click is pressed : show color dialog
        if event.buttons() & QtCore.Qt.RightButton:
            self.color_dialog_requested(self.mapToGlobal(event.pos()))

        return super(PaintView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # logger.debug("moved " + str(event.pos()))

        if self.locked:
            return

        self.tool.on_move(event)

        return super(PaintView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # logger.debug("released " + str(event.pos()))

        if self.locked:
            return

        self.tool.on_release(event)

        return super(PaintView, self).mousePressEvent(event)
    
    def closeEvent(self, event):
        self.color_dialog.close()
        super(PaintView, self).closeEvent(event)

    def clear(self):
        self.scene.clear()

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def paint_point(self, pos, width, color, silent=False):
        pixmap = paint.paint_point(self.scene.current_layer.pixmap(), pos, width, color)

        self.scene.current_layer.setPixmap(pixmap)

        if not silent:
            self.painted.emit(("paint_point", pos.toTuple(), width, color.name()))

    def paint_line(self, pos1, pos2, width, color, silent=False):
        pixmap = paint.paint_line(self.scene.current_layer.pixmap(), pos1, pos2, width, color)

        self.scene.current_layer.setPixmap(pixmap)

        if not silent:
            self.painted.emit(("paint_line",
                               pos1.toTuple(), pos2.toTuple(),
                               width, color.name()))

    def erase_point(self, pos, width, silent=False):
        pixmap = paint.erase_point(self.scene.current_layer.pixmap(), pos, width)

        self.scene.current_layer.setPixmap(pixmap)

        if not silent:
            self.painted.emit(("erase_point", pos.toTuple(), width))

    def erase_line(self, pos1, pos2, width, silent=False):
        pixmap = paint.erase_line(self.scene.current_layer.pixmap(),
                                  pos1, pos2, width)

        self.scene.current_layer.setPixmap(pixmap)

        if not silent:
            self.painted.emit(("erase_line", pos1.toTuple(), pos2.toTuple(), width))

    def bucket_fill(self, pos, color, silent=False):
        pixmap = paint.bucket_fill(self.scene.current_layer.pixmap(), pos, color)

        self.scene.current_layer.setPixmap(pixmap)

        if not silent:
            self.painted.emit(("bucket_fill", pos.toTuple(), color.name()))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    view = PaintView()
    view.show()

    app.exec_()
