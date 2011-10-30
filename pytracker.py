#!/usr/bin/env python

import sys, os, re, copy

from PySide.QtCore import *
from PySide.QtGui import *

from dialogs import AboutDlg, ColumnValueFilter
from datamodel import DataModel

class PyeTracker(QMainWindow):

    def __init__(self):
        super(PyeTracker, self).__init__()

        # Create Menus
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.openAction = self.createAction("&Open...", self.fileMenu, self.openFile)
        self.fileMenu.addSeparator()
        self.closeAction = self.createAction("Close", self.fileMenu, self.closeFile)
        self.closeAction.setEnabled(False)
        self.fileMenu.addSeparator()
        self.openAction = self.createAction("E&xit", self.fileMenu, self.close)        
        self.menuBar.addMenu(self.fileMenu)

        self.dataMenu = QMenu("&Data", self)
        self.filterByColumnValueAction = self.createAction("Filter by &column value...", self.dataMenu, self.filterByColumnValue)
        self.filterByColumnValueAction.setEnabled(True)
        self.dataMenu.addSeparator()
        self.undoAllAction = self.createAction("&Undo all filters", self.dataMenu, self.undoFilters)
        self.menuBar.addMenu(self.dataMenu)

        self.helpMenu = QMenu("&Help", self)
        self.helpAction = self.createAction("&About", self.helpMenu, self.about)
        self.menuBar.addMenu(self.helpMenu)

        self.setStatusBar(QStatusBar())
        self.setStatusbarMessage('Ready')

        self.header = None

        self.metrics = QFontMetrics(QApplication.font())

        self.rawdata = self.data = None

        layout0 = QHBoxLayout()
        self.createDataTable()               
        layout0.addWidget(self.dataTableGroupBox)

        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignTop)
        self.createParsingOptionsGroup()
        layout1.addWidget(self.parsingGroupBox)
        self.createColumnGroup()
        layout1.addWidget(self.columnGroupBox)
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
        self.setWindowIcon(QIcon('logo.png'))

        self.show()

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def filterByColumnValue(self):
        ColumnValueFilter(self)

    def undoFilters(self):
        if self.origdata:
            self.data = copy.copy(self.origdata)
            self.refreshDataTable()

    def updateProgress(self, n, nrows, message=None):
        self.pb.show()
        self.pb.setRange(0, nrows)
        self.pb.setValue(n)
        if message:
            self.setStatusbarMessage(message)
            
    def about(self):
        AboutDlg(self)

    def setStatusbarMessage(self, message):
        self.statusBar().showMessage(message)

    def createDataTable(self):
        self.dataTableGroupBox = QGroupBox("Gaze Data")
        self.dataTableGroupBox.setMinimumWidth(500)
        layout1 = QHBoxLayout()
        self.datatableModel = None
        self.datatable = QTableView()
        self.datatable.verticalHeader().setVisible(False)
        layout1.addWidget(self.datatable)        
        self.dataTableGroupBox.setLayout(layout1)

    def createStatsGroup(self):
        self.statsGroupBox = QGroupBox("Gaze Data Stats")
        self.statsGroupBox.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)

        layout2 = QVBoxLayout()
        stats = QGridLayout()
        self.statsLines = QLabel('NA')
        self.statsComments = QLabel('NA')
        self.statsPercentGood = QLabel('NA')
        stats.addWidget(QLabel('Lines:'),0,0)
        stats.addWidget(self.statsLines,0,1)
        stats.addWidget(QLabel('Comments:'),1,0)
        stats.addWidget(self.statsComments,1,1)
        stats.addWidget(QLabel('Percent Good:'),2,0)
        stats.addWidget(self.statsPercentGood,2,1)
        layout2.addLayout(stats)
        self.statsGroupBox.setLayout(layout2)

    def createColumnGroup(self):
        self.columnGroupBox = QGroupBox("Column Type")
        self.columnGroupBox.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)
        layout3 = QGridLayout()
        self.statusComboBox = QComboBox()
        self.gazexComboBox = QComboBox()
        self.gazeyComboBox = QComboBox()
        self.timestampComboBox = QComboBox()
        layout3.addWidget(QLabel('Status:'),2,0)
        layout3.addWidget(self.statusComboBox,2,1)
        layout3.addWidget(QLabel('Gaze X:'),3,0)
        layout3.addWidget(self.gazexComboBox,3,1)
        layout3.addWidget(QLabel('Gaze Y:'),4,0)
        layout3.addWidget(self.gazeyComboBox,4,1)
        layout3.addWidget(QLabel('Timestamp:'),5,0)
        layout3.addWidget(self.timestampComboBox,5,1)
        QObject.connect(self.statusComboBox, SIGNAL('currentIndexChanged(int)'), self.statusComboChanged)
        self.columnGroupBox.setLayout(layout3)

    def createParsingOptionsGroup(self):
        self.parsingGroupBox = QGroupBox("Parsing Options")
        self.parsingGroupBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        layout2 = QVBoxLayout()
        self.headerCheckBox = QCheckBox('First Row Header')
        QObject.connect(self.headerCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        self.delimTabCheckBox = QCheckBox('Tab Delim')
        self.delimTabCheckBox.setCheckState(Qt.CheckState.Checked)
        self.delimSpaceCheckBox = QCheckBox('Space Delim')
        self.delimSpaceCheckBox.setCheckState(Qt.CheckState.Checked)
        self.delimCommaCheckBox = QCheckBox('Comma Delim')
        layout3 = QGridLayout()
        layout3.addWidget(QLabel('Comment Char:'),0,0)
        self.commentLineEdit = QLineEdit('#')
        self.commentLineEdit.setFixedWidth(self.metrics.width('Z')*18)
        layout3.addWidget(self.commentLineEdit,0,1)
        layout3.addWidget(QLabel('Quote:'),1,0)
        self.quoteLineEdit = QLineEdit('"')
        self.quoteLineEdit.setFixedWidth(self.metrics.width('Z')*18)
        layout3.addWidget(self.quoteLineEdit,1,1)
        layout3.addWidget(QLabel('Cleanup Regex:'),2,0)
        self.cleanupLineEdit = QLineEdit('^\(|\)$')
        self.cleanupLineEdit.setFixedWidth(self.metrics.width('Z')*18)
        layout3.addWidget(self.cleanupLineEdit,2,1)
        layout2.addWidget(self.headerCheckBox)
        layout2.addWidget(self.delimTabCheckBox)
        layout2.addWidget(self.delimSpaceCheckBox)
        layout2.addWidget(self.delimCommaCheckBox)
        layout2.addLayout(layout3)
        self.reparseButton = QPushButton('Re-parse Data')
        self.reparseButton.setEnabled(False)
        QObject.connect(self.reparseButton, SIGNAL('clicked()'), self.parseData)
        layout2.addWidget(self.reparseButton)
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

    def closeFile(self):
        self.rawdata = None
        self.data = None
        self.header = None
        self.datatableModel = DataModel()
        self.datatable.setModel(self.datatableModel)
        self.datatable.horizontalHeader().setVisible(False)
        self.closeAction.setEnabled(False)
        self.reparseButton.setEnabled(False)
        self.statusComboBox.setCurrentIndex(0)
        self.gazexComboBox.setCurrentIndex(0)
        self.gazeyComboBox.setCurrentIndex(0)
        self.timestampComboBox.setCurrentIndex(0)
        self.statsPercentGood.setText('NA')
        self.statsLines.setText('NA')
        self.statsComments.setText('NA')
        self.filterByColumnValueAction.setEnabled(False)

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
                    self.rawdata = tmp
                    break
            f.close()
            self.parseData()
            self.reparseButton.setEnabled(True)
            self.closeAction.setEnabled(True)
            self.filterByColumnValueAction.setEnabled(True)

    def parseData(self):
        if not self.rawdata:
            return
        self.updateProgress(0, 1, 'Parsing eye gaze data...')
        self.data = []
        comments = 0
        firstNonComment = False
        cleanup = None
        if self.cleanupLineEdit.text():
            cleanup = self.cleanupLineEdit.text()
        lines = len(self.rawdata)
        delims = []
        if self.delimTabCheckBox.checkState() == Qt.CheckState.Checked:
            delims.append('\t')
        if self.delimSpaceCheckBox.checkState() == Qt.CheckState.Checked:
            delims.append(' ')
        if self.delimCommaCheckBox.checkState() == Qt.CheckState.Checked:
            delims.append(',')
        if delims:
            q1 = self.quoteLineEdit.text()
            q2 = q1[::-1]
            r1 = '|'.join(delims)
            r2 = ''.join(delims)
            r = '(?=\b|%s?)(%s[^%s]*%s|[^%s]*)(?=\b|%s?)' % (r1,q1,q1,q2,r2,r1)
            reg1 = re.compile(r)
            reg2 = re.compile('|'.join([q1,q2]))
        for i, line in enumerate(self.rawdata):
            self.updateProgress(i+1, lines, 'Parsing eye gaze data...')
            if re.match('^'+self.commentLineEdit.text(),line):
                comments += 1
                continue
            if cleanup:
                line = re.sub(cleanup,'',line)
            if delims:
                line = [reg2.sub('',l) for l in filter(None,reg1.findall(line))]
            self.data.append(line)
        self.statsLines.setText(str(len(self.rawdata)))
        self.statsComments.setText(str(comments))
        self.setStatusbarMessage('Finished')
        self.pb.hide()
        self.origdata = copy.copy(self.data)
        self.refreshDataTable()

    def refreshDataTable(self):
        if not self.data:
            return
        if self.headerCheckBox.checkState() == Qt.CheckState.Checked:
            self.datatableModel = DataModel(self.data, True)
        else:
            self.datatableModel = DataModel(self.data, False)
        self.datatable.setModel(self.datatableModel)
        self.datatable.horizontalHeader().setVisible(True)
        self.datatable.setShowGrid(True)
        self.datatable.resizeColumnsToContents()

        header = self.datatableModel.getHeader()
        if self.header != header:
            self.updateComboBox(self.statusComboBox, header)
            self.updateComboBox(self.gazexComboBox, header)
            self.updateComboBox(self.gazeyComboBox, header)
            self.updateComboBox(self.timestampComboBox, header)
        self.header = header

    def updateComboBox(self, cb, header):
        cb.clear()
        cb.addItem('')
        for h in header:
            cb.addItem(h)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    pyetracker = PyeTracker()
    sys.exit(app.exec_())