import sys, os
from PySide import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from tiff_stack import ImageStack


class PlotDisplay(QtGui.QDialog):

    def __init__(self, spectrum_collec, gen_heatmap, path, parent=None):

        super(PlotDisplay, self).__init__(parent)

        # Set spectrum collection instance variable/member
        self.my_collec = spectrum_collec

        # a figure instance to plot on
        self.figure = plt.figure()

        # callback to gen heatmap
        self.gen_heatmap = gen_heatmap

        self.path = path

        self.stack = ImageStack(self.my_collec, self.path)

        self.listview = QtGui.QListView()

        self.scroll_img = QtGui.QScrollArea()

        self.ax = self.figure.add_subplot(111)

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

        # add left slider
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld.setMinimum(0)
        self.wavenums = self.get_wavenums()
        self.sld.setMaximum(len(self.wavenums) - 1)
        self.sld.setTickInterval(1)
        self.curr_sld = self.sld.sliderPosition()
        self.sld.valueChanged.connect(self.sld_change)

        #TODO
        # add right slider
        self.sld_2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld_2.setMinimum(0)
        self.wavenums = self.get_wavenums()
        self.sld_2.setMaximum(len(self.wavenums)-1)
        self.sld_2.setTickInterval(1)
        self.curr_sld_2 = self.sld_2.sliderPosition()
        self.sld_2.valueChanged.connect(self.sld_change)

        # add line
        self.vert_line = None
        self.vert_line_2 = None

        # text edit to display wavenumber
        self.textedit = QtGui.QLabel()
        self.textedit.setStyleSheet('background-color: white')

        #TODO
        self.textedit_2 = QtGui.QLabel()
        self.textedit_2.setStyleSheet('background-color: white')

        # horizontal layout to hold slider and text edit box
        hslider_text = QtGui.QHBoxLayout()
        hslider_text.addWidget(self.sld, 2)
        hslider_text.addWidget(self.textedit, 1)

        # group box to group elements together
        gbox = QtGui.QGroupBox("Peak Selection")
        gbox.setLayout(hslider_text)
        qpalette = QtGui.QPalette()
        qpalette.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        gbox.setPalette(qpalette)
        #gbox.setStyleSheet("QGroupBox {border-radius: 9px; border:1px solid rgb(0, 0, 0); margin-top: 0.5em}")

        #TODO
        hslider_text_2 = QtGui.QHBoxLayout()
        hslider_text_2.addWidget(self.sld_2, 2)
        hslider_text_2.addWidget(self.textedit_2, 1)

        # group box to group elements together
        gbox_2 = QtGui.QGroupBox("Peak Selection")
        gbox_2.setLayout(hslider_text_2)
        qpalette = QtGui.QPalette()
        qpalette.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        gbox.setPalette(qpalette)

        # add button for heat map generation
        self.hm_button = QtGui.QPushButton('Generate Heatmap')
        self.hm_button.clicked.connect(self.hm_make)

        self.map_img = QtGui.QPushButton('Map Images')
        self.map_img.clicked.connect(self.img_stack)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.hm_button)
        layout.addWidget(self.map_img)
        layout.addWidget(splitter)
        layout.addWidget(gbox)
        layout.addWidget(gbox_2)
        self.setLayout(layout)

    def plot(self):
        """"Create matplotlib plot for specific X and Y contained in my_collec"""

        # create an axis

        # discards the old graph
        self.ax.hold(False)

        # get data from combo box
        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_y = self.drop_down_y.itemText(self.drop_down_y.currentIndex())

        # plot data
        spectra_list = self.my_collec.spectra
        print(spectra_list)
        for i, spectrum in enumerate(spectra_list):
            if (spectrum.x == float(curr_x)) and (spectrum.y == float(curr_y)):
                self.ax.scatter(*zip(*self.my_collec.spectra[i].info_flipped))

        # add left vert line
        self.vert_line = self.ax.axvline(x = 0)

        # add right vert line
        self.vert_line_2 = self.ax.axvline(x = 0)

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

        self.vert_line.remove()
        self.vert_line_2.remove()

        curr_pos = self.sld.sliderPosition()
        curr_wavenum = self.wavenums[curr_pos]

        curr_pos_2 = self.sld_2.sliderPosition()
        curr_wavenum_2 = self.wavenums[curr_pos_2]

        self.textedit.setText(str(curr_wavenum))
        self.textedit_2.setText(str(curr_wavenum_2))

        self.vert_line = self.ax.axvline(x = curr_wavenum)
        self.vert_line_2 = self.ax.axvline(x = curr_wavenum_2)

        self.canvas.draw()

    def hm_make(self):
        curr_pos = self.sld.sliderPosition()
        curr_wavenum = self.wavenums[curr_pos]

        curr_pos_2 = self.sld_2.sliderPosition()
        curr_wavenum_2 = self.wavenums[curr_pos_2]

        self.gen_heatmap(curr_wavenum, curr_wavenum_2)

    def img_stack(self):
        self.stack.show()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotDisplay(None, None, None)
    main.show()

    sys.exit(app.exec_())