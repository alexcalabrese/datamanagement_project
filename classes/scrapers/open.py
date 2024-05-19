from classes.scrapers.scraper import Scraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import re
from classes.scrapers.scraper import Scraper
from datetime import datetime


class Open(Scraper):
    def __init__(self):
        super().__init__()
        self.filename = 'open_parsed_df'
        self.parsed_df = super().load_backup(self.filename)
        
    def scrape(self, url = "https://web.archive.org/web/20240102003612/https://www.open.online/"):
        if not self.parsed_df.empty:
            return self.make_df_compatible()
        
        parsed_articles = []
        
        # Scraping the homepage
        news_data = self.scrape_news(url)
        
        try:
            for news in tqdm(news_data, desc="Parsing articles"):
                if self.parsed_df.empty:
                    # Cache df is empty
                    article_data = self.parse_article(self.remove_before_http(news['link']))
                    if article_data:
                        article_data['site'] = 'www.open.online'
                        parsed_articles.append(article_data)
                elif self.remove_before_http(news['link']) not in self.parsed_df['link'].values:
                    # Not in cache
                    article_data = self.parse_article(self.remove_before_http(news['link']))
                    if article_data:
                        article_data['site'] = 'www.open.online'
                        parsed_articles.append(article_data)
                else:
                    print(f"[SKIP] Article already parsed: {self.remove_before_http(news['link'])}")
                
            return parsed_articles
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
        
    def scrape_news(self, url: str) -> List[Dict[str, Optional[str]]]:
        """
        Scrape news data from a given website.

        Parameters:
        url (str): The URL of the website to scrape.

        Returns:
        List[Dict[str, Optional[str]]]: A list of dictionaries containing the scraped news data.
        """
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        news_inner_list = soup.find_all(class_="news__inner")
        news_data = []

        for news_inner in news_inner_list:
            title_element = news_inner.find(class_="news__title")
            title = title_element.text.strip() if title_element else None

            date_element = news_inner.find(class_="news__date-day")
            date = date_element.text.strip() if date_element else None

            author_element = news_inner.find(class_="news__author")
            author = author_element.text.strip() if author_element else None

            link_element = news_inner.find(class_="news__title").find('a')
            link = link_element['href'] if link_element else None

            news_data.append({'title': title, 'date': date, 'author': author, 'link': link})

        return news_data

    def parse_article(self, link: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Parse an article from a given link.

        Parameters:
        link (str): The URL of the article to parse.

        Returns:
        Optional[Dict[str, Optional[str]]]: A dictionary containing the parsed article data, or None if the request was unsuccessful.
        """
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(link)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        title_element = soup.find(class_="news__title")
        title = title_element.text.strip() if title_element else None

        date_element = soup.find(class_="news__date-day")
        date = date_element.text.strip() if date_element else None

        author_element = soup.find(class_="news__author")
        author = author_element.text.strip() if author_element else None

        content_element = soup.find(class_="news__content")
        content = content_element.text.strip() if content_element else None

        a_tag = soup.find('a', rel='category tag')
        tag = a_tag.text if a_tag else None

        article_data = {
            'title': title,
            'date': date,
            'author': author,
            'content': content,
            'tag': tag,
            'link': link
        }

        return article_data

    def remove_before_http(self, s):
        match = re.search(r'https?://', s)
        if match:
            return s[match.start():]
        else:
            return s
        
    def make_df_compatible(self):
        # substitute the tags array with the first element
        self.parsed_df.rename(columns={'tag': 'tags'}, inplace=True)
        
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