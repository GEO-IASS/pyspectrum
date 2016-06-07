import sys, os
from PySide import QtGui

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

        self.drop_down_x.currentIndexChanged.connect(self.selectionchange)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.drop_down_x)
        layout.addWidget(self.drop_down_y)
        self.setLayout(layout)

    def plot(self):

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        ax.scatter(*zip(*self.my_collec.spectra[0].info_flipped))

        # refresh canvas
        self.canvas.draw()

    def selectionchange(self):

        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_ys = list(self.my_collec.x_to_y.get(float(curr_x)))
        curr_ys = [str(each) for each in curr_ys]

        self.drop_down_y.clear()

        self.drop_down_y.addItems(curr_ys)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotDisplay(None, None)
    main.show()

    sys.exit(app.exec_())