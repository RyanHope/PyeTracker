#!/usr/bin/env python

from __future__ import division

import sys, os, re, copy

from PySide.QtCore import *
from PySide.QtGui import *

from about import AboutDlg
from filters import ColumnValueFilter
from parse import ParseDlg
from datamodel import DataModel
from treemodel import TreeModel

class PyeTracker(QMainWindow):

    def __init__(self):
        super(PyeTracker, self).__init__()

        # Create Menus
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.openAction = self.createAction("&Open...", self.fileMenu, self.openFile)
        self.fileMenu.addSeparator()
        #self.closeAction = self.createAction("Close", self.fileMenu, self.closeFile)
        #self.closeAction.setEnabled(False)
        self.fileMenu.addSeparator()
        self.openAction = self.createAction("E&xit", self.fileMenu, self.close)        
        self.menuBar.addMenu(self.fileMenu)

        self.helpMenu = QMenu("&Help", self)
        self.aboutAction = self.createAction("&About", self.helpMenu, self.about)
        self.aboutAction.setMenuRole(QAction.NoRole)
        self.menuBar.addMenu(self.helpMenu)

        self.setStatusBar(QStatusBar())
        self.setStatusbarMessage('Ready')
        
        mainLayout = QGridLayout()
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(mainLayout)
        
        self.filesmodel = TreeModel({})
        
        self.files = QTreeView()
        self.files.setModel(self.filesmodel)
        mainLayout.addWidget(self.files)
        
        self.setCentralWidget(self.mainWidget)

        self.setMenuBar(self.menuBar)
        self.pb = QProgressBar(self.statusBar())
        self.pb.hide()
        self.statusBar().addPermanentWidget(self.pb)

        self.setWindowTitle("PyeTracker")
        self.setWindowIcon(QIcon('logo.png'))
        
        self.setGeometry(0,0,600,300)

        self.show()
        self.activateWindow()
        self.raise_()

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def updateProgress(self, n, nrows, message=None):
        if n == nrows == None:
            self.pb.hide()
        else:
            self.pb.show()
            self.pb.setRange(0, nrows)
            self.pb.setValue(n)
        if message:
            self.setStatusbarMessage(message)
            
    def about(self):
        AboutDlg(self)

    def setStatusbarMessage(self, message):
        self.statusBar().showMessage(message)

    def createAction(self, text, menu, slot):
        action = QAction(text, self)
        menu.addAction(action)
        action.triggered.connect(slot)
        return action

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file')
        if filename:
            dlg = ParseDlg(filename)
            if dlg.exec_():
                dlg.parseData(progress_cb=lambda a,b: self.updateProgress(a, b, 'Importing data...'))
                dlg.updateModel()
                self.filesmodel = TreeModel(dlg.getSegments())
                self.files.setModel(self.filesmodel)
                self.updateProgress(None, None, 'Finished')

if __name__ == '__main__':

    app = QApplication(sys.argv)
    pyetracker = PyeTracker()
    sys.exit(app.exec_())