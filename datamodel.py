from PySide.QtCore import QAbstractTableModel, Qt

class DataModel(QAbstractTableModel): 

    def __init__(self, datain=[], firstRowAsHeader=False, parent=None):
        super(DataModel, self).__init__(parent)

        self.firstRowAsHeader = firstRowAsHeader
        self.arraydata = datain
        self.headerdata = ['Column %d'%i for i in range(1,len(self.arraydata[0])+1)]

    def rowCount(self, parent=None):
        if self.arraydata:
            if self.firstRowAsHeader:
                return len(self.arraydata)-1
            else:
                return len(self.arraydata)
        else:
            return 0

    def columnCount(self, parent=None):
        if self.arraydata:
            return len(self.arraydata[0])
        else:
            return 0

    def getHeader(self):
        if self.firstRowAsHeader:
            return self.arraydata[0]
        else:
            return self.headerdata

    def getData(self):
        if self.firstRowAsHeader:
            return self.arraydata[1:]
        else:
            return self.arraydata

    def data(self, index, role):
        if not index.isValid(): 
            return None
        if not 0 <= index.row() < self.rowCount():
            return None
        if role != Qt.DisplayRole: 
            return None
        try:
            if self.firstRowAsHeader:
                return self.arraydata[index.row()+1][index.column()]
            else:
                return self.arraydata[index.row()][index.column()]
        except IndexError:
            pass
        return None

    def headerData(self, col, orientation, role):
        try:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                if self.firstRowAsHeader:
                    return self.arraydata[0][col]
                else:
                    return self.headerdata[col]
        except IndexError:
            pass
        return None