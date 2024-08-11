import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGroupBox, QRadioButton, QCheckBox, QPushButton, QMenu, QGridLayout, QVBoxLayout, QComboBox)
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class General(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('General Settings')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        grid = QGridLayout()
        grid.addWidget(self.Design(), 0, 1)
        self.setLayout(grid)
        self.setFixedSize(400, 300)
        
        self.show()

    def createFirstExclusiveGroup(self):
        groupbox = QGroupBox('Exclusive Radio Buttons')
        radio1 = QRadioButton('Radio1')
        radio2 = QRadioButton('Radio2')
        radio3 = QRadioButton('Radio3')
        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        groupbox.setLayout(vbox)

        self.setFixedFontSize(groupbox, 9)

        return groupbox
    
    def createNonExclusiveGroup(self):
        groupbox = QGroupBox('Non-Exclusive Checkboxes')
        groupbox.setFlat(True)

        checkbox1 = QCheckBox('Checkbox1')
        checkbox2 = QCheckBox('Checkbox2')
        checkbox2.setChecked(True)
        tristatebox = QCheckBox('Tri-state Button')
        tristatebox.setTristate(True)

        vbox = QVBoxLayout()
        vbox.addWidget(checkbox1)
        vbox.addWidget(checkbox2)
        vbox.addWidget(tristatebox)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        self.setFixedFontSize(groupbox, 9)

        return groupbox

    def Design(self):
        groupbox = QGroupBox('Design')

        style_combo = QComboBox()
        style_combo.addItem('Fusion')
        style_combo.addItem('Windows')
        style_combo.addItem('Macintosh')
        style_combo.addItem('WindowsVista')
        style_combo.addItem('WindowsXP')
        style_combo.setCurrentIndex(0)
        style_combo.currentTextChanged.connect(self.change_style)

        font_combo = QComboBox()
        self.fonts = QFontDatabase().families()
        font_combo.addItems(self.fonts)
        font_combo.currentTextChanged.connect(self.change_font)

        vbox = QVBoxLayout()
        vbox.addWidget(style_combo)
        vbox.addWidget(font_combo)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        self.setFixedFontSize(groupbox, 9)

        return groupbox

    def change_style(self, style_name):
        QApplication.setStyle(style_name)
        self.setStyleSheet("") 
        QApplication.instance().setPalette(QApplication.style().standardPalette()) 

    def change_font(self, font_name):
        font = QFont(font_name)
        self.setFixedFontSize(self, 9)
        QApplication.instance().setFont(font)

    def setFixedFontSize(self, widget, size):
        if isinstance(widget, QWidget):
            font = widget.font()
            font.setPointSize(size)
            widget.setFont(font)
        elif isinstance(widget, QGroupBox):
            font = widget.font()
            font.setPointSize(size)
            widget.setFont(font)
            for sub_widget in widget.findChildren(QWidget):
                self.setFixedFontSize(sub_widget, size)
