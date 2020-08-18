import Odds_Scrape_Methods
import os
import pandas as pd
import pickle

save_place = os.path.join(os.getcwd(), "scrape_sites")



try:
	with open(save_place, "rb") as file:

		done = pickle.load(file)

		print("Loaded")

except:

	done = []


if __name__ == "__main__":


	csv_file = pd.read_excel(os.path.join(os.getcwd(), "dotabuff_matches.xlsx"), index_col = "Tournament Name", header = 0)

	output_data = dict()


	for name, url in csv_file.iterrows():

		if name in done: continue

		print(name)

		output_data[name] = Odds_Scrape_Methods.get_dotabuff_data(url.values[0])

		done.append(name)

		with open(save_place, "wb") as file:

			pickle.dump(done, file)

