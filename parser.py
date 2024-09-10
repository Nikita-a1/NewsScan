import requests
from bs4 import BeautifulSoup
from mysql.connector import connect


class Parser:

    @staticmethod
    def urls_db_download(db_access_key, webs_list, links_for_parsing):  # collects all urls from database in urls_from_db to
        # download their text

        for i in range(len(webs_list)):
            webs_list[i] = webs_list[i].split('/')[2]

        if len(webs_list) == 1:
            webs_list = "('{}')".format(webs_list[0])
        else:
            webs_list = tuple(webs_list)

        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "select URL from NS_table where Status = 'not_downloaded' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                connection.commit()
                result = [''.join(link) for link in result]
                for link in result:
                    links_for_parsing.append(link)

    @staticmethod
    def text_downloader(db_access_key, link):  # download content for each link
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        response = requests.get(link)
        response.encoding = response.apparent_encoding

        if response != '<Response [200]>':
            response = requests.get(link, headers=headers)
            response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            title = soup.find('title').text.strip()
        except:
            try:
                title = soup.find('h1').text.strip()
            except:
                try:
                    title = soup.find('span').text.strip()
                except:
                    title = 'Заголовок не найден'

        tags = ['p', 'li', 'u']
        prohibited_tags = ['comment', 'footer_text', 'block-error-message', 'overscroll', 'footer__body__social__row',
                           'footer__body__copyright', 'article__main-image__author', 'footer__bottom__middle']

        max_length = 0
        content = ""

        for tag in tags:
            all_text = []
            length = 0
            prohibited_found = False
            request = soup.findAll(tag)

            for string in request:

                text = str(string.get_text().strip())

                for prohibited_tag in prohibited_tags:
                    if prohibited_tag in str(string.parent):
                        prohibited_found = True
                        break
                if not prohibited_found:
                    while '  ' in text:
                        text = text.replace('  ', ' ')
                    while '\n' in text:
                        text = text.replace('\n', '')
                    if len(text) > 75:
                        all_text.append(text)
                        length += len(text)
            if length > max_length:
                for el in all_text:
                    content = content + el + ' '
                max_length = length

        request = soup.findAll('div', class_='article__text')
        for string in request:
            text = str(string.get_text().strip())

            if 'comment' not in str(string.parent) and len(text) > 100:
                while '  ' in text:
                    text = text.replace('  ', ' ')
                while '\n' in text:
                    text = text.replace('\n', '')
                content = content + text + ' '

        Parser.text_db_uploader(db_access_key, title, content, link)

    @staticmethod
    def text_db_uploader(db_access_key, title, content, link):
        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "update NS_table set Title = '{}', Content = '{}', Status = 'downloaded' where URl = '{}';".format(
                title, content, link)
            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()
