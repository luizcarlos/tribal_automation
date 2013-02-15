# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tribalMainLayout.ui'
#
# Created: Thu Mar 11 13:59:31 2010
#      by: PyQt4 UI code generator 4.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TribalMainWindow(object):
    def setupUi(self, TribalMainWindow):
        TribalMainWindow.setObjectName("TribalMainWindow")
        TribalMainWindow.resize(1182, 756)
        self.centralWidget = QtGui.QWidget(TribalMainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.tribalLabel = QtGui.QLabel(self.centralWidget)
        self.tribalLabel.setGeometry(QtCore.QRect(0, 0, 1162, 716))
        self.tribalLabel.setObjectName("tribalLabel")
        TribalMainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QtGui.QMenuBar(TribalMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1182, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDrawing = QtGui.QMenu(self.menubar)
        self.menuDrawing.setObjectName("menuDrawing")
        TribalMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(TribalMainWindow)
        self.statusbar.setObjectName("statusbar")
        TribalMainWindow.setStatusBar(self.statusbar)
        self.actionSave_As = QtGui.QAction(TribalMainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionStart_Drawaing = QtGui.QAction(TribalMainWindow)
        self.actionStart_Drawaing.setObjectName("actionStart_Drawaing")
        self.actionOpen = QtGui.QAction(TribalMainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionOpen)
        self.menuDrawing.addAction(self.actionStart_Drawaing)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDrawing.menuAction())

        self.retranslateUi(TribalMainWindow)
        QtCore.QMetaObject.connectSlotsByName(TribalMainWindow)

    def retranslateUi(self, TribalMainWindow):
        TribalMainWindow.setWindowTitle(QtGui.QApplication.translate("TribalMainWindow", "Tribal Window", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("TribalMainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuDrawing.setTitle(QtGui.QApplication.translate("TribalMainWindow", "Drawing", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_As.setText(QtGui.QApplication.translate("TribalMainWindow", "Save As", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStart_Drawaing.setText(QtGui.QApplication.translate("TribalMainWindow", "Start Drawaing", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("TribalMainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))

