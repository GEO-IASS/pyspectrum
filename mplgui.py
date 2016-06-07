import sys, os
from PySide import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class PlotDisplay(QtGui.QDialog):

    def __init__(self, spectrum_collec, parent=None):

        super(PlotDisplay, self).__init__(parent)

        # Set spectrum collection instance variable/member
        self.my_collec = spectrum_collec

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # a button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # add a combobox for all X values
        self.drop_down_x = QtGui.QComboBox()
        x_list = list(self.my_collec.x_to_y.keys())
        x_list = [str(each) for each in x_list]
        self.drop_down_x.addItems(x_list)

        # add a combobox for Y's corresponding to first X
        self.drop_down_y = QtGui.QComboBox()
        y_list = list(self.my_collec.x_to_y.values())
        y_list = [str(each) for each in y_list[0]]
        self.drop_down_y.addItems(y_list)

        self.drop_down_x.currentIndexChanged.connect(self.selection_change)

        # create label
        self.label_x = QtGui.QLabel("Select X:")
        self.label_y = QtGui.QLabel("Select Y:")

        # create split layout for displaying combo boxes side by side
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.label_x)
        splitter.addWidget(self.drop_down_x)
        splitter.addWidget(self.label_y)
        splitter.addWidget(self.drop_down_y)

        # add slider
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld.setMinimum(0)
        self.wavenums = self.get_wavenums()
        self.sld.setMaximum(len(self.wavenums)-1)
        self.sld.setTickInterval(1)
        curr_sld = self.sld.sliderPosition()
        self.sld.valueChanged.connect(self.sld_change)

        # text edit to display wavenumber
        self.textedit = QtGui.QTextEdit()

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(splitter)
        layout.addWidget(self.sld)
        layout.addWidget(self.textedit)
        #layout.addWidget(self.drop_down_x)
        #layout.addWidget(self.drop_down_y)
        self.setLayout(layout)

    def plot(self):
        """"Create matplotlib plot for specific X and Y contained in my_collec"""

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # get data from combo box
        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_y = self.drop_down_y.itemText(self.drop_down_y.currentIndex())

        spectra_list = self.my_collec.spectra
        print(spectra_list)
        for i, spectrum in enumerate(spectra_list):
            if (spectrum.x == float(curr_x)) and (spectrum.y == float(curr_y)):
                ax.scatter(*zip(*self.my_collec.spectra[i].info_flipped))

        # plot data
        #ax.scatter(*zip(*self.my_collec.spectra[0].info_flipped))

        # refresh canvas
        self.canvas.draw()

    def selection_change(self):
        """If the X drop down value changes, get the matching Y's corresponding to the new X"""

        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_ys = list(self.my_collec.x_to_y.get(float(curr_x)))
        curr_ys = [str(each) for each in curr_ys]

        self.drop_down_y.clear()
        self.drop_down_y.addItems(curr_ys)

    def get_wavenums(self):
        wavenums = []
        for spectrum in self.my_collec.spectra:
            wavenums = spectrum.info[1]

        return wavenums

    def sld_change(self):
        curr_pos = self.sld.sliderPosition()
        curr_wavenum = self.wavenums[curr_pos]

        self.textedit.setText(str(curr_wavenum))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotDisplay(None)
    main.show()

    sys.exit(app.exec_())