import csv
import os
import sys
from matplotlib import pyplot as plt

DEFAULT_PATH = "/home/danielle/Documents/LMCE"


def load_file(filename):
    """Loads file from directory ** needs input to be a fully qualified file path
    Returns a new list of tuples (x,y) containing points where x = wavenums and y = intensities"""
    if filename.endswith(".txt"):

        # Read in files row by row
        with open(filename, 'r') as csvfile:
            numreader = csv.reader(csvfile, delimiter='\t')
            curr_wavenums = []
            curr_intens = []
            for row in numreader:
                curr_wavenums.append(float(row[0]))
                curr_intens.append(float(row[1]))

            # Return a list of points where x = wavenumbers and y = intensities
            return zip(curr_wavenums, curr_intens)

def filter_negative(data):
    """Filters out negative data from spectrum data
    Returns original data without negative values"""
    return [elem for elem in data if elem[0] > 0]

def plot_spectrum(data):
    """Creates x-y scatter plot of the spectrum data"""
    plt.scatter(*zip(*data))
    plt.show()

def bg_subtract(data):
    """Returns background subtracted data set"""
    # TODO: from the horizontal line slider
    for i in range(len(data)):
        y_val = data[i][1]
        for j in range(i + 1, len(data)):
            if y_val == data[j][1]:
                return [(x, y - y_val) for x, y in data]
    min_y = min(data, key=lambda tup: tup[1])[1]
    return [(x, y - min_y) for x, y in data]

def trapezoidal_sum(data):
    """Calculates the area under the curve by trapezoidal method
    Two adjacent points in the data set are used to create a trapezoid and calculate its area
    Continues for all other points in the set and sums areas together,
    returning total area"""
    # TODO: check if points are within user inputted range
    total_area = 0

    # Iterates over all points in data set
    for index in range(len(data)-1):

        # Next adjacent point to current point
        next_point = data[index + 1]

        # Change in x between the points
        dx = next_point[0] - data[index][0]
        r_y = data[index][1]
        t_y = next_point[1] - r_y

        # Area of current trapezoid
        area = (r_y * dx) + (0.5 * dx * t_y)
        total_area += area

    return total_area

def specific_peak(w_num1, w_num2, data):

    culled_data = []

    for point in data:
        if w_num1 <= point[0] <= w_num2:
            culled_data.append(point)

def create_heatmap():

def main(path):
    file_list = sorted(os.listdir(path))
    os.chdir(path)
    spectra = []
    for each in file_list:
        print(each)
        spectrum = load_file(each)
        spectrum.sort(key=lambda tup: tup[0])
        spectrum = filter_negative(spectrum)
        spectrum = bg_subtract(spectrum)
        spectra.append(spectrum)
    plot_spectrum(spectra[-1])

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)