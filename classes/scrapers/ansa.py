from classes.scrapers.article import Article
from classes.scrapers.scraper import Scraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import re
from classes.scrapers.scraper import Scraper
from datetime import datetime


class Ansa(Scraper):
    def __init__(self):
        super().__init__()
        self.filename = 'ansa_parsed_df'
        self.parsed_df = super().load_backup(self.filename)
        self.homepage_html = None
        
    def scrape(self):
        if not self.parsed_df.empty:
            print("Returning parsed df")
            return self.make_df_compatible()
        
        print(f"Starting scraping...")
        
        self.homepage_html = self.get_homepage_html()
        print(f"Homepage status code: {self.homepage_html.status_code}")
        
        parsed_articles = []
        
        soup = BeautifulSoup(self.homepage_html.content, 'html.parser')

        articles = soup.find_all(class_="title")
        
        print(f"Found {len(articles)} articles")

        try:
            for article in tqdm(articles):
                title = article.find('a').text.strip() if article.find('a') else None

                link_element = article.find('a')
                link = link_element['href'] if link_element else None
                link = self.remove_before_http(str(link))

                if title is None or link is None or self.detect_videogallery(link):
                    tqdm.write(f"[SKIP] Article not conformed: {link}")
                    continue

                link = self.remove_before_ansa_link(link)

                tqdm.write(f"Link: {link}")

                if self.parsed_df.empty:
                    parsed_acrticle = Article(title, link, "www.ansa.it")
                    parsed_articles.append(parsed_acrticle)
                elif link not in self.parsed_df['link'].values:
                    parsed_acrticle = Article(title, link, "www.ansa.it")
                    parsed_articles.append(parsed_acrticle)
                else:
                    tqdm.write(f"[SKIP] Article already parsed: {link}")

                time.sleep(1)
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
            
        data = {
            'title': [article.title for article in parsed_articles],
            'link': [article.link for article in parsed_articles],
            'domain': [article.domain for article in parsed_articles],
            'date': [article.date for article in parsed_articles],
            'subtitle': [article.subtitle for article in parsed_articles],
            'content': [article.content for article in parsed_articles],
            'tags': [article.tags for article in parsed_articles]
        }
        
        self.parsed_df = pd.DataFrame(data)
        
        return self.make_df_compatible()
            
    def get_homepage_html(self, url = 'https://web.archive.org/web/20240102000309/https://www.ansa.it/'):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session.get(url)
    
    def remove_before_http(self, s):
        match = re.search(r'https?://', s)
        if match:
            return s[match.start():]
        else:
            return s
        

    def remove_before_ansa_link(self, url):
        pattern = r'(.*)(https://www\.ansa\.it/.*)'
        match = re.search(pattern, url)
        if match:
            return match.group(2)
        else:
            return url

    def detect_videogallery(self, url):
        pattern = r'(https://www\.ansa\.it/sito/videogallery/.*)'
        match = re.search(pattern, url)
        if match:
            return True
        else:
            return False
    
    def make_df_compatible(self):
        # substitute the tags array with the first element
        self.parsed_df['tags'] = self.parsed_df['tags'].apply(lambda x: str(x[0]))
        
        # Add the source site column
        self.parsed_df['source_site'] = self.parsed_df['link'].apply(self.extract_source_site)
                
        # Create a date object for January 2, 2024
        data = datetime(2024, 1, 2)
        
        self.parsed_df.apply(lambda x: data)
        return self.parsed_df

    # Function to extract the source site
    def extract_source_site(self, link, domain_to_site_name={
        'www.open.online': 'Open',
        'www.ansa.it': 'Ansa',
        'www.ilpost.it': 'Ilpost'
    }) -> str:
        """Extracts the source site from the link. """
        for domain, Name in domain_to_site_name.items():
            if domain in link:
                return Name
        return "-1"  # If none of the specified domains are found