from PySide2 import QtWidgets, QtCore, QtGui
from lib.gui.utils import PainterContext, ColorDialog
import logging
import qtawesome as qta

logger = logging.getLogger("PaintView")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s %(name)s : %(message)s')
formatter.datefmt = "%H:%M:%S"
handler.setFormatter(formatter)
logger.addHandler(handler)


class Tool(object):
    tools = {}
    shortcut = None
    icon = None

    def __init__(self, view):
        self.view = view

    @property
    def cursor(self):
        return QtCore.Qt.CursorShape.ArrowCursor

    @property
    def color(self):
        return self.view.color

    def on_press(self, event):
        pass

    def on_move(self, event):
        pass

    def on_release(self, event):
        pass

    @classmethod
    def register(cls, tool_cls):
        cls.tools[tool_cls.__name__] = tool_cls


class PainterTool(Tool):
    shortcut = QtGui.QKeySequence("B")

    def __init__(self, view):
        super(PainterTool, self).__init__(view)

        self._prec_pos = None
        self._prec_size = None

        self.pen = QtGui.QPen()
        self.pen.setCapStyle(QtCore.Qt.RoundCap)

        self._cursor = None
        self.is_editing_size = False
        self._size = None
        self.size = 5

        # preview item used when modifying size
        self.size_display_item = QtWidgets.QGraphicsEllipseItem()
        self.size_display_item.setPen(QtGui.QColor("red"))
        self.view.scene.addItem(self.size_display_item)

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

        self.pen.setWidth(self.size)

        self.update_cursor()

    @property
    def cursor(self):
        return self._cursor

    def update_cursor(self):
        pix = QtGui.QPixmap(self.size, self.size)
        pix.fill(QtCore.Qt.transparent)

        with PainterContext(pix) as painter:
            painter.drawEllipse(0, 0, self.size-1, self.size-1)

        self._cursor = QtGui.QCursor(pix)

    # == EVENTS ====================================================================================

    def on_press(self, event):
        self._prec_pos = self.view.mapToScene(event.pos())

        # If alt is pressed
        if event.modifiers() & QtCore.Qt.AltModifier:
            self._prec_size = self.size

            self.show_size_display(self._prec_pos)

            self.view.setCursor(QtCore.Qt.BlankCursor)

            self.is_editing_size = True

            return False

        return True

    def on_move(self, event):
        if self.is_editing_size:
            # Set size based on the x distance from mouse click
            dist = self.view.mapToScene(event.pos()).x() - self._prec_pos.x()
            self.size = self._prec_size + dist

            # Show the circle "preview" item
            self.show_size_display(self._prec_pos)

            return False

        return True

    def on_release(self, event):
        self.size_display_item.hide()

        if self.is_editing_size:
            self.view.setCursor(self.cursor)
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
        self.paint_point(self._prec_pos)

        return True

    def on_move(self, event):
        if not super(BrushTool, self).on_move(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        pos = self.view.mapToScene(event.pos())

        self.paint_line(self._prec_pos, pos)

        self._prec_pos = pos

        return True

    def paint_point(self, pos):
        pixmap = self.view.scene.current_layer.pixmap()

        # Create painter
        with PainterContext(pixmap) as painter:
            # Set painter settings
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            self.pen.setColor(self.color)
            painter.setPen(self.pen)

            # Paint point
            painter.drawPoint(pos)
            # painter.drawEllipse(pos, self.size, self.size)

        self.view.scene.current_layer.setPixmap(pixmap)

    def paint_line(self, pos1, pos2):
        pixmap = self.view.scene.current_layer.pixmap()

        # Create painter
        with PainterContext(pixmap) as painter:
            # Set painter settings
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            self.pen.setColor(self.color)
            painter.setPen(self.pen)

            # Paint point
            painter.drawLine(pos1, pos2)

        self.view.scene.current_layer.setPixmap(pixmap)


Tool.register(BrushTool)


class EraserTool(PainterTool):
    shortcut = QtGui.QKeySequence("E")
    icon = "fa5s.eraser"

    def __init__(self, view):
        super(EraserTool, self).__init__(view)

        self._prec_pos = None

        self.pen.setColor(QtGui.QColor(255,255,0,0))

    def on_press(self, event):
        if not super(EraserTool, self).on_press(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        self.erase_point(self._prec_pos)

        return True

    def on_move(self, event):
        if not super(EraserTool, self).on_move(event):
            return False

        if not event.buttons() & QtCore.Qt.LeftButton:
            return False

        pos = self.view.mapToScene(event.pos())

        self.erase_line(self._prec_pos, pos)

        self._prec_pos = pos

    def erase_point(self, pos):
        pixmap = self.view.scene.current_layer.pixmap()

        # Create painter
        with PainterContext(pixmap) as painter:
            # Set painter settings
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            painter.setCompositionMode(painter.CompositionMode_Clear)
            painter.setPen(self.pen)

            # Paint point
            painter.drawPoint(pos)

        self.view.scene.current_layer.setPixmap(pixmap)

    def erase_line(self, pos1, pos2):
        pixmap = self.view.scene.current_layer.pixmap()

        # Create painter
        with PainterContext(pixmap) as painter:
            # Set painter settings
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            painter.setCompositionMode(painter.CompositionMode_Clear)
            painter.setPen(self.pen)

            # Paint line
            painter.drawLine(pos1, pos2)

        self.view.scene.current_layer.setPixmap(pixmap)


Tool.register(EraserTool)


class BucketTool(Tool):
    shortcut = QtGui.QKeySequence("G")
    icon = "fa5s.fill-drip"

    to_adjacent = (0, 1), (0, -1), (1, 0), (-1, 0)

    def __init__(self, view):
        super(BucketTool, self).__init__(view)

        self.tolerance = 20

    def on_press(self, event):
        if not event.buttons() & QtCore.Qt.LeftButton:
            return

        self.fill_color(self.view.mapToScene(event.pos()))

    def fill_color(self, pos):
        start_pixel = pos.x(), pos.y()
        pixmap = self.view.scene.current_layer.pixmap()
        image = pixmap.toImage()

        image_width, image_height = image.width(), image.height()

        if (start_pixel[0] < 0 or
            start_pixel[0] > image_width or
            start_pixel[1] < 0 or
            start_pixel[1] > image_width):
            return

        start_color = image.pixelColor(*start_pixel)
        fill_color = self.color
        tolerance = self.tolerance / 100. / 4.

        to_sample = {start_pixel}
        already_added = {start_pixel}

        while to_sample:
            # Take one pixel from the set of pixel to sample
            pixel = to_sample.pop()

            # Get color at pixel
            pixel_color = image.pixelColor(*pixel)

            # If pixel color is the same as start color (based on tolerance)
            if (abs(pixel_color.hslHueF() - start_color.hslHueF()) < tolerance and
                abs(pixel_color.hslSaturationF() - start_color.hslSaturationF()) < tolerance and
                abs(pixel_color.lightnessF() - start_color.lightnessF()) < tolerance and
                abs(pixel_color.alphaF() - start_color.alphaF()) < tolerance):

                x, y = pixel

                # Fill pixel color with the view's color
                image.setPixelColor(x, y, fill_color)

                # Schedule adjacent pixels in to_sample and add them to already_added so that
                # they're not tested again

                # If pixel is not on the most left column, add the pixel at its left
                if x > 0:
                    adj = (x - 1, y)
                    if adj not in already_added:
                        to_sample.add(adj)
                        already_added.add(adj)

                # If pixel is not on the most right column, add the pixel at its right
                if x < image_width:
                    adj = (x + 1, y)
                    if adj not in already_added:
                        to_sample.add(adj)
                        already_added.add(adj)

                # If pixel is not on the highest row, add the pixel at above it
                if y > 0:
                    adj = (x, y - 1)
                    if adj not in already_added:
                        to_sample.add(adj)
                        already_added.add(adj)

                # If pixel is not on the lowest row, add the pixel at under it
                if y < image_height:
                    adj = (x, y + 1)
                    if adj not in already_added:
                        to_sample.add(adj)
                        already_added.add(adj)

        self.view.scene.current_layer.setPixmap(QtGui.QPixmap.fromImage(image))


Tool.register(BucketTool)


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

    def set_current_layer(self, index=-1):
        self.current_layer = self.layers[index]


class PaintView(QtWidgets.QGraphicsView):
    image_changed = QtCore.Signal(QtGui.QPixmap)
    color_changed = QtCore.Signal(QtGui.QColor)

    TOOLS = Tool.tools

    def __init__(self, parent=None, width=1024, height=1024):
        super(PaintView, self).__init__(parent=parent)

        self.scene = Scene(self, width, height)
        self.setScene(self.scene)

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
        print(color)
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
        logger.debug("pressed " + str(event.pos()))

        # Close color dialog
        # self.color_dialog.close()

        # Propagate event to the current tool
        if self.tool.on_press(event):
            self.image_changed.emit(self.pixmap)

        # If right click is pressed : show color dialog
        if event.buttons() & QtCore.Qt.RightButton:
            self.color_dialog_requested(self.mapToGlobal(event.pos()))

        return super(PaintView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        logger.debug("moved " + str(event.pos()))

        if self.tool.on_move(event):
            self.image_changed.emit(self.pixmap)

        return super(PaintView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        logger.debug("released " + str(event.pos()))

        if self.tool.on_release(event):
            self.image_changed.emit(self.pixmap)

        return super(PaintView, self).mousePressEvent(event)
    
    def closeEvent(self, event):
        self.color_dialog.close()
        super(PaintView, self).closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    view = PaintView()
    view.show()

    app.exec_()
