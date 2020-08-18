import itertools
import requests

import numpy as np
import pandas as pd

heroes = pd.DataFrame(requests.get(f"https://api.opendota.com/api/heroes").json())
synergy = pd.read_pickle("/mnt/b/Git_Projects/DOTA2Project/Stats_Data/synergy.pickle")



def adversity_scores(row):

    output = dict()
    i = 0

    for h1 in row.Radiant_heros:
        for h2 in row.Dire_heros:
            
            # Get the actual hero number from the heros DF
            h1, h2 = dict(heroes.id)[h1], dict(heroes.id)[h2]
            
            i+=1

            # Get the score for how h1 played against h2 on average
            try:
                
                output[f"p{i}"] = adversity.loc[(h1, h2)].values[0]

            except:
                output[f"p{i}"] = adversity.loc[(h1, h2)[::-1]].values[0]
            
    return output


def hero_one_hot(row):

    one_hot_vec = {f"T{ti}-H{hi}": 1 if hi in team else 0 for hi in range(1,len(heroes.id)+1) 
    for ti, team in enumerate([row.Radiant_heros, row.Dire_heros])}

    #for ti, team in enumerate([row.Radiant_heros, row.Dire_heros]):
    #    for hi in range(1,len(heroes.id)+1):

    return one_hot_vec


def synergy_scores(row):
    
    output = dict()

    for ti, team in enumerate([row.Radiant_heros, row.Dire_heros], start = 1):
        
        team_stats = []
        
        for pi, pair in enumerate(itertools.combinations(team, r = 2), start = 1):

            h1, h2 = dict(heroes.id)[pair[0]], dict(heroes.id)[pair[1]]

            try:
                output[f"t{ti}-p{pi}"] = synergy.loc[(h1, h2)].values[0]
                
            except:
                output[f"t{ti}-p{pi}"] = synergy.loc[(h1, h2)[::-1]].values[0]
                
    return output


def synergy_win_rates(row):
    
    sum_stats = {"Mean": np.mean
            ,"Std": np.std
            ,"Kurt": stats.kurtosis}
    
    output = dict()

    for ti, team in enumerate([row.Radiant_heros, row.Dire_heros], start = 1):
        
        team_stats = []
        
        for pi, pair in enumerate(itertools.combinations(team, r = 2), start = 1):

            h1, h2 = dict(heroes.id)[pair[0]], dict(heroes.id)[pair[1]]

            try:
                team_stats.append(synergy.loc[(h1, h2)].values)

            except:
                team_stats.append(synergy.loc[(h1, h2)[::-1]].values)
                
        for name, func in sum_stats.items():
            
            try:
                output[f"T{ti}-{name}"] = func(team_stats)[0]
            except:
                output[f"T{ti}-{name}"] = func(team_stats)


    return output


def row_process(row):
    
    out = {**synergy_win_rates(row),
            **adversity_scores(row),
            **hero_one_hot(row),
            **{"Radiant_win": row.radiant_win,
                "match_id": row.match_id}}
    
    return out