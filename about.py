from PySide.QtCore import *
from PySide.QtGui import *

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