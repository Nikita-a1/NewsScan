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
    try:
        urls_collector.UrlsCollector.all_urls(url)
    except ConnectionError:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), url,
                          "URLs parsing fault")
print(urls_collector.new_urls_list)


try:  # collect already uploaded urls from database
    urls_collector.UrlsCollector.get_downloaded_urls(host, user, password, database)
except ConnectionError:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't connect to database to get already uploaded urls")
print(urls_collector.download_urls_list)


urls_collector.UrlsCollector.urls_duplicate_check()  # delete duplicates urls
print(urls_collector.new_urls_list)


# for new_url in urls_collector.new_urls_list:  # record unique links in the database and set status 'not_downloaded'
#     try:
#         urls_collector.UrlsCollector.urls_record(host, user, password, database, new_url)
#     except ConnectionError:
#         log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
#                           "Can't connect to database to upload new urls")


try:  # collect all urls from database to download their text
    parser.Parser.urls_db_download(host, user, password, database)
except ConnectionError:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't connect to database to get all urls and download their text")
print(urls_collector.download_urls_list)


for url in parser.Parser.urls_from_db:
    try:
        parser.Parser.text_downloader(url)
    except ConnectionError:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), url,
                          "Can't download url text")
