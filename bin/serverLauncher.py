from PySide2 import QtCore

from network.server import SkribbleServer

app = QtCore.QCoreApplication([])

server = SkribbleServer()
server.start()

app.exec_()
