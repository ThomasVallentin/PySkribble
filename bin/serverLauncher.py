from PySide2 import QtCore

from network.server import SkribbleServer

app = QtCore.QCoreApplication([])

server = SkribbleServer(ip="", port=5555)
server.start()

app.exec_()
