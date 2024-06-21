import mysql.connector
import requests.exceptions
import urls_collector
import parser
import log
import yaml
import datetime

PATH = 'config.yml'  # specify the path for the file

try:  # try to open the yaml file
    with open(PATH, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---", "Can't open the yaml file")

user_id = data['user_id']  # write data from the yml file to variables
webs = data['webs']
key_words = data['key_words']
stop_words = data['stop_words']
frequency = data['frequency']
host = data['database']['host']
user = data['database']['user']
password = data['database']['password']
database = data['database']['database']


for url in webs:  # collect all links from websites and write them to new_urls_list
    if url[-1] == '/':
        url = url.rstrip(url[-1])

    try:
        urls_collector.UrlsCollector.all_urls(url)
    except ConnectionError:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), url,
                          "URLs parsing fault")
print(urls_collector.new_urls_list)


try:  # collect already uploaded urls from database
    urls_collector.UrlsCollector.get_downloaded_urls(host, user, password, database)
except mysql.connector.Error:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't connect to database to get already uploaded urls")
print(urls_collector.download_urls_list)


urls_collector.UrlsCollector.urls_duplicate_check(urls_collector.new_urls_list,  # delete duplicates urls
                                                  urls_collector.download_urls_list)
print(urls_collector.new_urls_list)


try:  # record unique links in the database and set status 'not_downloaded'
    urls_collector.UrlsCollector.urls_record(host, user, password, database,
                                             str(datetime.datetime.now().today().replace(microsecond=0)))
except mysql.connector.Error:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't connect to database to upload new urls")


try:  # collect all urls from database to download their text
    parser.Parser.urls_db_download(host, user, password, database)
except ConnectionError:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't connect to database to get all urls and download their text")
print(urls_collector.download_urls_list)


for url in parser.Parser.urls_from_db:
    try:
        parser.Parser.text_downloader(host, user, password, database, url)
    except requests.exceptions.InvalidSchema:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                          "Can't download url text")
    except mysql.connector.errors.ProgrammingError:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                          "Can't download url text")
    except mysql.connector.errors.DataError:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                          "Can't download url text")
