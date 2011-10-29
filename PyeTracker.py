#!/usr/bin/env python

import sys, os, re

from PySide.QtCore import *
from PySide.QtGui import *

class DataModel(QAbstractTableModel): 
    
    def __init__(self, datain=[], headerdata=[], parent=None):
        super(DataModel, self).__init__(parent)

        self.arraydata = datain
        self.headerdata = headerdata
    
    def rowCount(self, parent):
        if self.arraydata:
            return len(self.arraydata)
        else:
            return 0
    
    def columnCount(self, parent):
        if self.arraydata:
            return len(self.arraydata[0])
        else:
            return 0 
    
    def data(self, index, role):
        if not index.isValid(): 
            return None
        if not 0 <= index.row() < len(self.arraydata):
            return None
        elif role != Qt.DisplayRole: 
            return None
        return self.arraydata[index.row()][index.column()]
        
    
    def headerData(self, col, orientation, role):
        try:
            if self.headerdata and orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self.headerdata[col]
        except IndexError:
            pass
        return None

class PyeTracker(QMainWindow):

    def __init__(self):
        super(PyeTracker, self).__init__()

        # Create Menus
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.openAction = self.createAction("&Open...", self.fileMenu, self.openFile)
        self.openAction = self.createAction("E&xit", self.fileMenu, self.close)        
        self.menuBar.addMenu(self.fileMenu)
        
        self.setStatusBar(QStatusBar())
        self.setStatusbarMessage('Ready')
        
        self.header = []
        
        self.metrics = QFontMetrics(QApplication.font())
        
        self.origdata = self.data = None
        
        layout0 = QHBoxLayout()
        self.createDataTable()               
        layout0.addWidget(self.dataTableGroupBox)
        
        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignTop)
        self.createParsingOptionsGroup()
        layout1.addWidget(self.parsingGroupBox)
        self.createStatsGroup()
        layout1.addWidget(self.statsGroupBox)
        layout0.addLayout(layout1)
        
        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addLayout(layout0)
        
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainWidget)
        
        self.pb = QProgressBar(self.statusBar())
        self.pb.hide()
        self.statusBar().addPermanentWidget(self.pb)

        self.setWindowTitle("PyeTracker")
        
        self.show()
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    
    def updateProgress(self, n, nrows, message=None):
        self.pb.show()
        self.pb.setRange(0, nrows)
        self.pb.setValue(n)
        if message:
            self.setStatusbarMessage(message)
    
    def setStatusbarMessage(self, message):
        self.statusBar().showMessage(message)
    
    def createDataTable(self):
        self.dataTableGroupBox = QGroupBox("Gaze Data")
        self.dataTableGroupBox.setMinimumWidth(500)
        layout1 = QHBoxLayout()
        self.datatableModel = DataModel()
        self.datatable = QTableView()
        self.datatable.setModel(self.datatableModel)
        self.datatable.verticalHeader().setVisible(False)
        layout1.addWidget(self.datatable)        
        self.dataTableGroupBox.setLayout(layout1)
        
    def createStatsGroup(self):
        self.statsGroupBox = QGroupBox("Gaze Data Stats")
        self.statsGroupBox.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)
        
        layout2 = QVBoxLayout()
        #layout2.setAlignment(Qt.AlignVCenter)
        stats = QGridLayout()
        self.statsLines = QLabel('NA')
        self.statsComments = QLabel('NA')
        self.statsPercentGood = QLabel('NA')
        self.statsSegments = QLabel('NA')
        stats.addWidget(QLabel('Lines:'),0,0)
        stats.addWidget(self.statsLines,0,1)
        stats.addWidget(QLabel('Comments:'),1,0)
        stats.addWidget(self.statsComments,1,1)
        stats.addWidget(QLabel('Percent Good:'),2,0)
        stats.addWidget(self.statsPercentGood,2,1)
        stats.addWidget(QLabel('Segments:'),3,0)
        stats.addWidget(self.statsSegments,3,1)
        layout2.addLayout(stats)
        self.statsGroupBox.setLayout(layout2)
        
    def createParsingOptionsGroup(self):
        self.parsingGroupBox = QGroupBox("Parsing Options")
        self.parsingGroupBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        layout2 = QVBoxLayout()
        #layout2.setAlignment(Qt.AlignVCenter)
        self.headerCheckBox = QCheckBox('First Row Header')
        self.delimTabCheckBox = QCheckBox('Tab Delim')
        self.delimTabCheckBox.setCheckState(Qt.CheckState.Checked)
        self.delimSpaceCheckBox = QCheckBox('Space Delim')
        self.delimCommaCheckBox = QCheckBox('Comma Delim')
        self.statusComboBox = QComboBox()
        self.gazexComboBox = QComboBox()
        self.gazeyComboBox = QComboBox()
        self.timestampComboBox = QComboBox()
        layout3 = QGridLayout()
        layout3.addWidget(QLabel('Comment:'),0,0)
        self.commentLineEdit = QLineEdit('#')
        self.commentLineEdit.setFixedWidth(self.metrics.width('Z')*18)
        layout3.addWidget(self.commentLineEdit,0,1)
        layout3.addWidget(QLabel('Cleanup Regex:'),1,0)
        self.cleanupLineEdit = QLineEdit('^\(|\)$')
        self.cleanupLineEdit.setFixedWidth(self.metrics.width('Z')*18)
        layout3.addWidget(self.cleanupLineEdit,1,1)
        layout3.addWidget(QLabel('Status:'),2,0)
        layout3.addWidget(self.statusComboBox,2,1)
        layout3.addWidget(QLabel('Gaze X:'),3,0)
        layout3.addWidget(self.gazexComboBox,3,1)
        layout3.addWidget(QLabel('Gaze Y:'),4,0)
        layout3.addWidget(self.gazeyComboBox,4,1)
        layout3.addWidget(QLabel('Timestamp:'),5,0)
        layout3.addWidget(self.timestampComboBox,5,1)
        QObject.connect(self.headerCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        QObject.connect(self.delimTabCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        QObject.connect(self.delimSpaceCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        QObject.connect(self.delimCommaCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        QObject.connect(self.statusComboBox, SIGNAL('currentIndexChanged(int)'), self.statusComboChanged)
        layout2.addWidget(self.headerCheckBox)
        layout2.addWidget(self.delimTabCheckBox)
        layout2.addWidget(self.delimSpaceCheckBox)
        layout2.addWidget(self.delimCommaCheckBox)
        layout2.addLayout(layout3)
        self.parsingGroupBox.setLayout(layout2)
    
    def statusComboChanged(self, index):
        if index>0:
            index -= 1
            try:
                percentGood = sum([float(data[index]) for data in self.data]) / len(self.data) * 100.0
                self.statsPercentGood.setText('%.2f%%' % (percentGood))
            except ValueError, e:
                self.statusComboBox.setCurrentIndex(0)
                self.setStatusbarMessage('Error: "%s"' % (str(e)))
                self.statsPercentGood.setText('NA')
        else:
            self.statsPercentGood.setText('NA')
    
    def createAction(self, text, menu, slot):
        action = QAction(text, self)
        menu.addAction(action)
        action.triggered.connect(slot)
        return action

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file')
        if filename:
            self.setStatusbarMessage('Reading file...')
            f = open(filename, 'r')
            data = f.read()
            for delim in ['\r\n','\r','\n']:
                tmp = data.split(delim)
                l = len(tmp)
                if (l>1):
                    if not tmp[l-1]:
                        del tmp[l-1]
                    self.origdata = tmp
                    break
            f.close()
            self.refreshDataTable()
            
    def refreshDataTable(self):
        if not self.origdata:
            return
        self.updateProgress(0, 1, 'Parsing eye gaze data...')
        self.data = []
        oldheader = self.header
        comments = 0
        firstNonComment = False
        cleanup = None
        if self.cleanupLineEdit.text():
            cleanup = self.cleanupLineEdit.text()
        lines = len(self.origdata)
        for i, line in enumerate(self.origdata):
            self.updateProgress(i+1, lines, 'Parsing eye gaze data...')
            delims = []
            if re.match('^'+self.commentLineEdit.text(),line):
                comments += 1
                continue
            if cleanup:
                line = re.sub(cleanup,'',line)
            if self.delimTabCheckBox.checkState() == Qt.CheckState.Checked:
                delims.append('\t')
            if self.delimSpaceCheckBox.checkState() == Qt.CheckState.Checked:
                delims.append(' ')
            if self.delimCommaCheckBox.checkState() == Qt.CheckState.Checked:
                delims.append(',')
            if delims:
                line = re.split('|'.join(delims),line)
            self.data.append(line)
        self.statsLines.setText(str(len(self.origdata)))
        self.statsComments.setText(str(comments))
        self.datatable.horizontalHeader().setVisible(True)
        if self.headerCheckBox.checkState() == Qt.CheckState.Checked:
            self.header = self.data[0]
            self.data = self.data[1:]
        else:
            self.header = ['Column %d'%i for i in range(1,len(self.data[0])+1)]
        self.datatableModel = DataModel(self.data,self.header)
        self.datatable.setModel(self.datatableModel)
        self.datatable.setShowGrid(True)
        if oldheader != self.header:
            self.updateComboBox(self.statusComboBox)
            self.updateComboBox(self.gazexComboBox)
            self.updateComboBox(self.gazeyComboBox)
            self.updateComboBox(self.timestampComboBox)
        self.setStatusbarMessage('Finished')
        self.pb.hide()
        
    def updateComboBox(self, cb):
        cb.clear()
        cb.addItem('')
        for h in self.header:
            cb.addItem(h)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    pyetracker = PyeTracker()
    sys.exit(app.exec_())