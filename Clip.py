from dataclasses import dataclass

from bs4 import BeautifulSoup
import json
from datetime import datetime
import requests
import re

@dataclass
class Uploader:
    name: str
    link: str

def retrieve_clip_data(url):
    """
    Scrapes clip data from url
    :param url: url of clip
    :return: dictionary of clip data
    """
    request = requests.get(url)
    soup = BeautifulSoup(markup=request.text, features='html.parser')

    script = soup.select_one('script:-soup-contains("VideoObject")')

    if not script:
        return None

    match = re.search(r'(\{.*})', script.text)
    return json.loads(match.group(1))

class Clip:

    def __init__(self, url: str, content_url, title: str, game: str, author: Uploader, time: str):
        self.url = url
        self.content_url = content_url
        self.title = title
        self.game = game
        self.author = author
        self.time = time

    @classmethod
    def from_url(cls, url: str):
        """
        Constructs a Clip object from a url
        :param url: clip url
        :return: clip object if clip is available, else None
        """
        data = retrieve_clip_data(url)

        if data is None:
            return None

        content_url = data['contentUrl']

        title = data['name']
        time = data['datePublished']

        author = data['author']
        uploader = Uploader(name=author['name'], link=author['url'])

        game = data['keywords'].split(',')[0].title()

        return Clip(url=url, content_url=content_url, title=title, game=game, author=uploader, time=time)

    def timestamp(self):
        """
        Converts ISO-8601 datetime to discord timestamp
        :return: timestamp of datetime
        """
        dt_object = datetime.fromisoformat(self.time)
        unix_timestamp = int(dt_object.timestamp())
        return f"<t:{unix_timestamp}:R>"