import numpy as np
import pandas as pd
import selenium

def sort_date_list(date_list):
    
    dates = []

    for el in date_list:

        if len(el) > 12:
            current = el

        if len(el) == 12:

            dates.append(current)

    return dates

def get_dotabuff_matches(site):
    
    matchdriver.get(site)

    matches = matchdriver.find_elements_by_class_name("match-score")
    output = []
    
    for match in matches:

        match_dict = dict()

        try:
            # Dire team is the winner
            radiant = match.find_element_by_class_name("radiant")
            match_dict["radiant"] = radiant.find_elements_by_class_name("esports-team")[1].text

            dire = match.find_element_by_class_name("dire.team-winner")
            match_dict["dire"] = dire.find_elements_by_class_name("team-text.team-text-full")[0].text
            match_dict["radiant_win"] = False

        except: 
            # Radiant team is the winner
            radiant = match.find_element_by_class_name("radiant.team-winner")
            match_dict["radiant"] = radiant.find_elements_by_class_name("esports-team")[1].text
            match_dict["radiant_win"] = True

            dire = match.find_element_by_class_name("dire")
            match_dict["dire"] = dire.find_elements_by_class_name("team-text.team-text-full")[0].text

        hero_list = [ele.get_attribute("title") for ele in match.find_elements_by_class_name("image-hero.image-tinyicon")]

        match_dict["radiant_heroes"], match_dict["dire_heroes"] = hero_list[:5], hero_list[5:]

        output.append(match_dict)
        
    times = [time.text for time in matchdriver.find_elements_by_tag_name("time")]
    output_df = pd.DataFrame(output)
    output_df["Dates"] = sort_date_list(times)
        
    return output_df