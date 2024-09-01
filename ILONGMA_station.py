import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QDesktopWidget, QLabel, QVBoxLayout, QPushButton, QMainWindow, QTabWidget)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from map_module import WebViewer, html_content
from Settings_module import General
from Simulating_module import Simulation
from Interfaces_module import RocketSelector
import os
from datetime import datetime

def install(package):
    try:
        __import__(package)
    except ImportError:
        print(f"The '{package}' module is not installed. Attempt installation.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 필요한 패키지 목록
packages = [
    'PyQt5', 'numpy', 'pandas', 'geopandas', 'shapely', 'matplotlib',
    'contextily', 'geopy', 'pyproj', 'folium', 'pyqtwebengine'  # 'pyqtwebengine'는 'PyQtWebEngine'을 위한 패키지입니다.
]

for package in packages:
    install(package)

class Main(QMainWindow):
    def __init__(self, starting_window):
        super().__init__()
        self.starting_window = starting_window
        self.coordinate_window = None
        self.general_window = None
        self.simulation_window = None
        self.simulation_open = False
        self.interface_window = None
        self.defalts = 'rocket_selection_details_defaults.txt'
        self.coordinate = 'coordinates.txt'
        self.select = 'rocket_selection_details.txt'
        self.trajectory = 'rocket_trajectory.csv'
        self.initUI()
        self.createDefaultFile()

    def initUI(self):
        self.setWindowTitle('I.L.O.N.G.M.A station')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        self.setGeometry(0, 0, 1500, 170)
        self.setFixedSize(1500, 170)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        tab1 = QWidget()
        layout1 = QVBoxLayout(tab1)
        image_widget1 = ImageWidget('ILONGMA_SN.png', tab1)
        layout1.addWidget(image_widget1)

        button_layout1 = QHBoxLayout()
        coordinate = QPushButton('Coordinate', tab1)
        simulation = QPushButton('Simulation', tab1)
        interface = QPushButton('Interface', tab1)
        coordinate.setGeometry(30, 35, 100, 60)  
        simulation.setGeometry(160, 35, 100, 60)
        interface.setGeometry(290, 35, 100, 60)
        self.setFixedFontSize(coordinate, 10)
        self.setFixedFontSize(simulation, 10)
        self.setFixedFontSize(interface, 10)

        layout1.addLayout(button_layout1)
        self.tab_widget.addTab(tab1, 'Simulations')

        coordinate.clicked.connect(self.openCoordinate)
        simulation.clicked.connect(self.openSimulations)
        interface.clicked.connect(self.openInterfaces)

        tab2 = QWidget()
        layout2 = QVBoxLayout(tab2)
        image_widget2 = ImageWidget('ILONGMA_SN.png', tab2)
        layout2.addWidget(image_widget2)

        button_layout2 = QHBoxLayout()
        settings = QPushButton('Settings', tab2)
        settings.setGeometry(30, 35, 100, 60)
        self.setFixedFontSize(settings, 10)

        layout2.addLayout(button_layout2)
        self.tab_widget.addTab(tab2, 'Simulations')

        settings.clicked.connect(self.openSettings)

        tab3 = QWidget()
        layout3 = QVBoxLayout(tab3)
        image_widget3 = ImageWidget('ILONGMA_SN.png', tab3)
        layout3.addWidget(image_widget3)

        Youtube = QLabel('<a href="https://www.youtube.com/@6thBSSOCEANICTFESTIVAL/featured">Our Ocean ICT Youtube</a>',tab3)
        Youtube.setOpenExternalLinks(True)
        Help = QLabel('<a href="https://sites.google.com/view/ilongma-project/welcome-to-ilongma">Help and info</a>',tab3)
        Help.setOpenExternalLinks(True)
        Youtube.setGeometry(20, 15, 400, 60)
        Help.setGeometry(20, 45, 400, 60)
        self.setFixedFontSize(Youtube, 11)
        self.setFixedFontSize(Help, 11)

        self.tab_widget.addTab(tab3, 'Help and Information')

        self.setTabButtonFontSize(10)

    def setFixedFontSize(self, widget, size):
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)

    def setTabButtonFontSize(self, size):
        tab_bar = self.tab_widget.tabBar()
        font = tab_bar.font()
        font.setPointSize(size)
        tab_bar.setFont(font)

    def openCoordinate(self):
        if not self.coordinate_window:
            self.coordinate_window = WebViewer(html_content)
        else:
            self.coordinate_window.webview.setHtml(html_content)
        self.coordinate_window.show()
        self.coordinate_window.raise_()

    def openSettings(self):
        if not self.general_window:
            self.general_window = General()
        else:
            self.general_window.change_font('Arial')
        self.general_window.show()
        self.general_window.raise_()

    def openSimulations(self):
        if self.simulation_open:
            return
        self.simulation_window = Simulation()
        self.simulation_window.closed.connect(self.onSimulationWindowClosed)
        self.simulation_window.show()
        self.simulation_window.raise_()
        self.simulation_open = True

    def openInterfaces(self):
        if not self.interface_window:
            self.interface_window = RocketSelector()

        self.interface_window.show()
        self.interface_window.raise_()
            

    def onSimulationWindowClosed(self):
        self.simulation_window = None
        self.simulation_open = False

    def createDefaultFile(self):
        with open(self.defalts, 'w') as file:
            now = datetime.now()
            file.write(f"Selected Rocket Type: defalt rocket\n")
            file.write(f"Max Speed: 7.8 km/s\n")
            file.write(f"Orbit: GEO\n")
            file.write(f"Return Status: Return\n")
            file.write(f"Launch Delay: 10.0 minutes\n")
            file.write(f"Launch Date: {now.strftime('%Y-%m-%d')}\n")
            file.write(f"Launch Angle: 0.0°\n")

    def showEvent(self, event):
        super().showEvent(event)
        self.starting_window.closeWindow()

    def closeEvent(self, event):
        if self.coordinate_window and self.coordinate_window.isVisible():
            event.ignore()
        elif self.general_window and self.general_window.isVisible():
            event.ignore()
        elif self.simulation_window and self.simulation_window.isVisible():
            event.ignore()
        elif self.interface_window and self.interface_window.isVisible():
            event.ignore()
        else:
            event.accept()
            
            if os.path.exists(self.coordinate):
                try:
                    os.remove(self.coordinate)
                except OSError as e:
                    pass
                
            if os.path.exists(self.select):
                try:
                    os.remove(self.select)
                except OSError as e:
                    pass

            if os.path.exists(self.defalts):
                try:
                    os.remove(self.defalts)
                except OSError as e:
                    pass

            if os.path.exists(self.trajectory):
                try:
                    os.remove(self.trajectory)
                except OSError as e:
                    pass

class ImageWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setMinimumSize(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(self.image_path)
        scaled_pixmap = pixmap.scaledToHeight(self.height(), Qt.SmoothTransformation)
        x = self.width() - scaled_pixmap.width() - 20
        y = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)

class Starting(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(' ')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        self.img = QLabel(self)
        pixmap = QPixmap('ILONGMA.png')
        self.img.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.img.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.img)
        self.setLayout(layout)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeWindow(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setStyle('Fusion')
    starting = Starting()
    main = Main(starting)
    starting.show()
    main.show()
    sys.exit(app.exec_())

