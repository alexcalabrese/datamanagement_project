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
import time


class Ilpost(Scraper):
    def __init__(self, skip_backup=False):
        super().__init__()
        self.filename = "3_days_ilpost_parsed_df"
        self.parsed_df = super().load_backup(self.filename, skip=skip_backup)
        self.homepage_html = None

    def scrape(
        self,
        urls=[
            "https://web.archive.org/web/20240109082917/https://www.ilpost.it/italia/",
            "https://web.archive.org/web/20240115232213/https://www.ilpost.it/italia/",
            "https://web.archive.org/web/20240102004317/https://www.ilpost.it/italia/",
        ],
    ):
        """Scrapes articles from a list of URLs.

        Args:
            urls: A list of URLs to scrape articles from.

        Returns:
            A pandas DataFrame containing scraped article data.
        """

        if not self.parsed_df.empty:
            return self.make_df_compatible()

        print(f"Starting scraping...")

        # Call get_homepage_html with the list of urls
        responses = self.get_homepage_html(urls)

        dates = [datetime(2024, 1, 2), datetime(2024, 1, 9), datetime(2024, 1, 15)]

        # List to store parsed articles
        parsed_articles = []

        for idx, response in enumerate(responses):
            if response.status_code == 200:
                print(
                    f"Processing URL: {urls[idx]} (Status Code: {response.status_code})"
                )
                soup = BeautifulSoup(response.content, "html.parser")

                articles = soup.find_all(
                    "article", {"class": "_taxonomy-item_q6jgq_1 _opener_q6jgq_14"}
                )

                date = dates[idx]

                print(f"Found {len(articles)} articles on {urls[idx]}")

            try:
                for article in tqdm(articles):
                    time.sleep(2)

                    title = article.find("h2", {"class": "_article-title_1aaqi_4"}).text
                    link = article.find("a")["href"]

                    if self.parsed_df.empty:
                        parsed_article = Article(title, link, "www.ilpost.it", date)
                        parsed_articles.append(parsed_article)
                    elif link not in self.parsed_df["link"].values:
                        parsed_article = Article(title, link, "www.ilpost.it", date)
                        parsed_articles.append(parsed_article)
                    else:
                        print(f"[SKIP] Article already parsed: {link}")
            except Exception as e:
                print(f"An exception occurred while processing {urls[idx]}: {str(e)}")
            else:
                print(
                    f"Error fetching URL: {urls[idx]} (Status Code: {response.status_code})"
                )

        data = {
            "title": [article.title for article in parsed_articles],
            "link": [article.link for article in parsed_articles],
            "domain": [article.domain for article in parsed_articles],
            "date": [article.date for article in parsed_articles],
            "subtitle": [article.subtitle for article in parsed_articles],
            "content": [article.content for article in parsed_articles],
            "tags": [article.tags for article in parsed_articles],
        }

        self.parsed_df = pd.DataFrame(data)
        return self.make_df_compatible()

    def get_homepage_html(
        self,
        urls=[
            "https://web.archive.org/web/20240102004317/https://www.ilpost.it/italia/",  # 2 Jan
            "https://web.archive.org/web/20240109082917/https://www.ilpost.it/italia/",  # 9 Jan
            "https://web.archive.org/web/20240115232213/https://www.ilpost.it/italia/",  # 15 Jan
        ],
    ):
        """Fetches the homepage HTML for a given list of URLs.

        Args:
            urls: A list of URLs to fetch the homepage HTML for.

        Returns:
            A list of requests.Response objects, where each element corresponds to the response for the respective URL in the input list.
        """

        session = requests.Session()
        retry = Retry(connect=10, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        responses = []
        for url in urls:
            print(f"Fetching URL: {url}")
            response = session.get(url)
            time.sleep(2)

            print(f"Status code: {response.status_code}")
            responses.append(response)
        return responses

    def make_df_compatible(self):
        # substitute the tags array with the first element
        self.parsed_df["tags"] = self.parsed_df["tags"].apply(lambda x: str(x[0]))

        # Create a date object for January 2, 2024
        data = datetime(2024, 1, 2)

        # Add the source site column
        self.parsed_df["source_site"] = self.parsed_df["link"].apply(
            self.extract_source_site
        )

        self.parsed_df.apply(lambda x: data)
        return self.parsed_df

    # Function to extract the source site
    def extract_source_site(
        self,
        link,
        domain_to_site_name={
            "www.open.online": "Open",
            "www.ansa.it": "Ansa",
            "www.ilpost.it": "Ilpost",
        },
    ) -> str:
        """Extracts the source site from the link."""
        for domain, Name in domain_to_site_name.items():
            if domain in link:
                return Name
        return "-1"  # If none of the specified domains are found
