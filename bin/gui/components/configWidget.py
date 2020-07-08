from PySide2 import QtWidgets, QtCore, QtGui


from functools import partial
from lib import utils


class ConfigWidget(QtWidgets.QWidget):
    def __init__(self, config_dict, parent=None):
        super(ConfigWidget, self).__init__(parent=parent)

        self.config = config_dict

        self.setup_ui()

        self.update_from_config()

    def setup_ui(self):
        self.setObjectName("config_widget")
        # self.setStyleSheet("background-color: transparent")
        self.lyt = QtWidgets.QVBoxLayout(self)
        self.lyt.setSpacing(16)

        self.title_lbl = QtWidgets.QLabel("Settings", self)
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))

        self.lyt.addWidget(self.title_lbl)

        separator = QtWidgets.QFrame()
        separator.setFixedSize(250, 2)
        separator.setStyleSheet("background-color: #aaaaaa")

        self.lyt.addWidget(separator, 0, QtCore.Qt.AlignCenter)

        self.parameters_lyt = QtWidgets.QGridLayout()
        self.parameters_lyt.setSpacing(8)
        self.parameters_lyt.setContentsMargins(4, 16, 4, 16)
        self.lyt.addLayout(self.parameters_lyt)

        self.start_btn = QtWidgets.QPushButton("Start game !", self)
        self.start_btn.setProperty("importance", "secondary")
        self.start_btn.setStyleSheet("QPushButton{padding: 16px;background-color: rgb(255, 0, 88)} "
                                     "QPushButton:hover{background: rgb(255, 51, 121)}"
                                     "QPushButton:pressed{background: rgb(0, 0, 0)}")
        self.start_btn.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Black))
        self.start_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.start_btn.setFixedWidth(250)

        self.lyt.addWidget(self.start_btn, 0, QtCore.Qt.AlignCenter)

    def update_from_config(self):
        for i in range(self.parameters_lyt.count()):
            self.parameters_lyt.takeAt(0).widget().deleteLater()

        for i, (key, value) in enumerate(self.config.items()):
            name_lbl = QtWidgets.QLabel(utils.camel_to_pretty(utils.snake_to_camel(str(key))))
            name_lbl.setFont(QtGui.QFont("Arial", 14))
            name_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.parameters_lyt.addWidget(name_lbl, i, 0)

            value_field = QtWidgets.QSpinBox(self)
            value_field.setMaximum(999999)
            value_field.setFont(QtGui.QFont("Arial", 12))
            value_field.setValue(value)
            value_field.valueChanged.connect(partial(self.set_value_to_config, key))

            self.parameters_lyt.addWidget(value_field, i, 1)

    def set_value_to_config(self, key, value):
        self.config[key] = value


class ParameterWidget(QtWidgets.QWidget):
    typ_to_widget = {int: QtWidgets.QSpinBox}

    def __init__(self, name, value, config_widget, parent=None):
        super(ParameterWidget, self).__init__(parent=parent)

        self.config_widget = config_widget
        self.name = name
        self.value = value

        self.lyt = QtWidgets.QHBoxLayout(self)



        self.value_field = QtWidgets.QSpinBox(self)
        self.value_field.setMaximum(999999)
        self.value_field.setValue(self.value)
        self.value_field.valueChanged.connect(self.set_value_to_config)

        self.lyt.addWidget(self.value_field)

    def set_value_to_config(self, value):
        self.config_widget.config[self.name] = value


if __name__ == '__main__':
    from constants import DEFAULT_CONFIG

    app = QtWidgets.QApplication([])

    wid = ConfigWidget(DEFAULT_CONFIG.copy())
    wid.show()

    app.exec_()
