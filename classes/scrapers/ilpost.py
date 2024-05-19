from classes.scrapers.article import Article
from classes.scrapers.scraper import Scraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
from classes.scrapers.scraper import Scraper
from datetime import datetime


class Ilpost(Scraper):
    def __init__(self):
        super().__init__()
        self.filename = 'ilpost_parsed_df'
        self.parsed_df = super().load_backup(self.filename)
        self.homepage_html = None
                
    def scrape(self):
        if not self.parsed_df.empty:
            return self.make_df_compatible()
        
        print(f"Starting scraping...")
        
        self.homepage_html = self.get_homepage_html()
        
        print(f"Homepage status code: {self.homepage_html.status_code}")
        
        parsed_articles = []
        
        soup = BeautifulSoup(self.homepage_html.content, 'html.parser')

        articles = soup.find_all('article', {'class': '_taxonomy-item_q6jgq_1 _opener_q6jgq_14'})
        
        print(f"Found {len(articles)} articles")

        try:
            for article in tqdm(articles):
                
                title = article.find('h2', {'class': '_article-title_1aaqi_4'}).text
                link = article.find('a')['href']

                if self.parsed_df.empty:
                    parsed_acrticle = Article(title, link, "www.ilpost.it")
                    parsed_articles.append(parsed_acrticle)
                elif link not in self.parsed_df['link'].values:
                    parsed_acrticle = Article(title, link, "www.ilpost.it")
                    parsed_articles.append(parsed_acrticle)
                else:
                    print(f"[SKIP] Article already parsed: {link}")
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
            
    def get_homepage_html(self, url = 'https://web.archive.org/web/20240102004317/https://www.ilpost.it/italia/'):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # self.homepage_html = session.get(url)
        return session.get(url)
        
        
    def make_df_compatible(self):
        # substitute the tags array with the first element
        self.parsed_df['tags'] = self.parsed_df['tags'].apply(lambda x: str(x[0]))
        
        # Create a date object for January 2, 2024
        data = datetime(2024, 1, 2)
        
        # Add the source site column
        self.parsed_df['source_site'] = self.parsed_df['link'].apply(self.extract_source_site)
        
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
        