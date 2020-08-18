from multiprocessing import Pool
from pymongo import MongoClient
from tqdm import tqdm
import itertools

def get_win_rate(n):

    """


    """

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dota']

    t = db.matches.count_documents({"$and": [{"radiant_win": "t"},
     {"$or":[{"pgroup.{}.hero_id".format(i): n} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    if t == 0:
        return

    f = db.matches.count_documents({"$and": [{"radiant_win": "f"},
     {"$or":[{"pgroup.{}.hero_id".format(i): n} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    return {"Hero_id":n
           ,"Win_rate": t/(t+f)}


def get_pair_win_rate(input):

    """


    """

    assert len(input) == 2, "Invalid"

    h1, h2 = input

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dota']


    t = db.matches.count_documents({"$and": [{"radiant_win": "t"},
                                             {"$or":[{"pgroup.{}.hero_id".format(i): int(h1)} for i in [0,1,2,3,4,128,129,130,131,132]]},
                                             {"$or":[{"pgroup.{}.hero_id".format(i): int(h2)} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    #print(t)

    if t == 0:
        return

    f = db.matches.count_documents({"$and": [{"radiant_win": "f"},
                                             {"$or":[{"pgroup.{}.hero_id".format(i): int(h1)} for i in [0,1,2,3,4,128,129,130,131,132]]},
                                             {"$or":[{"pgroup.{}.hero_id".format(i): int(h2)} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    return {"Hero_1": h1
           ,"Hero_2": h2
           ,"Win_rate": t/(t+f)}


def get_pair_win_rate_new(input):

    """


    """

    assert len(input) == 2, "Invalid"

    h1, h2 = input

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dota']


    t = db.matches_pgroup_format.count_documents({"$and": [{"radiant_win": "t"},
                                             {"$or":[{"hero_id{}".format(i): int(h1)} for i in [0,1,2,3,4,128,129,130,131,132]]},
                                             {"$or":[{"hero_id{}".format(i): int(h2)} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    #print(t)

    if t == 0:
        return

    f = db.matches_pgroup_format.count_documents({"$and": [{"radiant_win": "f"},
                                             {"$or":[{"hero_id{}".format(i): int(h1)} for i in [0,1,2,3,4,128,129,130,131,132]]},
                                             {"$or":[{"hero_id{}".format(i): int(h2)} for i in [0,1,2,3,4,128,129,130,131,132]]}]})

    return {"Hero_1": h1
           ,"Hero_2": h2
           ,"Win_rate": t/(t+f)}



class Stats_Update:

    """
    A class to store all methods needed to update relevant dota stats

    """
    def __init__(self):

        pass

    def get_stats(self, heroes):

        with Pool(4) as p:

            r = tqdm(p.starmap(get_pair_win_rate, itertools.combinations(heroes, r = 2)))

