from PySide2 import QtWidgets, QtCore, QtGui


class Tool(object):
    tools = {}

    def __init__(self, view):
        self.view = view

    def on_press(self, event):
        pass

    def on_move(self, event):
        pass

    def on_release(self, event):
        pass

    @classmethod
    def register_tool(cls, tool_cls):
        cls.tools[tool_cls.__name__] = tool_cls


class BrushTool(Tool):
    def __init__(self, view):
        super(BrushTool, self).__init__(view)

        self.current_item = None

        self._size = 5
        self._color = QtGui.QColor("red")

    # == SIZE ==

    @property
    def size(self):
        return self._size

    def set_size(self, size):
        self._size = size

    # == COLOR ==

    @property
    def color(self):
        return self._color

    def set_color(self, color):
        self._color = coloraze

    # == EVENTS ====================================================================================

    def on_press(self, event):
        self.create_path(self.view.mapToScene(event.pos()))

    def on_move(self, event):
        self.add_pos_to_current_path(self.view.mapToScene(event.pos()))

    def on_release(self, event):
        self.current_item = None

    def create_path(self, start_pos=None):
        pen = QtGui.QPen(self.color)
        pen.setWidth(self.size)

        path = QtGui.QPainterPath(start_pos)

        item = QtWidgets.QGraphicsPathItem()
        item.setPath(path)
        item.setPen(pen)

        self.view.scene.addItem(item)
        self.current_item = item

    def add_pos_to_current_path(self, pos):
        if not self.current_item:
            return False

        path = self.current_item.path()
        path.lineTo(pos)

        self.current_item.setPath(path)

        return True


Tool.register_tool(BrushTool)


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, view, width=1024, height=1024):
        super(Scene, self).__init__()
        self.view = view

        self.layers = []
        self.current_layer = None

        self.setSceneRect(0, 0, width, height)

    def add_layer(self):
        layer = QtWidgets.QGraphicsPixmapItem()

        pixmap = QtGui.QPixmap(self.width(), self.height())
        layer.setPixmap(pixmap)

        self.addItem(layer)
        self.layers.append(layer)

    def set_current_layer(self, index=-1):
        self.current_layer = self.layers[index]


class PaintView(QtWidgets.QGraphicsView):
    TOOLS = Tool.tools

    def __init__(self, parent=None):
        super(PaintView, self).__init__(parent=parent)

        self.scene = Scene(self)
        self.setScene(self.scene)

        # Tools
        self.tools = {name: tool(self) for name, tool in self.TOOLS.items()}
        self._tool = None

        self.set_tool("BrushTool")

    # == TOOLS =====================================================================================

    @property
    def tool(self):
        return self._tool

    def set_tool(self, value):
        if isinstance(value, Tool):
            self._tool = value

        elif value not in self.tools:
            raise ValueError(f"Wrong tool : {value}")

        self._tool = self.tools[value]

    # == EVENTS ====================================================================================

    def mousePressEvent(self, event):
        print("pressed", event.pos())

        self.tool.on_press(event)

        return super(PaintView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        print("moved", event.pos())

        self.tool.on_move(event)

        return super(PaintView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        print("released", event.pos())

        self.tool.on_release(event)

        return super(PaintView, self).mousePressEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    view = PaintView()
    view.show()

    app.exec_()

    print("End")
