import numpy as np 
import pandas as pd
from dateutil.parser import parse
import requests, time, re, os, random
import datetime
from tqdm import tqdm
import pickle

from selenium import webdriver

def sort_date_list_oddsportal(date_list):

    dates = []

    for el in date_list:

        if len(el) > 12:
            current = el

        if len(el) == 12:

            date = datetime.datetime.strptime(remove_suffix(current), '%a %B %d, %Y')
            dates.append(date)

    return dates


def get_dotabuff_matches(matchdriver, site):

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

        # Retrieve and scrape ID number
        id_ = re.findall("\d{9}", match.get_attribute("href"))[0]
        match_dict["Match_ID"] = int(id_)

        output.append(match_dict)
    
    times = [time.text for time in matchdriver.find_elements_by_tag_name("time")]
    output_df = pd.DataFrame(output)

    output_df["Dates"] = sort_date_list_oddsportal(times)

    #X["DT_N"] = X.apply(lambda row: datetime.datetime.strptime(row["DT"], '%d %b %Y %H:%M'), axis=1)

    output_df["Start time"] = output_df.apply(lambda row: open_dota_time(row), axis = 1)

    return output_df


def dt_dotabuff(row):

    output = parse(row["Dates"])

    print(output)

    return None


def get_oddsportal_data(matchdriver, site):
    
    matchdriver.get(site)

    dates = []

    for n in range(len(matchdriver.find_elements_by_xpath("//table[@id='tournamentTable']/tbody/tr")) + 1):

        try: 
            date = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]".format(n)).text.split(" - ")[0]
            if len(date) >=1:
                dates.append(date)
            
        except:
            
            pass

    output_list = []
    current_date = []

    datelist = [re.findall("\d{1,2}\s\w{3}\s\d{4}", row) for row in dates]

    for date in datelist:
        
        # Set the current date to the most recent round
        try: 

            current = date[0]

            continue

        except:

            try: 
                output_list.append(current)

            except: continue

    output_list = np.array(output_list).flatten()[:]

    table = []

    # For every row in the page (apart from first)
    for n in range(len(matchdriver.find_elements_by_xpath("//table[@id='tournamentTable']/tbody/tr"))+1):

        row = dict()

        try: 

            row["Time"] = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]/td[1]".format(n)).text

            teams = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]/td[2]".format(n)).text
            row["Team_1"], row["Team_2"] = teams.split(" - ")
            row["Score"] = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]/td[3]".format(n)).text
            row["team_1_odds"] = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]/td[4]".format(n)).text
            row["team_2_odds"] = matchdriver.find_element_by_xpath("//table[@id='tournamentTable']/tbody/tr[{}]/td[5]".format(n)).text
            table.append(row)

        except: pass

    output = pd.DataFrame(table)

    output["Date"] = output_list
    output["DT"] = output["Date"] + " " + output["Time"]
    output["DT_N"] = output.apply(lambda row: datetime.datetime.strptime(row["DT"], '%d %b %Y %H:%M'), axis=1)

    # Add an hour to be UTC?
    output["date"] = output["DT_N"] + datetime.timedelta(hours=1)

    # Catch rows with no odds offered
    offered_odds = (output.team_1_odds != "-") & (output.team_2_odds != "-")
    output = output[offered_odds.values]

    #print(output)

    # Convert rows to probabilities
    probs = output.apply(lambda row: prob_convert(row), axis=1).values

    output["Prob_1"], output["Prob_2"] = list(zip(*probs))

    output.drop(["Date", "Time", "DT", "DT_N"], axis=1, inplace=True)
    
    output["T1_win"] = output.apply(lambda row: np.argmin(row["Score"].split(":")), axis=1)

    return output


def open_dota_time(row):

    time.sleep(1)
    request_ = requests.get("https://api.opendota.com/api/matches/{}".format(row["Match_ID"])).json()

    try:  
          
        start_time = pd.DataFrame(request_)["start_time"][0]

        return start_time

    except: pass


def prob_convert(row):

    return_list = []

    for n_team in [1,2]:

        num, denom = [int(n) for n in row["team_{}_odds".format(n_team)].split("/")]

        return_list.append((denom/(num + denom)))

    return_list = [n/sum(return_list) for n in return_list]

    return return_list


def liquid_dota(matchdriver, site):

    matchdriver.get(site)

    match_data = []

    matches = matchdriver.find_elements_by_class_name("bracket-game")

    for match in matches:

        match_dict = dict()

        # Find the icon to click
        try:
            icon = match.find_element_by_class_name('icon')
            icon.click()

        except:
            continue

        date = match.find_element_by_class_name('timer-object-date').text

        try: match_dict["date"] = datetime.datetime.strptime(date, '%B %d, %Y - %H:%M BST')
        except: match_dict["date"] = datetime.datetime.strptime(date, '%B %d, %Y - %H:%M GMT')

        # Team names
        match_dict["radiant"] = match.find_element_by_class_name("bracket-popup-header-left").find_element_by_class_name("team-template-text").text
        match_dict["dire"] = match.find_element_by_class_name("bracket-popup-header-right").find_element_by_class_name("team-template-text").text

        round_list = []
        
        for round_ in match.find_elements_by_class_name("match-row"):

            round_dict = dict()

            try: 
                round_.find_element_by_class_name("left").find_element_by_class_name("check")
                round_dict["Radiant_win"] = True

            except: round_dict["Radiant_win"] = False

            radiant_draft = round_.find_element_by_class_name("draft.radiant")
            radiant_heroes = radiant_draft.find_elements_by_tag_name("a")
            round_dict["radiant_hero_names"] = [hero.get_attribute("title") for hero in radiant_heroes]

            dire_draft = round_.find_element_by_class_name("draft.dire")
            dire_heroes = dire_draft.find_elements_by_tag_name("a")
            round_dict["dire_hero_names"] = [hero.get_attribute("title") for hero in dire_heroes]

            round_list.append(round_dict)
        match_dict["Rounds"] = round_list
        match_data.append(match_dict)
        icon.click()

    return pd.DataFrame(match_data)


def liquid_dota_group(matchdriver, site):

    matchdriver.get(site)

    try:
        show_button = matchdriver.find_element_by_class_name("toggle-group.toggle-state-show")
        show_button.find_element_by_tag_name("button").click()

    except: pass

    match_data = []

    matches = matchdriver.find_elements_by_class_name("match-row")

    for match in matches:

        match_dict = dict()

        # Find the icon to click
        try:

            icon = match.find_element_by_class_name('match-row-icon')
            icon.click()

        except:
            continue

        date = match.find_element_by_class_name('timer-object-date').text
        try: match_dict["date"] = datetime.datetime.strptime(date, '%B %d, %Y - %H:%M BST')
        except: match_dict["date"] = datetime.datetime.strptime(date, '%B %d, %Y - %H:%M GMT')

        # Team names
        # TODO: 
        # Change "radiant" and "dire" to do team 1 and 2, avoiding confusion. 

        for tn, side in zip(["radiant","dire"], ["left","right"]):

            name = match.find_element_by_class_name("bracket-popup-header-{}".format(side)).find_element_by_class_name("team-template-text").find_element_by_tag_name("a").get_attribute("title")

            match_dict[f"{tn}"] = name
        #match_dict["dire"] = match.find_element_by_class_name("bracket-popup-header-right").find_element_by_class_name("team-template-text").text

        round_list = []
        
        for round_ in match.find_elements_by_class_name("match-row"):

            round_dict = dict()

            try: 
                round_.find_element_by_class_name("left").find_element_by_class_name("check")
                round_dict["Radiant_win"] = True

            except: round_dict["Radiant_win"] = False

            radiant_draft = round_.find_element_by_class_name("draft.radiant")
            radiant_heroes = radiant_draft.find_elements_by_tag_name("a")
            round_dict["radiant_hero_names"] = [hero.get_attribute("title") for hero in radiant_heroes]

            dire_draft = round_.find_element_by_class_name("draft.dire")
            dire_heroes = dire_draft.find_elements_by_tag_name("a")
            round_dict["dire_hero_names"] = [hero.get_attribute("title") for hero in dire_heroes]

            round_list.append(round_dict)
        match_dict["Rounds"] = round_list
        match_data.append(match_dict)
        icon.click()

    return pd.DataFrame(match_data)


def dota_buff_page(site, gecko_path = r"B:\Git_Projects\dota_project\geckodriver.exe"):

    """
    try:
        matchdriver = webdriver.Firefox(executable_path = gecko_path)
        matchdriver.get(site)

    except:
        print("Proxy")
        proxies = get_proxy_list()
        proxy = random.choice(proxies)
        matchdriver = my_proxy(proxy[0], proxy[1])
        matchdriver.get(site)
    """

    matchdriver = webdriver.Firefox(executable_path = os.path.join(os.getcwd(), "geckodriver"))
    matchdriver.get(site)
    
    match_dict = dict()

    for side in ["radiant", "dire"]:

        # Try and get element from page in infinite loop, if it passes: break out of loop
        # otherwise wait for random few seconds and try again.

        while True:

            matchdriver.get(site)


            try:

                matchdriver.find_element_by_id("status").text == "Too Many Requests"

                print("Too many requests")

                duration = np.random.randint(100,600)

                print("Waiting for {} minutes".format(duration/60))

                time.sleep(duration)

            except:

                break

        side_ = matchdriver.find_element_by_class_name(side)


        match_dict["{}_name".format(side)] = side_.find_element_by_class_name("team-text.team-text-full").text
        player_n = 1

        for player in side_.find_elements_by_xpath("//section[@class='{}'][1]/article/table/tbody/tr".format(side)):

            player_id = player.get_attribute("class").split("player-")[1]

            # For some reason it picks up the other rows which don't contain player info.
            # If it fails: finishing scraping that page

            try:
                    hero = player.find_element_by_class_name("image-hero.image-icon.image-overlay")

            except:
                    break

            hero_name = hero.get_attribute("oldtitle")

            match_dict["{}_player_{}".format(side, player_n)] = (player_id, hero_name)
            player_n += 1

    matchdriver.close()

    return match_dict


def get_dotabuff_data(parent, save_place = r"B:\Git_Projects\dota_project\scrape_saves"):

    if not os.path.exists(os.path.join(os.getcwd(), "scrape_saves")): 

        os.mkdir(os.path.join(os.getcwd(), "scrape_saves"))

    try:

        with open(os.path.join(os.getcwd(), "scrape_saves", "scrape_saves.pickle"), "rb") as file:

            completed, matchlist = pickle.load(file)

    except:
        completed = []
        matchlist = []

    gecko_path = r"B:\Git_Projects\dota_project\geckodriver.exe"
    gecko_path = os.path.join(os.getcwd(), "geckodriver")
    matchdriver = webdriver.Firefox(executable_path = gecko_path)
    matchdriver.get(parent)

    match_links = []
    dates = []


    while True:

        for match in matchdriver.find_elements_by_class_name("match-score"):

            match_links.append(match.get_attribute("href"))

        for match in matchdriver.find_elements_by_class_name("match-score"):

            dates.append(match.find_element_by_tag_name("time").get_attribute("title"))

        try:
            print("Trying next page")
            
            try: 
                matchdriver.find_element_by_class_name("banner_save--3Xnwp").click()
                time.sleep(0.5) # Wait for barrier to disappear
            except:
                pass

            matchdriver.find_element_by_class_name("next").click()
            print("Next page")

        except:


            break

    matchdriver.close()

    #match_links = [match.get_attribute("href") for match in matchdriver.find_elements_by_class_name("match-score")]
    #dates = [match.find_element_by_tag_name("time").get_attribute("title") for match in matchdriver.find_elements_by_class_name("match-score")]

    for i, link, date in zip(tqdm(range(len(match_links))), match_links, dates):

        if link in completed: continue

        try: 
            match_dict = dota_buff_page(link, gecko_path)

        except: continue

        #time.sleep(random.randint(1,10))
        date = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date.lower())
        match_dict["Date"] = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')

        matchlist.append(match_dict)

        with open(os.path.join(os.getcwd(), "scrape_saves", "scrape_saves.pickle"), "wb") as file:

            completed.append(link)
            pickle.dump((completed, matchlist), file)

    return matchlist


def get_dotabuff_data2(parent):
    
    matchlist = []

    proxies = get_proxy_list()

    proxy = random.choice(proxies)
    matchdriver = my_proxy(proxy[0], proxy[1])
    matchdriver.get(parent)

    while True:

        match_links = [match.get_attribute("href") for match in matchdriver.find_elements_by_class_name("match-score")]
        dates = [match.find_element_by_tag_name("time").get_attribute("title") for match in matchdriver.find_elements_by_class_name("match-score")]

        for i, link, date in zip(tqdm(range(len(match_links))), match_links, dates):
    
            match_dict = dict()

            time.sleep(0.5)
            date = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date.lower())
            match_dict["Date"] = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')

            matchdriver.get(link)

            while True:

                try:

                    for side in ["radiant", "dire"]:
                        
                        # Try and get element from page in infinite loop, if it passes: break out of loop
                        # otherwise wait for random few seconds and try again.

                        side_ = matchdriver.find_element_by_class_name(side)

                        match_dict["{}_name".format(side)] = side_.find_element_by_class_name("team-text.team-text-full").text
                        player_n = 1

                        for player in side_.find_elements_by_xpath("//section[@class='{}'][1]/article/table/tbody/tr".format(side)):

                            player_id = player.get_attribute("class").split("player-")[1]

                            # For some reason it picks up the other rows which don't contain player info.
                            # If it fails: finishing scraping that page

                            try:
                                 hero = player.find_element_by_class_name("image-hero.image-icon.image-overlay")

                            except:
                                 break
                            hero_name = hero.get_attribute("oldtitle")

                            match_dict["{}_player_{}".format(side, player_n)] = (player_id, hero_name)
                            player_n += 1

                    break

                except:

                    print("New")
                    
                    time.sleep(np.random.randint(3,10,1))
                    matchdriver.close()
                    time.sleep(1)

                    proxy = random.choice(proxies)
                    matchdriver = my_proxy(proxy[0], proxy[1])
                    #time.sleep(np.random.randint(3,10,1))
                    matchdriver.get(link)

            # Add the current match to the 
            matchlist.append(match_dict)

            if (i % 10 == 0) & (i != 0):

                #return matchlist
                #print("Skip")
                time.sleep(np.random.randint(10,15,1))

            time.sleep(np.random.randint(55,105,1))

        # Go back to current page on tournament
        matchdriver.get(site)

        try:
            # Try and click away the barrier
            matchdriver.find_element_by_class_name("banner_save--3Xnwp").click()
            time.sleep(0.5) # Wait for barrier to disappear

        except:

            matchdriver.find_element_by_class_name("next").click()
            site = matchdriver.current_url
            print(site)

        try:
            matchdriver.find_element_by_class_name("next").click()
            print("Next page")

        except: return matchlist


def get_proxy_list():

    #gecko_path = r"B:\Git_Projects\dota_project\geckodriver.exe"
    gecko_path = os.path.join(os.getcwd(), "geckodriver")

    driver = webdriver.Firefox(executable_path = gecko_path)
    driver.get(r"http://spys.one/en/")

    proxies = []

    for result in driver.find_elements_by_class_name(r"spy14"):

        proxy = re.search("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{3,5}", result.text)

        if proxy != None:

            ip, port = proxy.string.split(":")

            proxies.append((ip, port))

    return proxies


def my_proxy(PROXY_HOST,PROXY_PORT):

        fp = webdriver.FirefoxProfile()
        # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
        fp.set_preference("network.proxy.type", 1)
        fp.set_preference("network.proxy.http",PROXY_HOST)
        fp.set_preference("network.proxy.http_port",int(PROXY_PORT))
        fp.set_preference("general.useragent.override","whater_useragent")
        fp.set_preference('network.proxy.ftp_port', int(PROXY_PORT))
        fp.set_preference('network.proxy.ssl', PROXY_HOST)
        fp.set_preference('network.proxy.ssl_port', int(PROXY_PORT))
        fp.set_preference('network.proxy.no_proxies_on', 'localhost, 192.168.0.1') 

        fp.update_preferences()

        return webdriver.Firefox(firefox_profile=fp, executable_path = r"B:\Git_Projects\dota_project\geckodriver.exe")

from selenium.webdriver.common.proxy import Proxy, ProxyType

def my_proxy2(PROXY_HOST,PROXY_PORT):

    PROXY_HOST, PROXY_PORT = PROXY_HOST, int(PROXY_PORT)

    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = "{}:{}".format(PROXY_HOST, PROXY_PORT)
    prox.socks_proxy = "{}:{}".format(PROXY_HOST, PROXY_PORT)
    prox.ssl_proxy = "{}:{}".format(PROXY_HOST, PROXY_PORT)

    capabilities = webdriver.DesiredCapabilities.FIREFOX
    prox.add_to_capabilities(capabilities)

    return webdriver.Firefox(desired_capabilities=capabilities)