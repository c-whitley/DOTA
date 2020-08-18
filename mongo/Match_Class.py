import ast
import numpy as np
import pandas as pd

class Match:

    # Allow the class to access a few global variables
    # which are irrespective of the actual match,
    # this will allow the process of collecting
    # relevant stats to be more efficient.

    def __init__(self, match_data_raw):

        # The raw data for the match
        self.match_data_raw = match_data_raw

        # Processed into a dataframe
        self.match_data = self.eval_match(self.match_data_raw)

        if self.match_data_raw.radiant_win == "t":
            self.Radiant_win = True

        else:
            self.Radiant_win = False

        # Player 1 heros
        self.team_1_heroes = self.match_data[self.match_data["player_slot"] < 5]["hero_id"].values

        # Player 2 heros
        self.team_2_heroes = self.match_data[self.match_data["player_slot"] > 5]["hero_id"].values


    def eval_match(self, match_data):
        # Takes a match as input and computes the relevant bits of information 

        df = pd.DataFrame.from_dict(ast.literal_eval(match_data.pgroup), orient = "index")

        return df


    def hero_vectors(self, heros):
        # Takes a match as input and returns the one-hot hero vector

        max_hero_n = len(heros.reset_index()["id"])

        one_hot_T1 = np.array([1 if i in self.team_1_heroes else 0 for i in range(max_hero_n)], dtype=int)
        one_hot_T2 = np.array([1 if i in self.team_2_heroes else 0 for i in range(max_hero_n)], dtype=int)

        # One hot vector for each team
        self.one_hot_hero_vector = np.vstack((one_hot_T1, one_hot_T2))


    def hero_attribute_vector(self, hero_stats):
        # Takes a match and generates a vector containing the stats for each hero in each team

        team_stats = [hero_stats.loc[team].drop(["roles","attack_type","move_speed","name", "localized_name", "primary_attr", "img", "id", "hero_id", "icon", "cm_enabled"], axis = 1).dropna(axis = 1) for team in [self.team_1_heroes, self.team_2_heroes]]

        # Team stats for each hero
        self.team_hero_stats = np.vstack(team_stats)


    def recent_win_rates(self, recent_matches):
        # Takes a match and outputs the recent win rates with the selected heros

        team_stats = [[recent_matches[hero_n] for hero_n in team] for team in [self.team_1_heroes, self.team_2_heroes]]

        # Recent win rates for heros on each team
        self.recent_win_rates = np.vstack(team_stats)


    def get_match_vector(self):

        # Calculate the output match vector
        self.match_vector = np.concatenate([np.array(stat).reshape(1, -1) for stat in 
        [
            self.one_hot_hero_vector
            #,self.team_hero_stats
            ,self.recent_win_rates
        ]], axis=1)

        return self.match_vector.flatten()