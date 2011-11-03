from __future__ import division

from PySide.QtCore import *
from PySide.QtGui import *

from datamodel import DataModel

import sys,re,csv,copy,operator

class ParseDlg(QDialog):
    
    def __init__(self, filename, parent=None):
        super(ParseDlg, self).__init__(parent)
        
        self.filename = filename
        self.rawdata = None
        
        f = open(self.filename)
        data = f.read()
        tmp = None
        for delim in ['\r\n','\r','\n']:
            tmp = data.split(delim)
            l = len(tmp)
            if (l>1):
                if not tmp[l-1]:
                    del tmp[l-1]
                self.rawdata = tmp
                break
        f.close()
        
        self.parent = parent
        
        self.header = None
        
        self.setModal(True)
        buttonBox = QDialogButtonBox()
        cancelButton = buttonBox.addButton(buttonBox.Cancel)
        QObject.connect(cancelButton, SIGNAL('clicked()'), self.close)
        self.okButton = buttonBox.addButton(buttonBox.Ok)
        QObject.connect(self.okButton, SIGNAL('clicked()'), self.doParse)
        
        mainLayout = QGridLayout()
        
        importBox = QGroupBox('Import')
        #importBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        importBoxLayout = QGridLayout()
        importBoxLayout.addWidget(QLabel('Character set'),0,0)
        self.charsetComboBox = QComboBox()
        self.charsetComboBox.addItems(['utf-8'])
        importBoxLayout.addWidget(self.charsetComboBox,0,1)
        importBox.setLayout(importBoxLayout)
        
        separatorBox = QGroupBox('Separator Options')
        #separatorBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        separatorBoxLayout = QGridLayout()
        separatorBoxLayout.setHorizontalSpacing(60)
        
        self.delimTab = QRadioButton('Tab')
        self.delimOther = QRadioButton('Other')
        self.otherLineEdit = QLineEdit(',')
        self.otherLineEdit.setMaxLength(1)
        
        separatorBoxLayout.addWidget(self.delimTab,0,0)
        separatorBoxLayout.addWidget(self.delimOther,0,2)
        separatorBoxLayout.addWidget(self.otherLineEdit,0,3)
        
        separatorBox.setLayout(separatorBoxLayout)
        
        otherBox = QGroupBox('Other Options')
        #otherBox.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        otherBoxLayout = QGridLayout()
        otherBoxLayout.setHorizontalSpacing(60)
        
        self.quotedFieldCheckBox = QCheckBox('Quoted field as text')
        self.textLabel = QLabel('Quote character')
        self.textLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.textLineEdit = QLineEdit('"')
        self.textLineEdit.setMaxLength(1)
        self.headerCheckBox = QCheckBox('First row as header')
        self.skipCommentsCheckBox = QCheckBox('Skip comment lines')
        self.commentLabel = QLabel('Comment prefix')
        self.commentLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.commentLineEdit = QLineEdit('#')
        self.stripCheckBox = QCheckBox('Strip lines')
        self.regexLabel = QLabel('Regex')
        self.regexLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.stripLineEdit = QLineEdit('^\(|\)$')
                                    
        otherBoxLayout.addWidget(self.quotedFieldCheckBox,0,0)
        otherBoxLayout.addWidget(self.textLabel,0,1)
        otherBoxLayout.addWidget(self.textLineEdit,0,2)
        otherBoxLayout.addWidget(self.headerCheckBox,1,0)
        otherBoxLayout.addWidget(self.skipCommentsCheckBox,2,0)
        otherBoxLayout.addWidget(self.commentLabel,2,1)
        otherBoxLayout.addWidget(self.commentLineEdit,2,2)
        otherBoxLayout.addWidget(self.stripCheckBox,3,0)
        otherBoxLayout.addWidget(self.regexLabel,3,1)
        otherBoxLayout.addWidget(self.stripLineEdit,3,2)
        
        otherBox.setLayout(otherBoxLayout)
        
        filterBox = QGroupBox('Sample Filter')
        filterBoxLayout = QGridLayout()
        filterBoxLayout.setHorizontalSpacing(60)
        
        filterBoxLayout.addWidget(QLabel('Column'),0,0)
        self.columnFilterComboBox = QComboBox()
        filterBoxLayout.addWidget(self.columnFilterComboBox,1,0)
        filterBoxLayout.addWidget(QLabel('Sample Indicator'),2,0)
        self.sampleIndicatorComboBox = QComboBox()
        self.sampleIndicatorComboBox.setEnabled(False)
        filterBoxLayout.addWidget(self.sampleIndicatorComboBox,3,0)
        QObject.connect(self.columnFilterComboBox, SIGNAL('currentIndexChanged(int)'), self.filterColChanged)
        QObject.connect(self.sampleIndicatorComboBox, SIGNAL('currentIndexChanged(int)'), self.sampleIndicatorChanged)
        
        filterBox.setLayout(filterBoxLayout)
        
        columnBox = QGroupBox('Column Options')
        columnBoxLayout = QGridLayout()
        columnBoxLayout.setHorizontalSpacing(60)
        
        columnBoxLayout.addWidget(QLabel('Status'),0,0)
        self.statusCombo = QComboBox()
        columnBoxLayout.addWidget(self.statusCombo,0,1,1,2)
        self.comparisonCombo = QComboBox()
        self.comparisonCombo.addItem('==',operator.eq)
        self.comparisonCombo.addItem('<',operator.lt)
        self.comparisonCombo.addItem('<=',operator.le)
        self.comparisonCombo.addItem('>',operator.gt)
        self.comparisonCombo.addItem('>=',operator.ge)
        columnBoxLayout.addWidget(self.comparisonCombo,0,3)
        self.comparisonValue = QLineEdit('1')
        columnBoxLayout.addWidget(self.comparisonValue,0,4,1,2)
        columnBoxLayout.addWidget(QLabel('Gaze X'),1,0)
        self.gazexCombo = QComboBox()
        columnBoxLayout.addWidget(self.gazexCombo,1,1,1,2)
        columnBoxLayout.addWidget(QLabel('Gaze Y'),2,0)
        self.gazeyCombo = QComboBox()
        columnBoxLayout.addWidget(self.gazeyCombo,2,1,1,2)
        columnBoxLayout.addWidget(QLabel('Timestamp'),1,3)
        self.timestampCombo = QComboBox()
        columnBoxLayout.addWidget(self.timestampCombo,1,4,1,2)
        columnBoxLayout.addWidget(QLabel('Trial'),2,3)
        self.trialCombo = QComboBox()
        columnBoxLayout.addWidget(self.trialCombo,2,4,1,2)
        
        columnBox.setLayout(columnBoxLayout)
        
        previewBox = QGroupBox('Preview')
        previewBoxLayout = QGridLayout()
        
        self.datatableModel = None
        self.datatable = QTableView()
        
        previewBoxLayout.addWidget(self.datatable)
        previewBox.setLayout(previewBoxLayout)

        mainLayout.addWidget(importBox,0,0)
        mainLayout.addWidget(separatorBox,0,1)
        mainLayout.addWidget(otherBox,1,1)
        mainLayout.addWidget(filterBox,1,0)
        mainLayout.addWidget(columnBox,3,0,1,2)
        mainLayout.addWidget(previewBox,4,0,1,2)
        mainLayout.addWidget(buttonBox,5,0,1,2)
        
        self.delimTab.setChecked(True)
        
        QObject.connect(self.headerCheckBox, SIGNAL('stateChanged(int)'), self.refreshDataTable)
        QObject.connect(self.delimTab, SIGNAL('toggled(bool)'), self.updatePreview)
        QObject.connect(self.delimOther, SIGNAL('toggled(bool)'), self.updatePreview)
        QObject.connect(self.otherLineEdit, SIGNAL('textChanged(const QString&)'), self.otherDelimChanged)
        QObject.connect(self.textLineEdit, SIGNAL('textChanged(const QString&)'), self.textChanged)
        QObject.connect(self.quotedFieldCheckBox, SIGNAL('stateChanged(int)'), self.updatePreview)
        QObject.connect(self.skipCommentsCheckBox, SIGNAL('stateChanged(int)'), self.updatePreview)
        QObject.connect(self.stripCheckBox, SIGNAL('stateChanged(int)'), self.updatePreview)
        
        self.skipCommentsCheckBox.setCheckState(Qt.CheckState.Checked)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Data Import - [%s]" % (self.filename))
        self.show()
        #self.setFixedSize(self.width(),self.height())
        
        self.updatePreview()
    
    def sampleIndicatorChanged(self, index):
        self.updatePreview()
        
    def filterColChanged(self, index):
        if index>0:
            index -= 1
            self.sampleIndicatorComboBox.setEnabled(True)
            items = []
            data = self.parseData(tmp=True)
            if self.headerCheckBox.isChecked():
                data = data[1:]
            for x in data:
                try:
                    items.append(x[index])
                except IndexError:
                    pass
            items = list(frozenset(items))
            items.insert(0,'')
            self.sampleIndicatorComboBox.clear()
            self.sampleIndicatorComboBox.addItems(items)
        else:
            self.sampleIndicatorComboBox.clear()
            self.sampleIndicatorComboBox.setEnabled(False)
        
    def textChanged(self):
        if len(self.textLineEdit.text()) == 1:
            self.updatePreview()
    
    def otherDelimChanged(self):
        if len(self.otherLineEdit.text()) == 1:
            self.updatePreview()
        
    def parseData(self, preview=False, progress_cb=None, tmp=False):
        
        reg0 = None
        if self.skipCommentsCheckBox.isChecked() and self.commentLineEdit.text():
            reg0 = re.compile('^'+self.commentLineEdit.text())
            
        reg1 = None
        if self.stripCheckBox.isChecked() and self.stripLineEdit.text():
            reg1 = re.compile(self.stripLineEdit.text())
            
        lines = []
        l = len(self.rawdata)
        for i, line in enumerate(self.rawdata):
            if progress_cb:
                progress_cb(i+1,l)
            line = line.encode(self.charsetComboBox.itemText(self.charsetComboBox.currentIndex()))
            if reg0 and reg0.match(line):
                continue
            if reg1:
                line = reg1.sub('', line)
            lines.append(line)
            if preview and len(lines) == 100:
                break
        
        quotechar = None
        if self.quotedFieldCheckBox.isChecked() and self.textLineEdit.text():
            quotechar = str(self.textLineEdit.text())
        
        delim = None
        if self.delimTab.isChecked():
            delim = '\t'
        elif self.delimOther.isChecked() and self.otherLineEdit.text():
            delim = str(self.otherLineEdit.text())
            
        tmpData = None
        if not tmp and self.columnFilterComboBox.currentIndex() > 0 and self.sampleIndicatorComboBox.currentIndex() > 0:
            col = self.columnFilterComboBox.itemData(self.columnFilterComboBox.currentIndex())
            val = self.sampleIndicatorComboBox.itemText(self.sampleIndicatorComboBox.currentIndex())
            if self.headerCheckBox.isChecked():
                tmpData = [line for i,line in enumerate(csv.reader(lines, delimiter=delim, quotechar=quotechar)) if i==0 or line[col] ==  val]
            else:
                tmpData = [line for line in csv.reader(lines, delimiter=delim, quotechar=quotechar) if line[col] ==  val]
        else:
            tmpData = [line for line in csv.reader(lines, delimiter=delim, quotechar=quotechar)]
        if not tmp:
            self.data = tmpData
        return tmpData
            
        
    def updatePreview(self):
        self.parseData(preview=True)
        self.refreshDataTable()
    
    def doParse(self):
        self.done(1)
        
    def updateModel(self):
        if self.headerCheckBox.isChecked():
            self.datatableModel = DataModel(self.data, True)
        else:
            self.datatableModel = DataModel(self.data, False)

    def refreshDataTable(self):
        if not self.data:
            return
        self.updateModel()
        self.datatable.setModel(self.datatableModel)
        self.datatable.horizontalHeader().setVisible(True)
        self.datatable.verticalHeader().setVisible(True)
        self.datatable.setShowGrid(True)
        self.datatable.resizeColumnsToContents()
        self.datatable.resizeRowsToContents()
        headers = copy.copy(self.datatableModel.getHeader())
        headers.insert(0,None)
        if headers != self.header:
            self.updateHeaderCombo(self.statusCombo, headers)
            self.updateHeaderCombo(self.gazexCombo, headers)
            self.updateHeaderCombo(self.gazeyCombo, headers)
            self.updateHeaderCombo(self.timestampCombo, headers)
            self.updateHeaderCombo(self.trialCombo, headers)
            self.updateHeaderCombo(self.columnFilterComboBox, headers)
            self.header = headers
            
    def updateHeaderCombo(self, combobox, headers):
        combobox.clear()
        for i,v in enumerate(headers):
            if i == 0:
                combobox.addItem(v,None)
            else:
                combobox.addItem(v,i-1)
    
    def getSegments(self, status_cb=None):
        segments = []
        tidx = self.trialCombo.currentIndex()-1
        sidx = self.statusCombo.currentIndex()-1
        data = self.datatableModel.getData()
        header = self.datatableModel.getHeader()
        current = [header]
        status = []
        line = 0
        lines = len(data)
        trial = 1
        if tidx != -1:
            trial = data[line][tidx]
        while line < lines:
            if tidx != -1 and data[line][tidx] != trial:
                segments.append({'trial': trial, 'data': current, 'status': status})
                current = [header]
                status = []
                trial = data[line][tidx]
            if sidx == -1:
                status.append(True)
            else:
                status.append(self.comparisonCombo.itemData(self.comparisonCombo.currentIndex())(float(data[line][sidx]),float(self.comparisonValue.text())))
                
            current.append(data[line])
            line += 1
        segments.append({'trial': trial, 'data': current, 'status': status})
        return {'filename': self.filename,
                'segments': segments,
                'firstRowIsHeader': self.headerCheckBox.isChecked()}
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    dlg = ParseDlg('300fe9ab_2011-11-2_16-58-41.log')
    if dlg.exec_():
        dlg.parseData(progress_cb=lambda a,b: sys.stdout.write("%.3f\n" % (a/b*100)))
        dlg.updateModel()
        segments = dlg.getSegments()['segments']
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        for i, seg in enumerate(segments):
            print i+1,len(seg['data']),sum(seg['status'])/len(seg['status'])*100
    sys.exit()