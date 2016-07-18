import sys, os
from PySide import QtGui, QtCore
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from tiff_stack import ImageStack

class PlotDisplay(QtGui.QDialog):
    """Creates the main application window"""

    def __init__(self, spectrum_collec, gen_heatmap, map, path, parent=None):

        super(PlotDisplay, self).__init__(parent)

        # Set spectrum collection instance variable/member
        self.my_collec = spectrum_collec

        # a figure instance to plot on
        self.figure = plt.figure()

        # callback to gen heatmap
        self.gen_heatmap = gen_heatmap

        # callback to map images
        self.map = map

        #self.lin_reg = lin_reg

        # initializations for image stack creation
        self.path = path
        self.stack = ImageStack(self.my_collec, self.path)
        self.stack.setWindowTitle('TIFF Image Stack')

        self.ax = self.figure.add_subplot(111)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # a button connected to `plot` method
        self.button = QtGui.QPushButton('Plot Spectrum')
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

        # add left vertical line slider for peak selection
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld.setMinimum(0)
        self.wavenums = self.get_wavenums()
        self.sld.setMaximum(len(self.wavenums) - 1)
        self.sld.setTickInterval(1)
        self.curr_sld = self.sld.sliderPosition()
        self.sld.valueChanged.connect(self.sld_change)

        # add right vertical line slider for peak selection
        self.sld_2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld_2.setMinimum(0)
        self.wavenums = self.get_wavenums()
        self.sld_2.setMaximum(len(self.wavenums)-1)
        self.sld_2.setTickInterval(1)
        self.curr_sld_2 = self.sld_2.sliderPosition()
        self.sld_2.valueChanged.connect(self.sld_change)

        # initialize left and right lines to start at None
        self.vert_line = None
        self.vert_line_2 = None

        # text edit to display wavenumber for left slider
        self.textedit = QtGui.QLabel()
        self.textedit.setStyleSheet('background-color: white')

        # text edit to display wavenumber for right slider
        self.textedit_2 = QtGui.QLabel()
        self.textedit_2.setStyleSheet('background-color: white')

        # horizontal layout to hold slider and text edit box
        hslider_text = QtGui.QHBoxLayout()
        hslider_text.addWidget(self.sld, 2)
        hslider_text.addWidget(self.textedit, 1)

        # group box to group left slider and text elements together
        gbox = QtGui.QGroupBox("Left")
        gbox.setLayout(hslider_text)
        qpalette = QtGui.QPalette()
        qpalette.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        gbox.setPalette(qpalette)

        # set layout of left slider group box
        hslider_text_2 = QtGui.QHBoxLayout()
        hslider_text_2.addWidget(self.sld_2, 2)
        hslider_text_2.addWidget(self.textedit_2, 1)

        # group box to group right slider and text elements together
        gbox_2 = QtGui.QGroupBox("Right")
        gbox_2.setLayout(hslider_text_2)
        qpalette = QtGui.QPalette()
        qpalette.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        gbox.setPalette(qpalette)

        # set layout of right slider group box
        slider_layout = QtGui.QVBoxLayout()
        slider_layout.addWidget(gbox)
        slider_layout.addWidget(gbox_2)

        slider_group = QtGui.QGroupBox("Peak Selection")
        slider_group.setLayout(slider_layout)

        # add button for heat map generation
        self.hm_button = QtGui.QPushButton('Generate Heatmap')
        self.hm_button.clicked.connect(self.hm_make)

        # add button for image stack pop out window
        self.map_img = QtGui.QPushButton('View Image Stack')
        self.map_img.clicked.connect(self.img_stack)

        # add baseline correction button
        self.bg_test = QtGui.QPushButton('Baseline Correction')
        self.bg_test.clicked.connect(self.rb_test)

        # set the layout of main window, adding all widgets
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(splitter)
        layout.addWidget(slider_group)
        layout.addWidget(self.hm_button)
        layout.addWidget(self.map_img)
        layout.addWidget(self.bg_test)
        self.setLayout(layout)

    def plot(self):
        """"Create matplotlib plot for specific X and Y contained in my_collec"""

        # discards the old graph
        self.ax.hold(False)

        # get data from combo box
        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_y = self.drop_down_y.itemText(self.drop_down_y.currentIndex())

        # plot data
        spectra_list = self.my_collec.spectra
        for i, spectrum in enumerate(spectra_list):
            if (spectrum.x == float(curr_x)) and (spectrum.y == float(curr_y)):
                self.ax.scatter(*zip(*self.my_collec.spectra[i].info_flipped))
                self.ax.grid('on')

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
        """"Makes a list of all wavenums in spectra"""
        wavenums = []
        for spectrum in self.my_collec.spectra:
            wavenums = spectrum.info[1]

        wavenums.sort()
        return wavenums

    def sld_change(self):
        """If left and/or right slider changes, set respective text to correct wavenumber, move line
        vertical line to correct position"""

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
        """
        Generate heatmap using values selected from left and right sliders
        """
        curr_pos = self.sld.sliderPosition()
        curr_wavenum = self.wavenums[curr_pos]

        curr_pos_2 = self.sld_2.sliderPosition()
        curr_wavenum_2 = self.wavenums[curr_pos_2]

        self.ax.grid('off')
        self.gen_heatmap(curr_wavenum, curr_wavenum_2)


    def img_stack(self):
        """
        Show scrollable set of TIFF images
        """
        file_names = [f for f in sorted(os.listdir(self.path)) if f.endswith(".tiff")]
        if len(file_names) == 0:
            self.map()
        self.stack.show()

    def bg_sub_test(self):
        """
        Background subtraction using linear regression method
        """
        curr_pos = self.sld.sliderPosition()
        curr_wavenum = self.wavenums[curr_pos]

        curr_pos_2 = self.sld_2.sliderPosition()
        curr_wavenum_2 = self.wavenums[curr_pos_2]

        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_y = self.drop_down_y.itemText(self.drop_down_y.currentIndex())

        spectra_list = self.my_collec.spectra
        for i, spectrum in enumerate(spectra_list):
            if (spectrum.x == float(curr_x)) and (spectrum.y == float(curr_y)):

                intens = self.my_collec.spectra[i].info[0]

                wavenums = self.my_collec.spectra[i].info[1]

                btwn_wavenums = []
                btwn_intens = []

                for i, wavenum in enumerate(wavenums):
                    if wavenum <= curr_wavenum_2 and wavenum >= curr_wavenum:
                        btwn_wavenums.append(wavenum)
                        btwn_intens.append(intens[i])

                new_y_list = []

                slope, intercept = self.lin_reg(btwn_wavenums, btwn_intens)

                for i, y in enumerate(intens):
                    fit_y = slope * wavenums[i] + intercept
                    y -= fit_y
                    if y < 0:
                        y = 0
                    new_y_list.append(y)

                print(len(wavenums), len(new_y_list))

                new_plot = np.column_stack((wavenums, new_y_list))
                self.ax.scatter(*zip(*new_plot))

                self.canvas.draw()

    def rb_test(self):
        """
        Background/baseline subtraction using 'rubberband correction' method
        """
        # get data from combo box
        curr_x = self.drop_down_x.itemText(self.drop_down_x.currentIndex())
        curr_y = self.drop_down_y.itemText(self.drop_down_y.currentIndex())

        # get vertex points
        curr_spec = None
        curr_spec_plt = None
        spectra_list = self.my_collec.spectra
        for i, spectrum in enumerate(spectra_list):
            if (spectrum.x == float(curr_x)) and (spectrum.y == float(curr_y)):
                curr_spec = self.my_collec.spectra[i]

        # Separate x and y values into two separate lists
        x = curr_spec.info[1]
        y = curr_spec.info[0]

        # Zip to create np array of (x, y) tuples
        zipped = np.column_stack((x, y))

        # Find the convex hull, where array v contains the indices of the convex hull
        # vertex points arranged in a counter clockwise direction
        v = ConvexHull(zipped).vertices

        # Rotate convex hull vertices until v starts from the lowest one
        v = np.roll(v, -v.argmin())

        # Leave only the ascending part
        v = v[:v.argmax()]

        # Create baseline using linear interpolation between vertices
        bsln = np.interp(x, x[v], y[v])

        # Find new y values using baseline
        new_y = []
        for i, point in enumerate(y):
            point -= bsln[i]
            new_y.append(point)

        # convert list of x and new y's into an np array of tuples
        x_y = np.column_stack((x, new_y))

        # plot the new spectrum
        self.ax.scatter(*zip(*x_y))

        self.ax.grid(which='both')

        # add left vert line
        self.vert_line = self.ax.axvline(x = 0)

        # add right vert line
        self.vert_line_2 = self.ax.axvline(x = 0)

        self.canvas.draw()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = PlotDisplay(None, None, None, None)
    main.show()

    sys.exit(app.exec_())