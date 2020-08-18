import numpy as np
import pandas as pd

import requests
import shelve
import time
import pickle

less_than_n = np.random.randint(1e8, 9.9e8)

request = requests.get(f"https://api.opendota.com/api/proMatches?less_than_match_id=5{less_than_n}")

# Just stores the first table from the api.
pro_matches = pd.DataFrame(request.json())

detailed_matches = dict()

# Iterate through the match_ids to retrieve the detailed match info.
for i, row in pro_matches.iterrows():
        if i >3: continue
        match_id = row["match_id"]

        match_data = requests.get(f"https://api.opendota.com/api/matches/{match_id}").json()

        detailed_matches[match_id] = match_data
        time.sleep(1)

with open("output.pkl", "rb") as output_file:

    pickle.dump(detailed_matches, output_file, pickle.HIGHEST_PROTOCOL)

#output = pd.DataFrame(detailed_matches)
#output.to_pickle("output")