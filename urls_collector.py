from mysql.connector import connect
import requests
from bs4 import BeautifulSoup
import re


class UrlsCollector:

    @staticmethod
    def all_urls(url, new_links):  # collect all links from websites and write them to new_links
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url)
        response.encoding = 'utf-8'

        if response != '<Response [200]>':
            response = requests.get(url, proxies={'http': None, 'https': None})
            response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')
        forbidden_words = ['app', 'org', '.com', '.rss', '/group', '/story', 'channel/', '/rutube']
        web = '/'.join(url.split('/')[:3])

        def date_checker(ob):  # check links for date
            date_formats = r'\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{8}'
            match = re.search(date_formats, ob)
            return bool(match)

        for link in soup.find_all('a', href=True):
            link = link['href']
            link = str(link)

            forbidden_found = False

            if (web in link and len(link) > 30) or (url not in link and len(link) >= 25) or ('/p/' in link) or (
                    re.search(r'/\d{6}', link)):  # check links and edit them
                for word in forbidden_words:
                    if word in link:
                        forbidden_found = True
                        break

                if not forbidden_found:
                    if (date_checker(link)) or ('/news/' in link) or (len(link) > 40 and link.count(
                            '-') >= 3) or ('/p/' in link) or (re.search(r'/\d{6}', link)):
                        if link[0:4] != 'http':
                            link = web + link
                        if link not in new_links:
                            new_links.append((url, link))

    @staticmethod
    def get_downloaded_urls(db_access_key, links_from_db):  # collect already uploaded urls
        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select URL from NS_table")
                result = cursor.fetchall()
                result = [i[0] for i in result]
                for el in result:
                    links_from_db.append(el)

    @staticmethod
    def urls_duplicate_check(new_list, old_list):  # delete duplicates urls
        new_list[:] = set([el for el in new_list if el[1] not in old_list])

    @staticmethod
    def urls_record(db_access_key, link, url,
                    time):  # record unique links in the database and set status 'not_downloaded'
        web = url.split('/')[2]

        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "insert into NS_table (Web, URL, DownloadTime, Status) values ('{}', '{}', '{}', 'not_downloaded');\n".format(
                web, link, time)

            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()
