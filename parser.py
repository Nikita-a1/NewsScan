import requests
from bs4 import BeautifulSoup


class Parser:
    urls_from_db = []
    urls_to_download = []

    @staticmethod
    def urls_db_download(host, user, password, database):  # collects all urls from database in urls_from_db to
        # download their text
        pass

    @staticmethod
    def text_downloader(url):  # download content for each url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('title').text
        ###################

        content = soup.findAll('p')
        for i in range(len(content)):
            content[i] = str(content[i].text.strip())
            while '  ' in content[i]:
                content[i] = content[i].replace('  ', ' ')

        content1 = sorted(content, key=len, reverse=True)[:10]

        for el in content:
            if el not in content1:
                content.remove(el)

        text = ''
        for t in content:
            if len(t) > 70:
                text = text + t
