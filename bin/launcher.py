from PySide2 import QtWidgets, QtGui

from constants import *

app = QtWidgets.QApplication([])

from app import Skribble

app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(RESSOURCES_DIR, "window_icon.png"))))

client = Skribble()
client.launch()

app.exec_()
