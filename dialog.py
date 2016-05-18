import sys
from PySide import QtGui
import os


class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        # Folder Browser
        lbBroswer = QtGui.QLabel('Directory:', self)
        lbBroswer.move(15, 40)

        self.etBrowser = QtGui.QLineEdit('', self)
        self.etBrowser.resize(210,20)
        self.etBrowser.move(90, 37)
        self.etBrowser.setEnabled(0)
        self.etBrowser.isReadOnly = 0

        btnBrowse = QtGui.QPushButton('Browse...', self)
        btnBrowse.setToolTip('Select directory for project location.')
        btnBrowse.resize(70,20)
        btnBrowse.move(305, 37)
        btnBrowse.clicked.connect(self.selectDirectory)

        self.setWindowTitle('Folder Utility')
        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def selectDirectory(self):

        selected_directory = QtGui.QFileDialog.getExistingDirectory(self)
        self.etBrowser.setText(selected_directory)

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()