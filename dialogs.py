from PySide.QtCore import *
from PySide.QtGui import *

import copy

class ColumnValueFilter(QDialog):
    
    def __init__(self, parent=None):
        super(ColumnValueFilter, self).__init__(parent)
        self.parent = parent
        self.setModal(True)
        buttonBox = QDialogButtonBox()
        cancelButton = buttonBox.addButton(buttonBox.Cancel)
        QObject.connect(cancelButton, SIGNAL('clicked()'), self.close)
        self.okButton = buttonBox.addButton(buttonBox.Ok)
        self.okButton.setEnabled(False)
        QObject.connect(self.okButton, SIGNAL('clicked()'), self.doFilter)
        layout = QVBoxLayout()
        filteropts = QGridLayout()
        filteropts.addWidget(QLabel('Column:'),0,0)
        self.columns = QComboBox()
        coldata = copy.copy(self.parent.datatableModel.getHeader())
        coldata.insert(0,'')
        self.columns.addItems(coldata)
        filteropts.addWidget(self.columns,0,1)
        filteropts.addWidget(QLabel('Value:'),1,0)
        self.values = QComboBox()
        self.values.setEnabled(False)
        filteropts.addWidget(self.values,1,1)
        layout.addLayout(filteropts)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.setWindowTitle("Filter By Column Value")
        self.show()
        self.setFixedSize(self.width(),self.height())
        QObject.connect(self.columns, SIGNAL('currentIndexChanged(int)'), self.columnChanged)
        QObject.connect(self.values, SIGNAL('currentIndexChanged(int)'), self.valueChanged)
        self.exec_()
        
    def doFilter(self):
        self.hide()
        self.parent.updateProgress(0, 1, 'Filtering eye gaze data...')
        val = self.values.itemText(self.values.currentIndex())
        newdata = []
        l = len(self.parent.datatableModel.arraydata)
        s = 0
        if self.parent.headerCheckBox.checkState() == Qt.CheckState.Checked:
            newdata.append(self.parent.datatableModel.arraydata[s])
            s = 1
        for i in range(s,l):
            self.parent.updateProgress(i+1, l, 'Filtering eye gaze data...')
            if self.parent.datatableModel.arraydata[i][self.columns.currentIndex()-1] == val:
                newdata.append(self.parent.datatableModel.arraydata[i])
        self.parent.setStatusbarMessage('Finished')
        self.parent.pb.hide()
        self.parent.data = newdata
        self.parent.refreshDataTable()
        self.close()
    
    def valueChanged(self, index):
        if index>0:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)
    
    def columnChanged(self, index):
        if index>0:
            index -= 1
            self.values.setEnabled(True)
            items = []
            for x in self.parent.datatableModel.getData():
                try:
                    items.append(x[index])
                except IndexError:
                    pass
            items = list(frozenset(items))
            items.insert(0,'')
            self.values.clear()
            self.values.addItems(items)
        else:
            self.values.clear()
            self.values.setEnabled(False)
            self.okButton.setEnabled(False)

class AboutDlg(QDialog):
    
    def __init__(self, parent=None):
        super(AboutDlg, self).__init__(parent)
        self.setModal(True)
        buttonBox = QDialogButtonBox()
        closeButton = buttonBox.addButton(buttonBox.Close)
        QObject.connect(closeButton, SIGNAL('clicked()'), self.close)
        top = QHBoxLayout()
        topleft = QVBoxLayout()
        name = QLabel('<h1>PyeTracker</h1>')
        version = QLabel('<h3>Version: %s</h2>' % ('1.0'))#(parent.githash))
        topleft.addWidget(name)
        topleft.addWidget(version)
        topleft.setAlignment(Qt.AlignTop)
        top.addLayout(topleft)
        logo = QLabel()
        logo.setPixmap(QPixmap('logo.png'))
        logo.setAlignment(Qt.AlignTop)
        top.addWidget(logo)
        layout = QVBoxLayout()
        layout.addLayout(top)
        copyright = QLabel('<p>&#64; Copyright Ryan M. Hope, 2011.  All rights reserved.</p>')
        layout.addWidget(copyright)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.setWindowTitle("About")
        self.setSizeGripEnabled(False)
        self.show()
        self.setFixedSize(self.width(),self.height())
        self.exec_()