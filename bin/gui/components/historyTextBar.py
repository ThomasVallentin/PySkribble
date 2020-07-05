from PySide2 import QtWidgets, QtCore, QtGui


class HistoryTextBar(QtWidgets.QLineEdit):
    text_sent = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(HistoryTextBar, self).__init__(parent=parent)

        self.history = [""]
        self.current_index = 0
        self.setup_ui()
        self.make_connections()

    def setup_ui(self):
        self.setObjectName("ChatBar")
        self.setFixedHeight(34)

    def send_text(self):
        if not self.history[self.current_index]:
            return

        text = self.history.pop(self.current_index)
        self.text_sent.emit(text)

        # If we have history and the last line is empty, we insert the text before the last line
        # The empty line becomes the current one
        if self.history and not self.history[-1]:
            self.history.insert(-1, text)
        # If there is no history or the last line has text, we append the sent text and a new line
        else:
            self.history.append(text)
            self.history.append("")

        self.setText("")
        self.current_index = len(self.history) - 1

    def set_current_text(self, text):
        self.history[self.current_index] = text

    def restore_history(self, index):
        self.current_index = index
        self.setText(self.history[self.current_index])

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            if self.current_index > 0:
                self.restore_history(self.current_index - 1)

        if event.key() == QtCore.Qt.Key_Down:
            if self.current_index < len(self.history) - 1:
                self.restore_history(self.current_index + 1)

        super(HistoryTextBar, self).keyPressEvent(event)

    def make_connections(self):
        self.textEdited.connect(self.set_current_text)
        self.returnPressed.connect(self.send_text)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    wid = HistoryTextBar()
    wid.show()

    app.exec_()