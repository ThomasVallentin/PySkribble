from PySide2 import QtCore

from network.server import SkribbleServer

app = QtCore.QCoreApplication([])

server = SkribbleServer(ip="192.168.56.1", port=5555)
server.start()

app.exec_()
