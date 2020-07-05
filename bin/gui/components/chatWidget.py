from PySide2 import QtWidgets, QtCore, QtGui


from gui.components import historyTextBar


class ChatWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ChatWidget, self).__init__(parent=parent)

        self.setup_ui()

    def setup_ui(self):
        self.lyt = QtWidgets.QVBoxLayout(self)
        self.lyt.setObjectName(u"chat_wid_lyt")
        self.lyt.setContentsMargins(8, 8, 8, 8)

        self.chat_message_list_wid = QtWidgets.QListWidget(self)
        self.chat_message_list_wid.setObjectName(u"chat_message_list_wid")
        self.chat_message_list_wid.setStyleSheet(u"color: #aaaaaa;")

        self.lyt.addWidget(self.chat_message_list_wid)

        self.chat_message_txe = historyTextBar.HistoryTextBar(self)

        self.lyt.addWidget(self.chat_message_txe)

