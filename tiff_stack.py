
from PySide import QtGui, QtCore
import os

path = '/home/danielle/Documents/LMCE/'

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
        layout.addWidget(self.slider)
        self.setLayout(layout)


    def show_images(self):
        curr_pos = self.slider.sliderPosition()
        curr_img = self.image_files[curr_pos]
        self.my_image.load(self.path + '/' + curr_img)
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.my_image))

    def get_float(self):
        sorted_img_files = []
        for img in self.image_files:
            basename = img.rpartition('.')
            sorted_img_files.append(basename[0])
        sorted_img_files.sort(key=float)
        return sorted_img_files

"""
file_list = [f for f in sorted(os.listdir(path)) if f.endswith(".txt")]
os.chdir(path)
spectra = []
for each in file_list:
    spectra.append(SpectrumData.from_file(each))
collec = SpectrumCollection.from_spectrum_data_list(spectra)

app = QtGui.QApplication(sys.argv)
main = ImageStack(None)
main.show()
sys.exit(app.exec_())

"""