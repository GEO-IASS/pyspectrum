import csv
# go through the txt file
# get first x and y, put wavenum & intens in new file
# if next x and y the same as first, put wavenum & intens in same file
# if next x and y are different, start new txt file and put wavenum & intens there
# repeat
from pyspec import SpectrumData, SpectrumCollection
from PIL import Image

def from_line_file(filename, filter_negative=True):
    """
    Loads file from directory ** needs input to be a fully qualified file
    path.
    Returns a new list of tuples (x,y) containing points, where
    x = wavenums and y = intensities.
    """
    spectra = []
    # Read in files row by row
    with open(filename, 'r') as csvfile:
        numreader = csv.reader(csvfile, delimiter='\t')
        data = []
        last_seen_xy = None
        for row in numreader:
            # First row - just use the first X/Y we see
            if last_seen_xy is None:
                last_seen_xy = (float(row[0]), float(row[1]))
            else:
                # Check if current row X/Y is the same as the last one we saw
                new_xy = (float(row[0]), float(row[1]))
                # If they are different, make a data object out of the data we've collected so far
                if last_seen_xy[0] != new_xy[0] or last_seen_xy[1] != new_xy[1]:
                    data_obj = SpectrumData(last_seen_xy[0], last_seen_xy[1], data)
                    spectra.append(data_obj)
                    last_seen_xy = new_xy
                    data = []
            if not (filter_negative and float(row[2]) < 0):
                data.append((float(row[2]), float(row[3])))
    # Once file ends, make a SpectrumData object with remaining data
    if len(data) > 0:
        spectra.append(SpectrumData(last_seen_xy[0], last_seen_xy[1], data))
    # Use this method which builds the X->Y mapping for us into the SpectrumCollection object
    return SpectrumCollection.from_spectrum_data_list(spectra)

path = "/home/danielle/Documents/Raman Linescan/TP,U,L,1_linescan.txt"
collec = from_line_file(path)
collec.gen_heatmap_linescan(2907.666992, 3024.534180)