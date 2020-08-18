from functools import partial
from multiprocessing import Pool
import pandas as pd
import numpy as np
from pymongo import MongoClient
import os
import tqdm
import requests
import time
import itertools
import datetime

import query_methods

heroes = pd.DataFrame(requests.get(f"https://api.opendota.com/api/heroes").json())

if __name__ == '__main__':

    list_ = heroes["id"].values#[:3]
    list_ = list(itertools.combinations(list_, r = 2))

    with Pool(4) as p:

        r = list(tqdm.tqdm(p.imap(query_methods.get_pair_win_rate_new, list_), total  = len(list_)))

    date_string = datetime.datetime.isoformat(datetime.datetime.now())[:-10]

    path = os.path.join(os.getcwd(), date_string)

    pd.DataFrame(r).to_pickle(path)

    print("Saved at: ", path)

