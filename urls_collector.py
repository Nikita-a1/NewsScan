import yaml
from mysql.connector import connect, Error
import requests
from bs4 import BeautifulSoup
import re

PATH = 'config.yml'  # specify the path for the file

try:  # try to open the yaml file
    with open(PATH, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    print("Can't find the file. Check the path.")

new_urls_list = []  # create a list of URLS to download
download_urls_list = []  # create a list of URLS from the DataBase


class UrlsCollector:
    @staticmethod
    def all_urls():  # collect all links from websites and write them to new_urls_list
        for url in data['webs']:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            def date_checker(link):  # check urls for date
                date_formats = r'\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{8}'
                match = re.search(date_formats, link)
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
    def get_downloaded_urls():  # collect already uploaded urls
        try:
            with connect(
                    host=data['database']['host'],
                    user=data['database']['user'],
                    password=data['database']['password'],
                    database=data['database']['database']
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("select URL from NS_table")
                    result = cursor.fetchall()
                    result = [i[0] for i in result]
                    for el in result:
                        download_urls_list.append(el)
        except Error:
            file = open('log.txt', 'w')
            file.write('s')
            file.close()

    @staticmethod
    def urls_duplicate_check():  # delete duplicates urls
        for item in new_urls_list:
            if item in download_urls_list:
                new_urls_list.remove(item)

    @staticmethod
    def urls_record(new_url):  # record unique links in the database and set status 'not_downloaded'
        try:
            with connect(
                    host="localhost",
                    user="NewsScan",
                    password="Sql_9909",
                    database="NS_db"
            ) as connection:
                new_url = str(new_url)
                with connection.cursor() as cursor:
                    request = "insert into NS_table (URL, Status) values ('{}', 'not_downloaded')".format(new_url)
                    cursor.execute(request)
                    print(request)
        except Error as e:
            print(e)
