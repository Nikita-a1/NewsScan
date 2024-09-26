# from mysql.connector import connect
#
# def f(db_access_key):
#
#     with connect(
#             host=db_access_key['host'],
#             port=db_access_key['port'],
#             user=db_access_key['user'],
#             password=db_access_key['password'],
#             database=db_access_key['database']
#     ) as connection:
#         request = "INSERT INTO Users_table (id, tg_channel) VALUES (1, 'John Doe') ON DUPLICATE KEY UPDATE tg_channel = 'www';"
#
#         with connection.cursor() as cursor:
#             cursor.execute(request)
#             connection.commit()
#
#
#
# db_access_key = {'host': '172.20.10.2', 'port': 3306, 'user': 'Nicki', 'password': 'sql123', 'database': 'NS_db'}
#
# f(db_access_key)



# tuple = {'user_id': 1, 'tg_channel': -1002217281756, 'webs': None, 'key_words': 333, 'stop_words': ['слово1', 'слово2']}
# if all(tuple[element] for element in tuple):
#     print(1)


# dollar = '$'
# string = f'На моём счету 1.000.000.000{dollar}'
#
# print(string)
#
#
# l1 = ['Павел Дуров', 'Телеграм']
# l2 = ', '.join(l1)
# print(l2)


from bs4 import BeautifulSoup
import requests
import time

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
# urls_list = ['https://www.autonews.ru', 'https://thebell.io', 'https://quote.ru/', 'https://rbc.ru/', 'https://www.interfax.ru/business', 'https://www.forbes.ru', 'https://www.kommersant.ru', 'https://ru.investing.com/news/economy', 'https://ria.ru', 'https://lenta.ru']
#
# for url in urls_list:
#     try:
#         response = requests.get(url)
#     except:
#         print(url)
#
#
#     # response.encoding = response.apparent_encoding
#     response.encoding = 'utf-8'
#
#     # if response != '<Response [200]>':
#     #     response = requests.get(url, headers=headers)
#
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     title = soup.find('title').text.strip()
#
#     print(response)
#     print(title)

headers = {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X; U; en) Presto/2.2.15 Version/10.00'}
response = requests.get('https://www.interfax.ru/business', headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
title = soup.find('title').text.strip()
print(title)