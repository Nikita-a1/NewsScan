import requests
from bs4 import BeautifulSoup
from mysql.connector import connect


class Parser:
    urls_from_db = []
    urls_to_download = []

    @staticmethod
    def urls_db_download(host, user, password, database):  # collects all urls from database in urls_from_db to
        # download their text
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            request = "select URL from NS_table where Status = 'Not_downloaded'"
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                connection.commit()
                result = [''.join(url) for url in result]
                for url in result:
                    Parser.urls_from_db.append(url)

    @staticmethod
    def text_downloader(host, user, password, database, url):  # download content for each url
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

        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            request = "update NS_table set Title = '{}', Content = '{}', Status = 'downloaded' where URl = '{}';".format(
                title, text, url)
            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()
