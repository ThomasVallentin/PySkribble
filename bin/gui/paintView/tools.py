from PySide2 import QtWidgets, QtCore, QtGui
from gui.utils import PainterContext
from gui.paintView import painting as paint


class Tool(object):
    tools = {}
    shortcut = None
    icon = None

    def __init__(self, view):
        self.view = view

        self.default_cursor = QtCore.Qt.CursorShape.ArrowCursor
        self.cursor = self.default_cursor

    def on_press(self, event):
        return True

    def on_move(self, event):
        return True

    def on_release(self, event):
        return True

    def on_key_press(self, event):
        return True

    def on_key_release(self, event):
        return True

    @classmethod
    def register(cls, tool_cls):
        cls.tools[tool_cls.__name__] = tool_cls


class ColorTool(Tool):
    eye_dropper_cursor = QtGui.QCursor(QtGui.QPixmap("ressources/EyeDropper.png"), 1, 23)

    def __init__(self, view):
        super(ColorTool, self).__init__(view)

        self.alt_pressed = False

    @property
    def color(self):
        return self.view.color

    def on_press(self, event):
        if event.modifiers() & QtCore.Qt.AltModifier:
            self.cursor = self.eye_dropper_cursor

            # Pick color on alt + click
            if event.button() == QtCore.Qt.LeftButton:
                self.view.pick_color(event.pos())
                return False

        # If right click is pressed : show color dialog
        elif event.buttons() & QtCore.Qt.RightButton:
            self.view.color_dialog_requested(self.view.mapToGlobal(event.pos()))

        return True

    def on_move(self, event):
        if event.modifiers() & QtCore.Qt.AltModifier:

            self.cursor = self.eye_dropper_cursor

            if event.buttons() & QtCore.Qt.LeftButton:
                return False

        else:
            self.cursor = self.default_cursor

        return True

    def on_key_press(self, event):
        if event.key() == QtCore.Qt.Key_Alt:
            self.cursor = self.eye_dropper_cursor

    def on_key_release(self, event):
        if event.key() == QtCore.Qt.Key_Alt:
            self.cursor = self.default_cursor


class PainterTool(ColorTool):
    def __init__(self, view):
        super(PainterTool, self).__init__(view)

        self._prec_pos = None
        self._prec_size = None

        self.is_editing_size = False
        self._size = None
        self.size = 5

        # preview item used when modifying size
        self.size_display_item = QtWidgets.QGraphicsEllipseItem()
        self.size_display_item.setPen(QtGui.QColor("red"))
        self.size_display_item.setZValue(99999)
        self.view.scene.addItem(self.size_display_item)

        self.update_cursor()

    # == SIZE ======================================================================================

    def show_size_display(self, pos):
        self.size_display_item.show()
        self.size_display_item.setRect(pos.x() - self.size / 2,
                                       pos.y() - self.size / 2,
                                       self.size,
                                       self.size)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = max(0.1, size)

        self.update_cursor()

    def update_cursor(self):
        pix = QtGui.QPixmap(self.size, self.size)
        pix.fill(QtCore.Qt.transparent)

        with PainterContext(pix) as painter:
            painter.drawEllipse(1, 1, self.size-2, self.size-2)

        self.default_cursor = QtGui.QCursor(pix)

    # == EVENTS ====================================================================================

    def on_press(self, event):
        if not super(PainterTool, self).on_press(event):
            return False

        self._prec_pos = self.view.mapToScene(event.pos())

        # If alt is pressed
        if event.modifiers() & QtCore.Qt.AltModifier and event.button() == QtCore.Qt.RightButton:
            self._prec_size = self.size

            self.show_size_display(self._prec_pos)

            self.cursor = QtCore.Qt.BlankCursor

            self.is_editing_size = True

            return False

        return True

    def on_move(self, event):
        if not super(PainterTool, self).on_move(event):
            return False

        if self.is_editing_size:
            # Set size based on the x distance from mouse click
            dist = self.view.mapToScene(event.pos()).x() - self._prec_pos.x()
            self.size = self._prec_size + dist

            self.cursor = QtCore.Qt.BlankCursor

            # Show the circle "preview" item
            self.show_size_display(self._prec_pos)

            return False

        if not event.modifiers() & QtCore.Qt.AltModifier:
            self.cursor = self.default_cursor

        return True

    def on_release(self, event):
        self.size_display_item.hide()

        if self.is_editing_size:
            self.cursor = self.default_cursor

            self.is_editing_size = False


class BrushTool(PainterTool):
    shortcut = QtGui.QKeySequence("B")
    icon = "fa5s.paint-brush"

    def __init__(self, view):
        super(BrushTool, self).__init__(view)

        self._current_layer = None

    # == EVENTS ====================================================================================

    def on_press(self, event):
        if not super(BrushTool, self).on_press(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        # if alt is not pressed
        self.view.paint_point(self._prec_pos, self.size, self.color)

        return True

    def on_move(self, event):
        if not super(BrushTool, self).on_move(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        pos = self.view.mapToScene(event.pos())

        self.view.paint_line(self._prec_pos, pos, self.size, self.color)

        self._prec_pos = pos

        return True


Tool.register(BrushTool)


class EraserTool(PainterTool):
    shortcut = QtGui.QKeySequence("E")
    icon = "fa5s.eraser"

    def __init__(self, view):
        super(EraserTool, self).__init__(view)

        self._prec_pos = None

    def on_press(self, event):
        if not super(EraserTool, self).on_press(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        self.view.erase_point(self._prec_pos, self.size)

        return True

    def on_move(self, event):
        if not super(EraserTool, self).on_move(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        pos = self.view.mapToScene(event.pos())

        self.view.erase_line(self._prec_pos, pos, self.size)

        self._prec_pos = pos


Tool.register(EraserTool)


class BucketTool(ColorTool):
    shortcut = QtGui.QKeySequence("G")
    icon = "fa5s.fill-drip"

    to_adjacent = (0, 1), (0, -1), (1, 0), (-1, 0)

    def __init__(self, view):
        super(BucketTool, self).__init__(view)

        self.tolerance = 20
        self.default_cursor = QtGui.QCursor(QtGui.QPixmap("ressources/BucketFill.png"), 23, 20)

    def on_press(self, event):
        if not event.buttons() & QtCore.Qt.LeftButton:
            return

        self.view.bucket_fill(self.view.mapToScene(event.pos()), self.color)


Tool.register(BucketTool)
