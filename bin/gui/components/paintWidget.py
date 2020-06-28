from PySide2 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from gui.paintView.view import PaintView


class PaintWidget(QtWidgets.QWidget):
    painted = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super(PaintWidget, self).__init__(parent=parent)

        self.setup_ui()
        self.make_connections()

    def setup_ui(self):
        self.lyt = QtWidgets.QVBoxLayout(self)

        self.paint_view = PaintView(self, 1000, 562)
        self.paint_view.setStyleSheet("background-color: white;")
        self.lyt.addWidget(self.paint_view)

        self.toolbox_lyt = QtWidgets.QHBoxLayout()
        self.build_toolbox()
        self.lyt.addLayout(self.toolbox_lyt)

    def build_toolbox(self):
        for name, tool in sorted(self.paint_view.tools.items()):
            btn = PaintToolButton(self, tool)
            self.toolbox_lyt.addWidget(btn)

        self.color_choice_btn = QtWidgets.QPushButton(self)
        self.color_choice_btn.setFixedSize(35, 35)
        self.color_choice_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_color_display(self.paint_view.color)
        self.toolbox_lyt.addWidget(self.color_choice_btn)

    def update_color_display(self, color):
        self.color_choice_btn.setStyleSheet("border-radius: 2px; "
                                            "background-color: {}".format(color.name()))

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
                                        QtGui.QColor(args[2]),
                                        silent=True)
        elif typ == "paint_line":
            self.paint_view.paint_line(QtCore.QPoint(*args[0]), QtCore.QPoint(*args[1]),
                                       args[2], QtGui.QColor(args[3]), silent=True)

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
