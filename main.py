import urls_collector
import parser
import summary
import telegram
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
language = config_data['language']
frequency = config_data['frequency']
db_access_key = keys_data['database']

write_log = log.Log.write_log
collect_links_from_url = urls_collector.UrlsCollector.all_urls
get_all_links_from_db = urls_collector.UrlsCollector.get_downloaded_urls
check_duplicate_links = urls_collector.UrlsCollector.urls_duplicate_check
record_new_url = urls_collector.UrlsCollector.urls_record
collect_links_for_parsing = parser.Parser.urls_db_download
get_text_from_link = parser.Parser.text_downloader
collect_content_for_summarising = summary.Summary.content_db_download
detect_interesting_articles = summary.Summary.detect_interesting_articles
translate_to_english = summary.Summary.trans_to_english
compress_article = summary.Summary.compress_article
translate_back = summary.Summary.trans_back
summarised_articles_db_upload = summary.Summary.summarised_articles_db_uploader
get_summaries_from_db = telegram.Sender.get_summary_from_db
get_telegram_format = telegram.Sender.telegram_format
send_message = telegram.Sender.send_msg

new_links = []  # create a list of links from websites
links_from_db = []  # create a list of uploaded links from database
links_for_parsing = []  # create a list of links for parsing
downloaded_articles = []  # create a list of articles from db with 'downloaded' status
content_for_translation = []  # create a list of articles with keywords to translate
english_content = []  # create a list of english articles
compressed_content = []  # create a list of compressed articles in english
ready_content = []  # create a list of compressed articles in native language
summarized_articles = []  # create a list of compressed articles from database
articles_to_send = []  # create a list of tg-format articles

for word in key_words:  # change the case of keywords letters
    word = str(word)
    new_word = word.lower()
    if new_word != word:
        key_words.append(new_word)

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


detect_interesting_articles(downloaded_articles, content_for_translation, key_words, stop_words)
print('interesting articles: ' + str(len(content_for_translation)))

try:
    translate_to_english(content_for_translation, english_content)  # translate content to english and write it to english_content
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't translate article to english")
print('articles translated: ' + str(len(english_content)))


for article_block in english_content:  # compress articles in english
    try:
        compress_article(article_block, compressed_content)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(article_block[0]),
                  "Can't compress the article")
print('articles compressed: ' + str(len(compressed_content)))


translate_back(compressed_content, ready_content)  # translate compressed articles back
print('summaarized articles: ' + str(len(ready_content)))


for article_block in ready_content:  # update summarised articles
    id = article_block[0]
    text = article_block[1]
    try:
        summarised_articles_db_upload(db_access_key, id, text)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), str(id),
                      "Can't connect to database to upload summary")


#  TELEGRAM.PY
try:  # collect all summaries from database to summarized_articles
    get_summaries_from_db(db_access_key, webs, summarized_articles)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all summaries")


try:  # set telegram format for each article
    get_telegram_format(summarized_articles, articles_to_send, language)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
              "telegram-format fault")

count = 0
for article_block in articles_to_send:  # send all articles in tg channel
    title = article_block[0]
    summary = article_block[1]
    website = article_block[2]
    link = article_block[3]

    try:
        send_message(title, summary, website, link)
        count += 1
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
                  "telegram send fault")
print('articles sent: ' + str(count))