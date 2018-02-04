#!/usr/bin/env python2

import sys
from datetime import datetime

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget


class DigitalClock(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 320))
        self.setWindowTitle("Hello world")

        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)

        title = QLabel("", self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        font = QFont('DSEG7 Classic', 50)
        title.setFont(font)
        gridLayout.addWidget(title, 0, 0)

        self._counter = 0
        self._title = title

    def show_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self._title.setText(now)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = DigitalClock()
    mainWin.show()
    sys.exit(app.exec_())
