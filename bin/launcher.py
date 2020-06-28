import os
import sys

from PySide2 import QtWidgets, QtGui

from constants import *

sys.path.insert(0, ROOT_DIR)

from app import Skribble



app = QtWidgets.QApplication([])
app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(RESSOURCES_DIR, "window_icon.png"))))

client = Skribble()
client.launch()

app.exec_()
