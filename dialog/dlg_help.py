__author__ = 'Hoang'
import sys,os,codecs
from PyQt4 import QtGui
import myFuncs
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class hwDlgHelp(QtGui.QDialog):

    def __init__(self,parent=None):
        super(hwDlgHelp, self).__init__(parent)

        self.initUI()

    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
# OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        #f=os.popen("data/help.txt",'r')
        root_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        f=codecs.open(("data/help.txt"),mode='r',encoding='utf-8')
        help_content = f.read()
        f.close()

        longTxt = QtGui.QTextBrowser( )
        longTxt.setText(help_content)
        vbox.addWidget(longTxt)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        """
        btn_ok=QtGui.QPushButton()
        btn_ok.setText("Ok")
        btn_ok.clicked.connect(self.hide)
        """
        hbox.addWidget(buttons)

        self.setLayout(vbox)
        self.resize(500,400)
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Huong dan')
        self.show()


def main_():

    app = QtGui.QApplication(sys.argv)

    t=hwDlgHelp()

    sys.exit(app.exec_())


if __name__ == '__main__':
    #main_()
    pass