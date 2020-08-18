import numpy as np
import pandas as pd

import glob
import pickle

def pickle_read(file_name):
    with open(file_name, "rb") as file:

        dict_ = pickle.load(file)
    return dict_

def pickle_write(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

total_data = []

for file_name in glob.glob("*.pkl"):

    try:
        total_data.append(pickle_read(file_name))
        print(file_name)

    except:
        pass

pickle_write(total_data, "total_data.pkl")