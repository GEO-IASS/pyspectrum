import csv
import os
import sys
from collections import namedtuple
from matplotlib import pyplot as plt
import re
import numpy as np
import math

DEFAULT_PATH = "/home/danielle/Documents/LMCE_one"

SpectrumData = namedtuple("SpectrumData", ['X', 'Y', 'info'])

def load_file(filename: str) -> SpectrumData:
    """Loads file from directory ** needs input to be a fully qualified file path
    Returns a new list of tuples (x,y) containing points where x = wavenums and y = intensities"""

    data = None

    if filename.endswith(".txt"):

        # Read in files row by row
        with open(filename, 'r') as csvfile:
            numreader = csv.reader(csvfile, delimiter='\t')
            curr_wavenums = []
            curr_intens = []
            for row in numreader:
                curr_wavenums.append(float(row[0]))
                curr_intens.append(float(row[1]))

            # Create a list of points (x,y) where x = wavenumbers and y = intensities
            data = list(zip(curr_wavenums, curr_intens))

    # Find bigX and bigY in the file name, append them to SpectrumData object
    matches = re.findall('[+-]?[XY]_.[0-9]+\.[0-9]+', filename)

    X = None
    Y = None

    for match in matches:
        if "X_" in match:
            X = match[2:]

        if "Y_" in match:
            Y = match[2:]

    return SpectrumData(X, Y, data)

def filter_negative(data: SpectrumData) -> SpectrumData:
    """Filters out negative data from spectrum datas
    Returns original data without negative values"""
    # return [elem for elem in data if elem > 0]
    return SpectrumData(data.X, data.Y, [elem for elem in data.info if elem[0] and elem[1] > 0])

def plot_spectrum(data: SpectrumData):
    """Creates x-y scatter plot of the spectrum data"""
    plt.scatter(*zip(*data.info))
    plt.show()

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

def trapezoidal_sum(data: list, w_num1: int, w_num2: int) -> float:
    """Calculates the area under the curve by trapezoidal method
    Two adjacent points in the data set are used to create a trapezoid and calculate its area
    Continues for all other points in the set and sums areas together,
    returning total area
    w_num1 = x @ left vertical
    w_num2 = x @ right vertical
    """

    # Check if points are within user inputted range
    culled_data = []
    for point in data:
        if w_num1 <= point[0] <= w_num2:
            culled_data.append(point)

    total_area = 0

    # Iterates over all points in data set
    for index in range(len(culled_data)-1):

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

def create_heatmap(spectra: list, w_num1: int, w_num2: int):

    master_list = []

    X_list = []
    for each in spectra:
        X_list.append(each.X)
    X_list.sort()
    for X in X_list:
        temp = []
        for SD in spectra:
            if SD.X == X:
                temp.append((SD.Y, SD.info))
            temp.sort(key=lambda tup: tup[0])
        trap_sums = []
        for y, info in temp:
            trap_sums.append(trapezoidal_sum(info, w_num1, w_num2))
        master_list.append(trap_sums)

    print(master_list)

    # Transpose matrix
    transform = []
    if len(master_list) > 1:
        for i in range(len(master_list[0])):
            transpose = []
            for j in range(len(master_list)):
                transpose.append(master_list[j][i])
            transform.append(transpose)
    else:
        transform = [master_list]

    # Convert to numpy array
    transform = np.array(transform)

    # Plot
    plt.pcolor(transform, cmap=plt.cm.Blues)
    plt.show()

def subtract_lower(data: list):

    # Get lowest and highest points according to x
    data.sort(key=lambda tup: tup[0])
    p0 = data[0]
    p1 = data[-1]

    # slope = (p1[1] - p0[1])/(p1[0] - p0[0])
    # dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1])

    horiz = abs(p1[1] - p0[1])
    vert = abs(p1[0] - p0[0])

    area_tri = 0.5 * horiz * vert

    area_rec = horiz * vert

    total_area = area_rec + area_tri

    return total_area

def main(path):
    file_list = sorted(os.listdir(path))
    os.chdir(path)
    spectra = []
    for each in file_list:
        spectrum = load_file(each)
        spectrum.info.sort(key=lambda tup: tup[0])
        spectrum = filter_negative(spectrum)
        spectra.append(spectrum)
        plot_spectrum(spectrum)
    create_heatmap(spectra, 3000, 4000)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)