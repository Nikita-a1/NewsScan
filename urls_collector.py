from mysql.connector import connect
import requests
from bs4 import BeautifulSoup
import re

PATH = 'config.yml'  # specify the path for the file

new_urls_list = []  # create a list of URLS to download
download_urls_list = []  # create a list of URLS from the DataBase


class UrlsCollector:

    @staticmethod
    def all_urls(url):  # collect all links from websites and write them to new_urls_list
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        def date_checker(ob):  # check links for date
            date_formats = r'\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{8}'
            match = re.search(date_formats, ob)
            return bool(match)

        all_a = soup.findAll('a')
        for a in all_a:
            link = a.get('href')
            link = str(link)

            if (url in link and len(link) > 45) or (
                    url not in link and len(link) > 35):  # check links and edit them
                if '/app/' not in link and 'org' not in link:
                    if date_checker(link) or '/news/' in link or len(link) > 60 and link.count('-') >= 5:
                        if link[0:4] != 'http':
                            link = url + link
                        new_urls_list.append(link)

    @staticmethod
    def get_downloaded_urls(host, user, password, database):  # collect already uploaded urls
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select URL from NS_table")
                result = cursor.fetchall()
                result = [i[0] for i in result]
                for el in result:
                    download_urls_list.append(el)

    @staticmethod
    def urls_duplicate_check():  # delete duplicates urls
        for item in new_urls_list:
            if item in download_urls_list:
                new_urls_list.remove(item)

    @staticmethod
    def urls_record(host, user, password, database,
                    new_url):  # record unique links in the database and set status 'not_downloaded'
        with connect(
                host=host,
                user=user,
                password=password,
                database=database
        ) as connection:
            new_url = str(new_url)
            with connection.cursor() as cursor:
                request = "insert into NS_table (URL, Status) values ('{}', 'not_downloaded')".format(new_url)
                cursor.execute(request)
