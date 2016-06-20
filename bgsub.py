"""
TODO: Module documentation
"""
from __future__ import print_function
import csv
import os
import sys
import re
import bisect
from operator import itemgetter, attrgetter
from pprint import pprint
from collections import OrderedDict

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from PySide import QtGui

from mplgui import PlotDisplay
from directory_dialog import DialogGUIBox

DEFAULT_PATH = "/home/danielle/Documents/LMCE"


class SpectrumCollection(object):

    def __init__(self, spectra, x_to_y):
        #: List of SpectrumData objects
        self.spectra = spectra
        #: Mapping of Xs to Ys for the speectra
        self.x_to_y = x_to_y
        self.num_xs = len(self.x_to_y.keys())
        # Find number of ys
        biggest = 0
        for y_list in self.x_to_y.values():
            biggest = len(y_list) if len(y_list) > biggest else biggest
        self.num_ys = biggest

    @classmethod
    def from_spectrum_data_list(cls, spectra):
        """Creates a new SpectrumCollection object from a SpectrumData list"""
        x_to_y = OrderedDict()
        # Sort the spectra by Y, then by X (relative ordering is maintained)
        spectra.sort(key=attrgetter("y"))
        spectra.sort(key=attrgetter("x"))
        # For all spectrum, build a map from xs to ys
        for spectrum in spectra:
            currx = spectrum.x
            if currx not in x_to_y:
                x_to_y[currx] = [spec.y for spec in spectra if spec.x == currx]
        return SpectrumCollection(spectra, x_to_y)

    def _xy_to_pixel(self, x, y):
        """Converts x,y coordinate to pixel grid location"""
        # Check if x and y are in our spectra
        if x not in self.x_to_y:
            raise ValueError
        elif y not in self.x_to_y[x]:
            raise ValueError
        # Find absolute index of where x and y are in the spectra
        x_coord = bisect.bisect_left(list(self.x_to_y.keys()), x)
        y_coord = bisect.bisect_left(self.x_to_y[x], y)
        return (x_coord, y_coord)

    def get_img_array(self, wavenum):
        """Constructs a numpy array containing the intesity at the wavenum"""
        img_array = np.zeros((self.num_xs, self.num_ys))
        # Iterate through the spectra and get the intensity value at wavenum
        for spectrum in self.spectra:
            i, j = self._xy_to_pixel(spectrum.x, spectrum.y)
            img_array[i][j] = spectrum.get_intens(wavenum)
        return np.flipud(np.rot90(img_array))

    def map_images(self):
        """Constructs a greyscale image of intensity at each pixel, for each wavenum"""
        wavenums = []
        for spectrum in self.spectra:
            wavenums = spectrum.info[1]
        for wavenum in wavenums:
            img_array = self.get_img_array(wavenum)
            im = Image.fromarray(img_array)
            im.save(str(wavenum) + ".tiff", "tiff")

    def get_heatmap_array(self, wnum_1, wnum_2):
        """Constructs a numpy array containing the intesity at the wavenum"""
        img_array = np.zeros((self.num_xs, self.num_ys))
        # Iterate through the spectra and get the intensity value at wavenum
        for spectrum in self.spectra:
            i, j = self._xy_to_pixel(spectrum.x, spectrum.y)
            img_array[i][j] = spectrum.trapezoidal_sum(wnum_1, wnum_2)
        return (np.rot90(img_array))

    def gen_heatmap(self, wnum_1, wnum_2):
        heatmap_array = self.get_heatmap_array(wnum_1, wnum_2)
        plt.imshow(heatmap_array, interpolation='bilinear', origin='lower', cmap='hot')
        plt.colorbar()
        plt.savefig("heat_map.png")

class SpectrumData(object):
    """ Object representing the spectrum at a single (X, Y) coordinate. """

    def __init__(self, x, y, info):
        self.x = x
        self.y = y
        self.info = np.array(info)
        self.info = np.rot90(self.info)
        self.info_flipped = np.rot90(self.info, 3)

    @classmethod
    def from_file(cls, filename, filter_negative=True):
        """
        Loads file from directory ** needs input to be a fully qualified file
        path.
        Returns a new list of tuples (x,y) containing points, where
        x = wavenums and y = intensities.
        """
        data = []
        # Read in files row by row
        with open(filename, 'r') as csvfile:
            numreader = csv.reader(csvfile, delimiter='\t')
            for row in numreader:
                # Filter out negatives if flag is on
                if not (filter_negative and float(row[0]) < 0):
                    data.append((float(row[0]), float(row[1])))
        # Sort by wavenum (increasing)
        data.sort(key=itemgetter(0))
        # Find bigX and bigY in the file name, add to SpectrumData object
        matches = re.findall('[+-]?[XY]_.[0-9]+\.[0-9]+', filename)
        X = None
        Y = None
        for match in matches:
            if "X_" in match:
                X = match[2:]
            if "Y_" in match:
                Y = match[2:]

        return SpectrumData(float(X), float(Y), data)

    def get_intens(self, wavenum):
        """Gets the intensity corresponding to the given wavenumber"""
        # 'Flip' array so that we can get only the wavenumbers
        wavenums = self.info[1]
        # Find index of requested wavenumber
        indx = np.searchsorted(wavenums, wavenum)
        # Return intensity at that indx
        return self.info[0][indx]

    def __repr__(self):
        return "SpectrumData(X = {}, Y = {})".format(self.x, self.y)

    def plot_spectrum(self, show=False):
        """Creates x-y scatter plot of the spectrum data"""
        plt.scatter(*zip(*self.info_flipped))
        plt.savefig("{}_{}_plot.png".format(self.x, self.y))
        if show:
            plt.show()

    def trapezoidal_sum(self, w_num1, w_num2):
        """Calculates the area under the curve by trapezoidal method.

        Two adjacent points in the data set are used to create a trapezoid and
        calculate its area.

        Continues for all other points in the set and sums areas together,
        returning total area.
        """
        # Get points within user inputted range
        culled_data = [intens for wavenum, intens in self.info_flipped if wavenum > w_num1 and wavenum < w_num2]
        total_area = 0
        # Iterates over all points in data set
        for index in range(len(culled_data) - 1):

            # Next adjacent point to current point
            next_point = culled_data[index + 1]

            # Change in x between the points
            dx = next_point - culled_data[index]
            r_y = culled_data[index]
            t_y = next_point - r_y

            # Area of current trapezoid
            area = (r_y * dx) + (0.5 * dx * t_y)
            total_area += area

        # Subtract area under horizontal line drawn between w_num1 & w_num2, if there is one
        if len(culled_data) > 1:
            under_area = subtract_lower(culled_data)
            total_area -= under_area
        else:
            total_area = culled_data[0]

        return total_area

    def plot_spec(self):
        """Creates x-y scatter plot of the spectrum data"""
        plt.scatter(*zip(*self.info_flipped))

def create_heatmap(spectra, w_num1, w_num2):

    num_xs, num_ys = get_num_xys(spectra)

    # Calculate all trapezoidal sums for every point
    transform = np.array([s.trapezoidal_sum(w_num1, w_num2) for s in spectra])

    # Turns 1D transform array into 2D ndarray
    transform = transform.reshape((num_ys, num_xs))

    # Plot
    plt.imshow(transform, interpolation='bilinear', origin='lower', cmap='Reds')
    plt.savefig("heat_map.png")


def get_num_xys(spectra):
    # Gets the number of Ys per X
    curr_x = spectra[0].x
    num_ys = 0
    for indx, spectrum in enumerate(spectra):
        if curr_x == spectrum.x:
            continue
        else:
            num_ys = indx - 1
            break
    # num_xs = int(spectra[0].x - spectra[-1].x)
    return (len(spectra) // num_ys, num_ys)


def subtract_lower(data):
    # Get min & max points according to x (assuming data is already sorted)
    p0 = data[0]
    p1 = data[-1]

    horiz = abs(p1 - p0)
    vert = abs(p1 - p0)

    area_tri = 0.5 * horiz * vert
    area_rec = horiz * vert

    total_area = area_rec + area_tri

    return total_area

def remap_image(spectra):
    """
    Takes the ith intensity from each spectrum with a matching wavenumber.
    This becomes a list of i arrays, which will then be converted
    to an intensity heatmap.
    """

    # Initialize the list
    intens_array = []

    # Iterate through each SpectrumData object in spectra list,
    # getting the ith itensity for each object and putting it in a sublist
    # put this sublist into intens_array
    for i in range(len(spectra[0].info)):
        sublist = []
        for spectrum in spectra:
            sublist.append(spectrum.info[i][1])
        intens_array.append(sublist)

    # Get the dimensions of the heatmap (numxs, numys)
    intens_array = np.array(intens_array)
    num_xs, num_ys = get_num_xys(spectra)

    # Reshape the lists in intens_array to an array numxs by numys dimensions
    reshaped_intens = []
    for ith_intens in intens_array:
        print(len(ith_intens))
        print(num_xs)
        print(num_ys)
        reshaped_intens.append(ith_intens.reshape(num_ys, num_xs))

    # Make heatmaps for all reshaped arrays, naming each by wavenumber
    wavenums = [wavenum for wavenum, _ in spectra[0].info]
    for wavenum, intens in zip(wavenums, reshaped_intens):
        arr_max = intens.max()
        norm_intens = np.array([each / arr_max for each in intens])
        im = Image.fromarray(norm_intens)
        im.save(str(wavenum) + ".tiff", "tiff")
        # plt.imshow(intens, origin='lower', cmap='binary')
        # plt.savefig("{}.png".format(wavenum))

def build_plot_display(path):
    file_list = [f for f in sorted(os.listdir(path)) if f.endswith(".txt")]
    os.chdir(path)
    spectra = []
    for each in file_list:
        spectra.append(SpectrumData.from_file(each))
    collec = SpectrumCollection.from_spectrum_data_list(spectra)
    # create_heatmap(spectra, 957, 968)
    # remap_image(spectra)
    #wavenum = 4016.413574
    #img_array = collec.get_img_array(wavenum)
    #im = Image.fromarray(img_array)
    #im.save(str(wavenum) + ".tiff", "tiff")
    # collec.map_images()
    # collec.gen_heatmap(926.365601, 970.27771)
    #collec.gen_heatmap(2907.666992, 3024.534180)
    # collec.gen_heatmap(2822.091309, 2879.218262)

    # Create the window with the collection, show and run
    window = PlotDisplay(collec, collec.gen_heatmap)
    window.setWindowTitle("PySpectrum Analyzer")
    window.show()


def main(path):
    # Must construct application first
    app = QtGui.QApplication(sys.argv)

    # Read user directory using dialog, which starts the GUI chain
    dialog = DialogGUIBox(build_plot_display)
    dialog.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)
