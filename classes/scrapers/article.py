# perform a GET http request to this website https://web.archive.org/web/20240102004317/https://www.ilpost.it/italia/
import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd

class Article:
    def __init__(self, title, link, domain):
        self.title = title
        self.link = link
        self.domain = domain
        self.date = None

        # Content
        self.title = None
        self.subtitle = None
        self.content = None
        self.tags = []

        self.session = None

        self.setup_session()

        self.extract_date()
        self.extract_content()

    def setup_session(self, connect=3, backoff_factor=0.5):
        self.session = requests.Session()
        retry = Retry(connect=connect, backoff_factor=backoff_factor)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def extract_content(self):
        if self.domain == "www.ilpost.it":
            response = self.session.get(self.link)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('h1').text
            self.title = title

            # Extract subtitle
            subtitle = soup.find('h2').text
            self.subtitle = subtitle

            # Extract article content
            article_content = soup.find('div', {'id': 'singleBody'}).get_text(strip=True)
            self.content = article_content

            # Extract tags
            tags_div = soup.find('div', {'class': 'index_art_tag__pP6B_'})
            tags = [a.text for a in tags_div.find_all('a')]
            self.tags = tags

            print(f"- Title: {self.title}\nLink: {self.link}\nDomain: {self.domain}\nDate: {self.date}\nSubtitle: {self.subtitle}\nContent: {self.content}\nTags: {self.tags}")

            time.sleep(1)
        if self.domain == "www.ansa.it":
            response = self.session.get(self.link)

            soup = BeautifulSoup(response.content, "html.parser")
            title_element = soup.find(class_="post-single-title")
            title = title_element.text.strip() if title_element else None
            self.title = title

            date_element = soup.find(class_="details")
            date = date_element.text.strip() if date_element else None
            self.date = date

            author_element = soup.find(class_="author")
            author = author_element.text.strip() if author_element else None
            self.author = author

            content_element = soup.find(class_="post-single-text rich-text news-txt")
            content = content_element.text.strip() if content_element else None
            self.content = content

            a_tag = soup.find( class_='is-section')
            tag = a_tag.text.replace('\n', '').strip() if a_tag else None
            print(tag)
            self.tags = tag

    def extract_date(self):
        if self.domain != "www.ansa.it":
        # extract date from the link: https://web.archive.org/web/20240102004317/https://www.ilpost.it/2024/01/01/fine-reddito-di-cittadinanza/
            date = self.link.split('/')[4]
            self.date = date

    def __str__(self):
        return f"Title: {self.title}\nLink: {self.link}\nDomain: {self.domain}\nDate: {self.date}\nSubtitle: {self.subtitle}\nContent: {self.content}\nTags: {self.tags}"