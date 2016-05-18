"""
TODO: Module documentation
"""
import csv
import os
import sys
import re
from operator import itemgetter, attrgetter
from pprint import pprint

import numpy as np
from matplotlib import pyplot as plt

DEFAULT_PATH = "/home/danielle/Documents/Test/Test"

class SpectrumData(object):
    """ Object representing the spectrum at a single (X, Y) coordinate. """

    def __init__(self, x: float, y: float, info: list((float, float))):
        self.x = x
        self.y = y
        self.info = np.array(info)

    @classmethod
    def from_file(cls, filename: str, filter_negative=True):
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
        # Sort by X (increasing)
        data.sort(key=itemgetter(0))
        # Find bigX and bigY in the file name, append to SpectrumData object
        matches = re.findall('[+-]?[XY]_.[0-9]+\.[0-9]+', filename)
        X = None
        Y = None
        for match in matches:
            if "X_" in match:
                X = match[2:]
            if "Y_" in match:
                Y = match[2:]

        return SpectrumData(float(X), float(Y), data)

    def __repr__(self):
        return "SpectrumData(X = {}, Y = {})".format(self.x, self.y)

    def plot_spectrum(self, show=False):
        """Creates x-y scatter plot of the spectrum data"""
        plt.scatter(*zip(*self.info))
        plt.savefig("{}_{}_plot.png".format(self.x, self.y))
        if show:
            plt.show()

    def trapezoidal_sum(self, w_num1: float, w_num2: float) -> float:
        """Calculates the area under the curve by trapezoidal method.

        Two adjacent points in the data set are used to create a trapezoid and
        calculate its area.

        Continues for all other points in the set and sums areas together,
        returning total area.
        """
        # Get points within user inputted range
        start_x = 0
        for i in range(len(self.info)):
            if self.info[i][0] > w_num1:
                start_x = i
                break
        end_x = len(self.info)
        for i in range(len(self.info) - 1, 0, -1):
            if self.info[i][0] < w_num2:
                end_x = i + 1
                break
        # Culled data is a memory view into our array
        culled_data = self.info[start_x:end_x]

        total_area = 0
        # Iterates over all points in data set
        for index in range(len(culled_data) - 1):

            # Next adjacent point to current point
            next_point = culled_data[index + 1]

            # Change in x between the points
            dx = next_point[0] - culled_data[index][0]
            r_y = culled_data[index][1]
            t_y = next_point[1] - r_y

            # Area of current trapezoid
            area = (r_y * dx) + (0.5 * dx * t_y)
            total_area += area

        # Subtract area under horizontal line drawn between w_num1 & w_num2
        under_area = subtract_lower(culled_data)
        total_area -= under_area

        return total_area


def bg_subtract(data: SpectrumData) -> SpectrumData:
    """Returns background subtracted data set"""
    # TODO: from the horizontal line slider
    for i in range(len(data.info)):
        y_val = data.info[i][1]
        for j in range(i + 1, len(data.info)):
            if y_val == data.info[j][1]:
                return [(x, y - y_val) for x, y in data.info]
    min_y = min(data.info, key=lambda tup: tup[1])[1]
    return SpectrumData(data.X, data.Y, [(x, y - min_y) for x, y in data.info])


def create_heatmap(spectra: list, w_num1: int, w_num2: int):
    spectra.sort(key=attrgetter("y"))
    spectra.sort(key=attrgetter("x"))
    pprint(spectra)
    num_xs, num_ys = get_num_xys(spectra)
    # Calculate all trapezoidal sums for every point
    transform = np.array([s.trapezoidal_sum(w_num1, w_num2) for s in spectra])
    # Turns 1D transform array into 2D ndarray
    transform = transform.reshape((num_ys, num_xs))
    print(transform)
    # Plot
    plt.imshow(transform, interpolation='bilinear', origin='lower', cmap='Reds')
    plt.savefig("heat_map.png")


def get_num_xys(spectra: list) -> (int, int):
    # Gets the number of Ys per X
    curr_x = spectra[0].x
    num_ys = 0
    for indx, spectrum in enumerate(spectra):
        if curr_x == spectrum.x:
            continue
        else:
            num_ys = indx
            break
    return (len(spectra) // num_ys, num_ys)


def subtract_lower(data: np.array):
    # Get min & max points according to x (assuming data is already sorted)
    p0 = data[0]
    p1 = data[-1]

    horiz = abs(p1[1] - p0[1])
    vert = abs(p1[0] - p0[0])

    area_tri = 0.5 * horiz * vert
    area_rec = horiz * vert

    total_area = area_rec + area_tri

    return total_area

def remap_image(spectra: list):
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
        reshaped_intens.append(ith_intens.reshape(num_ys, num_xs))

    # Make heatmaps for all reshaped arrays, naming each by wavenumber
    wavenums = [wavenum for wavenum, _ in spectra[0].info]
    for wavenum, intens in zip(wavenums, reshaped_intens):
        plt.imshow(intens, origin='lower', cmap='binary')
        plt.savefig("{}.png".format(wavenum))

def main(path):
    file_list = [f for f in sorted(os.listdir(path)) if f.endswith(".txt")]
    os.chdir(path)
    spectra = []
    for each in file_list:
        spectra.append(SpectrumData.from_file(each))
    # create_heatmap(spectra, 820, 985)
    remap_image(spectra)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)
