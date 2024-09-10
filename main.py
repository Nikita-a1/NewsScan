import loader
import urls_collector
import parser
import summary
import telegram
import log
import datetime


users_directory = 'users'  # specify the path for the directory with users files
path_keys = 'keys.yml'  # specify the path for the hidden file

try:  # try to get users requests from users directory
    webs, users_requests = loader.Load.get_users_requests(users_directory)
except:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't open the users directory and get data")

try:  # try to get db_access_key from keys.yml file
    db_access_key = loader.Load.get_keys_data(path_keys)
except:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't open the keys.yml file to get db_access_key")

try:  # try to get data from keys.yml file
    api_key, prompt, bot_token = loader.Load.get_api_key(path_keys)
except:
    log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                      "Can't open the keys.yml file to get api_key")


write_log = log.Log.write_log
update_users_table = loader.Load.update_users_table
get_sent_urls = loader.Load.get_sent_urls
collect_links_from_url = urls_collector.UrlsCollector.all_urls
get_all_links_from_db = urls_collector.UrlsCollector.get_downloaded_urls
check_duplicate_links = urls_collector.UrlsCollector.urls_duplicate_check
record_new_url = urls_collector.UrlsCollector.urls_record
collect_links_for_parsing = parser.Parser.urls_db_download
get_text_from_link = parser.Parser.text_downloader
collect_content_for_summarising = summary.Summary.content_db_download
detect_interesting_articles = summary.Summary.detect_interesting_articles
compress_article = summary.Summary.compress_article
summarized_articles_db_upload = summary.Summary.summarized_articles_db_uploader
get_summaries_from_db = telegram.Sender.get_summary_from_db
send_message = telegram.Sender.send_msg
update_sent_urls = telegram.Sender.update_sent_urls

new_links = []  # create a list of links from websites
links_from_db = []  # create a list of uploaded links from database
links_for_parsing = []  # create a list of links for parsing
downloaded_articles = []  # create a list of articles from db with 'downloaded' status
content_for_summarization = []  # create a list of articles with keywords to translate
compressed_content = []  # create a list of compressed articles in english
articles_to_send = []  # create a list of tg-format articles


#  LOADER.PY
for user_request in users_requests:  # update keywords and stop words in database
    try:
        update_users_table(db_access_key, user_request)
    except:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                          "Can't update users table")


for user_request in users_requests:  # get already sent urls from database
    try:
        get_sent_urls(db_access_key, user_request)
    except:
        log.Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                          "Can't get sent urls from database")


#  URLS_COLLECTOR.PY
for url in webs:  # collect all links from websites and write them to new_urls_list
    if url[-1] == '/':
        webs[webs.index(url)] = webs[webs.index(url)].rstrip(url[-1])
        url = url.rstrip(url[-1])
    try:
        collect_links_from_url(url, new_links)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), url,
                  "URLs parsing fault")
print('urls downloaded: ' + str(len(new_links)))


try:  # collect already uploaded links from database and write them to links_from_db
    get_all_links_from_db(db_access_key, links_from_db)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get already uploaded urls")


check_duplicate_links(new_links, links_from_db)  # delete duplicates urls
print('urls uploaded: ' + str(len(new_links)))


for new_link in new_links:  # record unique links in the database and set status 'not_downloaded'
    url = new_link[0]
    link = new_link[1]
    try:
        record_new_url(db_access_key, link, url, str(datetime.datetime.now().today().replace(microsecond=0)))
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                  "Can't connect to database to upload new links")


#  PARSER.PY
try:  # collect all links from database to download their text
    collect_links_for_parsing(db_access_key, webs, links_for_parsing)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all urls and download their text")
print('urls for parsing: ' + str(len(links_for_parsing)))


for link in links_for_parsing:  # download links content to database
    try:
        get_text_from_link(db_access_key, link)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), link,
                  "Can't download link content")


#  SUMMARY.PY
try:  # collect all content from database for summarising to content_for_translation
    collect_content_for_summarising(db_access_key, webs, downloaded_articles)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all content")
print('all articles: ' + str(len(downloaded_articles)))


detect_interesting_articles(downloaded_articles, content_for_summarization,
                            users_requests)  # check articles for keywords and stop words
print('interesting articles: ' + str(len(content_for_summarization)))


for article_block in content_for_summarization:  # compress articles
    try:
        compress_article(article_block, compressed_content, api_key, prompt)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(article_block[0]),
                  "Can't compress the article")


for article_block in compressed_content:  # update summarized articles
    id = article_block[0]
    text = article_block[1]
    try:
        summarized_articles_db_upload(db_access_key, id, text)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(id),
                      "Can't connect to database to upload summary")


#  TELEGRAM.PY
try:  # collect all summaries from database to summarized_articles
    get_summaries_from_db(db_access_key, webs, articles_to_send)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all summaries")


# send all articles in tg channel
try:
    send_message(users_requests, articles_to_send, bot_token)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
              "telegram send fault")
print('sent')


for user_request in users_requests:  # update sent_urls to database
    try:
        update_sent_urls(db_access_key, user_request)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
                  "can't update sent urls")