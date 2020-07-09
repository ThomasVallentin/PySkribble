from PySide2 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from functools import partial

from gui.paintView.view import PaintView


class PaintWidget(QtWidgets.QWidget):
    COLOR_PALETTE = ("#FF3020", "#FF4081", "#F57C00", "#FFC107", "#FFCCBC", "#FFFFFF",
                     "#4CAF50", "#2196F3", "#3F51B5", "#9C27B0", "#915A46", "#000000")
    painted = QtCore.Signal(tuple)

    def __init__(self, parent=None, width=1000, height=562):
        super(PaintWidget, self).__init__(parent=parent)
        # self.setStyleSheet("border: 1px solid red;")

        self.setup_ui(width, height)
        self.make_connections()

    def setup_ui(self, width, height):
        self.lyt = QtWidgets.QVBoxLayout(self)

        self.paint_view = PaintView(self, width, height, base_color=QtCore.Qt.white)
        self.paint_view.setStyleSheet("PaintView{background-color: white;}")

        self.paint_view.scene.add_layer(switch=True)

        self.lyt.addWidget(self.paint_view)

        self.toolbox_lyt = QtWidgets.QHBoxLayout()
        self.build_toolbox()
        self.lyt.addLayout(self.toolbox_lyt)

    def build_toolbox(self):
        for name, tool in sorted(self.paint_view.tools.items()):
            btn = PaintToolButton(self, tool)
            self.toolbox_lyt.addWidget(btn)

        self.color_palette_wid = QtWidgets.QWidget(self)
        self.color_palette_wid.setFixedSize(206, 50)
        self.toolbox_lyt.addWidget(self.color_palette_wid)

        self.color_palette_lyt = QtWidgets.QGridLayout(self.color_palette_wid)
        self.color_palette_lyt.setSpacing(2)
        self.color_palette_lyt.setContentsMargins(0, 0, 0, 0)

        for i, color in enumerate(self.COLOR_PALETTE):
            btn = QtWidgets.QPushButton(self)
            btn.setMaximumSize(256, 256)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet("background-color: " + color)
            btn.clicked.connect(partial(self.paint_view.set_color, color))

            self.color_palette_lyt.addWidget(btn, i/6, i%6)

        self.color_choice_btn = QtWidgets.QPushButton(self)
        self.color_choice_btn.setFixedSize(50, 50)
        self.color_choice_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_color_display(self.paint_view.color)
        self.color_palette_lyt.addWidget(self.color_choice_btn,
                                         0, self.color_palette_lyt.columnCount(),
                                         2, 2)

    def update_color_display(self, color):
        self.color_choice_btn.setStyleSheet("background-color: {}".format(color.name()))

    def color_choice_requested(self):
        dialog_heigt = self.paint_view.color_dialog.height()

        pos = self.color_choice_btn.mapToGlobal(QtCore.QPoint(0, dialog_heigt * -1 - 8))

        self.paint_view.color_dialog_requested(pos)

    def make_connections(self):
        self.paint_view.painted.connect(self.painted.emit)
        self.paint_view.color_changed.connect(self.update_color_display)
        self.color_choice_btn.clicked.connect(self.color_choice_requested)

    def paint_from_message(self, typ, *args):
        if typ == "paint_point":
            self.paint_view.paint_point(QtCore.QPoint(*args[0]), args[1],
                                        QtGui.QColor(args[2]), silent=True)
        elif typ == "paint_line":
            self.paint_view.paint_line(QtCore.QPoint(*args[0]), QtCore.QPoint(*args[1]),
                                       args[2], QtGui.QColor(args[3]), silent=True)

        elif typ == "erase_point":
            self.paint_view.erase_point(QtCore.QPoint(*args[0]), args[1], silent=True)

        elif typ == "erase_line":
            self.paint_view.erase_line(QtCore.QPoint(*args[0]), QtCore.QPoint(*args[1]),
                                       args[2], silent=True)

        if typ == "bucket_fill":
            self.paint_view.bucket_fill(QtCore.QPoint(*args[0]), QtGui.QColor(args[1]),
                                        silent=True)

    def lock(self):
        self.paint_view.lock()

    def unlock(self):
        self.paint_view.unlock()


class PaintToolButton(QtWidgets.QPushButton):
    def __init__(self, paint_widget, tool):
        super(PaintToolButton, self).__init__(parent=paint_widget)

        self.tool = tool
        self.paint_widget = paint_widget

        self.setFlat(True)
        self.setFixedSize(35, 35)
        self.setIcon(qta.icon(self.tool.icon, color="#aaaaaa"))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("font-size: 10px; text-align: top; color: #757575;")
        self.setText(self.tool.shortcut.toString())

        self.clicked.connect(lambda: self.paint_widget.paint_view.set_tool(tool))
