
from PySide import QtGui, QtCore
import os

class ImageStack(QtGui.QWidget):
    def __init__(self, spectrum_collec, path, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.path = path

        self.image_files = [f for f in sorted(os.listdir(path)) if f.endswith(".tiff")]
        self.image_files = self.get_float()

        self.button = QtGui.QPushButton('Images')
        self.button.clicked.connect(self.show_images)

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.image_files)-1)
        self.slider.setTickInterval(1)
        self.curr_img_indx = self.slider.sliderPosition()
        self.slider.valueChanged.connect(self.show_images)

        # text next to slider showing file name
        self.sld_text = QtGui.QLabel()
        self.sld_text.setStyleSheet('background-color: white')

        # layout to hold slider and text
        sld_text_box = QtGui.QHBoxLayout()
        sld_text_box.addWidget(self.slider, 2)
        sld_text_box.addWidget(self.sld_text, 1)

        # group box to hold layout
        self.gbox_sld = QtGui.QGroupBox()
        self.gbox_sld.setLayout(sld_text_box)
        self.gbox_sld.setContentsMargins(0, 0, 0, 0)

        self.my_collec = spectrum_collec

        # initialize image and label for gui
        self.my_image = QtGui.QImage()
        self.label = QtGui.QLabel()

        # set label to show first image
        if len(self.image_files) > 0:
            self.my_image.load(path + '/' + self.image_files[0])
            self.label.setPixmap(QtGui.QPixmap.fromImage(self.my_image))

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.gbox_sld)
        self.setLayout(layout)

    def show_images(self):
        curr_pos = self.slider.sliderPosition()
        curr_img = self.image_files[curr_pos]
        self.sld_text.setText(str(self.image_files[curr_pos]))
        self.my_image.load(self.path + '/' + curr_img)
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.my_image))

    def get_float(self):
        sorted_img_files = []
        for img in self.image_files:
            basename = img.rpartition('.')
            sorted_img_files.append(basename[0])
        sorted_img_files.sort(key=float)
        return sorted_img_files



