from PySide2 import QtWidgets, QtGui
import qtawesome as qta


class IconButton(QtWidgets.QPushButton):
    def __init__(self, icon=("fa5s.square", "#888888"), hover_icon=None, parent=None):
        super(IconButton, self).__init__(parent=parent)

        self._hovered = False

        self._icon = self.build_icon(icon)
        if not hover_icon:
            if isinstance(icon, tuple):
                hover_icon = (icon[0], "white")
            else:
                hover_icon = self._icon

        self._hover_icon = self.build_icon(hover_icon)

        self.set_icons()

    @staticmethod
    def build_icon(icon):
        if isinstance(icon, QtGui.QIcon):
            return icon

        icon, color = icon

        return qta.icon(icon, color=color)

    def set_icons(self):
        if self._hovered:
            self.setIcon(self._hover_icon)
        else:
            self.setIcon(self._icon)

    def enterEvent(self, event):
        self._hovered = True
        self.set_icons()

    def leaveEvent(self, event):
        self._hovered = False
        self.set_icons()
