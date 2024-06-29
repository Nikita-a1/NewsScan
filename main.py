import mysql.connector
import requests.exceptions
import urllib3.exceptions
import urls_collector
import parser
import log
import yaml
import datetime

PATH_config = 'config.yml'  # specify the path for the file
PATH_keys = 'keys.yml'

try:  # try to open config.yml file
    with open(PATH_config, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)
except:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't open the config.yml file")

try:  # try to open keys.yml file
    with open(PATH_keys, 'r', encoding='utf-8') as file:
        keys_data = yaml.safe_load(file)
except:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't open the keys.yml file")

user_id = config_data['user_id']  # write data from the yml file to variables
webs = config_data['webs']
key_words = config_data['key_words']
stop_words = config_data['stop_words']
frequency = config_data['frequency']
db_access_key = keys_data['database']

write_log = log.Log.write_log
collect_links_from_url = urls_collector.UrlsCollector.all_urls
get_all_links_from_db = urls_collector.UrlsCollector.get_downloaded_urls
check_duplicate_links = urls_collector.UrlsCollector.urls_duplicate_check
record_new_url = urls_collector.UrlsCollector.urls_record
collect_links_for_parsing = parser.Parser.urls_db_download
get_text_from_link = parser.Parser.text_downloader

all_links_from_url = urls_collector.new_urls_list
all_links_from_db = urls_collector.download_urls_list
links_for_parsing = parser.Parser.urls_from_db
content_for_summary = parser.Parser.content_for_summary


for word in key_words:  # change the case of letters
    new_word = word.lower()
    if new_word != word:
        key_words.append(new_word)


for url in webs:  # collect all links from websites and write them to new_urls_list
    if url[-1] == '/':
        webs[webs.index(url)] = webs[webs.index(url)].rstrip(url[-1])
        url = url.rstrip(url[-1])
    try:
        collect_links_from_url(url)
    except ConnectionError:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), url,
                  "URLs parsing fault")
print(all_links_from_url)


try:  # collect already uploaded links from database
    get_all_links_from_db(db_access_key)
except mysql.connector.Error:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get already uploaded urls")
print(all_links_from_db)


check_duplicate_links(all_links_from_url, all_links_from_db)  # delete duplicates urls
print(all_links_from_url)


for new_url in all_links_from_url:  # record unique links in the database and set status 'not_downloaded'
    try:
        record_new_url(db_access_key, new_url, str(datetime.datetime.now().today().replace(microsecond=0)))
    except mysql.connector.Error:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                  "Can't connect to database to upload new urls")


try:  # collect all urls from database to download their text
    collect_links_for_parsing(db_access_key, webs)
except ConnectionError:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all urls and download their text")
print(links_for_parsing)


for url in links_for_parsing:  # download urls content to database
    try:
        get_text_from_link(db_access_key, url, key_words, stop_words)
    except requests.exceptions.InvalidSchema:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                  "Can't download url text")
    except mysql.connector.errors.ProgrammingError:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                  "Can't download url text")
    except mysql.connector.errors.DataError:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                  "Can't download url text")
    except ConnectionError:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                  "Can't download url text")
    except urllib3.exceptions.ProtocolError:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(url),
                  "Can't download url text")


