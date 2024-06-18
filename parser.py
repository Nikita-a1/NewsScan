import requests
from bs4 import BeautifulSoup


class Parser:

    urls_from_db = []
    urls_to_download = []
    contents = []

    @staticmethod
    def urls_db_download():  # collects all urls from database
        pass

    @staticmethod
    def text_downloader():  # download content for each url
        for url in Parser.urls_from_db:
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

            Parser.contents.append(text)
