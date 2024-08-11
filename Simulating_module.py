import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QDesktopWidget, QLabel, QVBoxLayout, QPushButton, QMainWindow, QTabWidget)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class Simulation(QMainWindow):
    closed = pyqtSignal() 

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('I.L.O.N.G.M.A simulation')
        self.setWindowIcon(QIcon('ILONGMA.png'))

        settings1 = QPushButton('Settings', self)
        self.setFixedFontSize(settings1, 10)
        settings1.move(5, 5)
        settings1.setFixedSize(100, 50)

        self.setGeometry(0, 0, 900, 600)
        self.show()
        
    def setFixedFontSize(self, widget, size):
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    simulation = Simulation()
    sys.exit(app.exec_())
