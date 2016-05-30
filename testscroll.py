from PySide import QtCore, QtGui
import os,sys
from bgsub import SpectrumData
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

path = "/home/danielle/Documents/LMCE_one"

file_list = [f for f in sorted(os.listdir(path)) if f.endswith(".txt")]
os.chdir(path)
spectra = []
for each in file_list:
    spectra.append(SpectrumData.from_file(each))

#import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

qapp = QtGui.QApplication(sys.argv)
qwidget = QtGui.QWidget()
qwidget.setGeometry(QtCore.QRect(0, 0, 500, 500))
qlayout = QtGui.QHBoxLayout(qwidget)
qwidget.setLayout(qlayout)

qscroll = QtGui.QScrollArea(qwidget)
qscroll.setGeometry(QtCore.QRect(0, 0, 500, 500))
qscroll.setFrameStyle(QtGui.QFrame.NoFrame)
qlayout.addWidget(qscroll)

qscrollContents = QtGui.QWidget()
qscrollLayout = QtGui.QHBoxLayout(qscrollContents)
qscrollLayout.setGeometry(QtCore.QRect(0, 0, 1000, 1000))

qscroll.setWidget(qscrollContents)
qscroll.setWidgetResizable(True)

for spectrum in spectra:

    qfigWidget = QtGui.QWidget(qscrollContents)

    fig = Figure()
    canvas = FigureCanvas(fig)
    canvas.setParent(qfigWidget)
    toolbar = NavigationToolbar(canvas, qfigWidget)
    plt = fig.add_subplot(111)
    plt.scatter(*zip(*spectrum.info))
    #axvert = plt.axvline()
    #sfreq = Slider(axvert, 'vertical', 0, 1000)

    # place plot components in a layout
    plotLayout = QtGui.QVBoxLayout()
    plotLayout.addWidget(canvas)
    plotLayout.addWidget(toolbar)
    qfigWidget.setLayout(plotLayout)

    # prevent the canvas to shrink beyond a point
    # original size looks like a good minimum size
    canvas.setMinimumSize(canvas.size())

    qscrollLayout.addWidget(qfigWidget)

qwidget.show()
exit(qapp.exec_())