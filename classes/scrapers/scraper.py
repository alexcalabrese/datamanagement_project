# write a basic scraper class that will be inherited by all other scrapers
# this class will have a method to get the html of a page and a method to parse the html
# the parse method will be overwritten by the child classes

import requests
from bs4 import BeautifulSoup
import os
import pandas as pd


class Scraper:
    def __init__(self):
        self.url = None
        self.verbose = True

    def load_backup(self, filename, skip=False):
        if skip:
            return pd.DataFrame()

        try:
            if self.verbose:
                print(f"Loading backup: {filename}")

            # load pickle file in the backups folder
            pickle_file = os.path.join(os.getcwd(), "backups", f"{filename}.pkl")

            if self.verbose:
                print(f"Searching backup in: {pickle_file}")
            if self.verbose:
                print(f"Backup is existing: {os.path.exists(pickle_file)}")

            # pickle_file = os.getcwd() + f"""/{filename}.pkl"""
            if os.path.exists(pickle_file):
                if self.verbose:
                    print(f"Backup found: {filename}")
                open_parsed_df = pd.read_pickle(pickle_file)

                # parsed_articles = open_parsed_df.to_dict('records')

                if self.verbose:
                    print(f"Backup loaded: {filename}")

                return open_parsed_df
            else:
                print(f"Backup not found: {filename}")
                open_parsed_df = pd.DataFrame()
                return open_parsed_df
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
            raise e
