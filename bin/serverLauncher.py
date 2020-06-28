from PySide2 import QtCore

import sys

from constants import *

sys.path.insert(0, ROOT_DIR)

from network.server import SkribbleServer

app = QtCore.QCoreApplication([])

server = SkribbleServer()
server.start()

app.exec_()