from PySide.QtCore import QAbstractTableModel, Qt

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
        try:
            return self.arraydata[index.row()][index.column()]
        except IndexError:
            pass
        return None

    def headerData(self, col, orientation, role):
        try:
            if self.headerdata and orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self.headerdata[col]
        except IndexError:
            pass
        return None