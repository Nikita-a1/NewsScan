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
translate_to_english = summary.Summary.trans_to_english
compress_article = summary.Summary.compress_article
translate_back = summary.Summary.trans_back
summarised_articles_db_upload = summary.Summary.summarised_articles_db_uploader
get_telegram_format = telegram.Sender.telegram_format
send_message = telegram.Sender.send_msg

new_links = []  # create a list of links from websites
links_from_db = []  # create a list of uploaded links from database
links_for_parsing = []  # create a list of links for parsing
content_for_translation = [('article1', 'СИМФЕРОПОЛЬ, 1 июл – РИА Новости. Отражение ракетной атаки на Севастополь продолжается, предварительно 4 воздушные цели уничтожены в небе над акваторией и в районе Балаклавы, сообщил губернатор города Михаил Развожаев в своем Telegram-канале. Ранее в городе объявили воздушную тревогу. Сообщалось о работе ПВО. «"Отражение ракетной атаки продолжается. По предварительной информации, 4 воздушные цели уничтожены в небе над акваторией и в районе Балаклавы", - написал Развожаев. По его словам, ситуация на контроле экстренных служб.'), ('article2', 'В Николаевской области фиксируется активность украинской авиации. Об этом РИА Новости сообщил координатор николаевского подполья Сергей Лебедев.'), ('article3', 'ВАШИНГТОН, 1 июл — РИА Новости. Верховный суд США отказался признать за Дональдом Трампом абсолютный иммунитет от юридического преследования за действия в бытность президентом. В постановлении говорится, что президент неподсуден только за действия, совершенные им в официальном качестве, но часть из того, что ему инкриминируется, под это определение может не подпадать. «Другие обвинения, в том числе относящиеся к взаимодействию Трампа с вице-президентом, должностными лицами штатов и отдельными частными сторонами, а также его высказывания на публике, представляют собой более сложный вопрос», — говорится в постановлении суда. Трамп настаивает на том, что его нельзя судить за действия, относящиеся к периоду его пребывания в должности президента США, включая центральный эпизод процесса — штурм Капитолия его сторонниками 6 января 2021 года в попытке сорвать утверждение конгрессом победы на президентских выборах его конкурента-демократа Джо Байдена.')
, ('article4', 'Осколки сбитых над Севастополем ракет упали в прибрежной зоне и Балаклавском районе, заявил губернатор Михаил Развожаев. Предварительно, уничтожены четыре цели над городом. Информация о возможных повреждениях уточняется, также сказал он. Ранее в городе объявили ракетную опасность. Работали силы ПВО.'), ('article5', 'Верховный суд США постановил, что экс-президент Дональд Трамп имеет право на уголовный иммунитет по делу о попытках повлиять на результаты выборов 2020 года, сообщает CNN. В феврале этого года федеральный апелляционный суд вынес решение, согласно которому в рамках данного дела «бывший президент Трамп стал гражданином Трампом» и потому он не имел иммунитета, который был бы ему положен как занимавшему президентский пост. Верховный суд эту трактовку отклонил. «В соответствии с нашей конституционной структурой разделения властей характер президентской власти требует, чтобы бывший президент имел определенный иммунитет от уголовного преследования за официальные действия во время своего пребывания в должности. По крайней мере, в отношении осуществления президентом своих основных конституционных полномочий этот иммунитет должен быть абсолютным», — говорится в заключении судьи Джона Робертса. Он отметил, что президент не имеет иммунитета в отношении своих неофициальных действий: не все, что делает глава государства, носит официальный характер. Поэтому суду первой инстанции (окружной) предстоит оценить, какие действия Трампа будут защищены согласно решению Верховного суда, а какие нет. Экс-президент в своей соцсети Truth Social назвал решение «большой победой для нашей Конституции и демократии». В феврале адвокаты Трампа настаивали, что политик обладает «абсолютным иммунитетом» от преследования, поскольку обвинения связаны с действиями, совершенными в то время, когда он был президентом. Помимо обвинения, связанного с событиями в Капитолии в январе 2021 года, Трампа подозревают в еще нескольких преступлениях: попытке отменить его поражение на президентских выборах 2020 года в штате Джорджия; хранении в его резиденции во Флориде Мар-а-Лаго секретных документов; подлоге финансовой документации. Это дело также известно как связанное с выплатами порноактрисе Сторми Дэниэлс: ей заплатили за молчание о романе с женатым Трампом в 2006 году, в документах это было отражено как расход на оплату юридических услуг. В конце мая суд присяжных признал Трампа виновным по этому делу, 11 июля будет вынесено судебное решение.')]  # create a list of articles texts to translate them
english_content = []  # create a list of english articles
compressed_content = []  # create a list of compressed articles in english
ready_content = []  # create a list of compressed articles in native language
summarized_articles = [("title1", "Продолжается отражение ракетной атаки на Севастополь. Ранее в небе над акваторией и в районе Балаклавы были уничтожены четыре воздушные цели, сообщил городской губернатор Михаил Развожаев. Ранее в городе была объявлена воздушная тревога.", "web1.ru", "https://web1.ru"),
    ("title2", "Верховный суд США отказался предоставить Дональду Трампу абсолютный иммунитет от судебного преследования за его действия на посту президента. Президент пользуется иммунитетом только за действия, совершенные им в официальном качестве. Трамп настаивал на том, что его нельзя судить за действия, совершенные еще во время его пребывания на посту президента.", "web2.ru", "https://web2.ru"),
    ("title3", "Обломки ракет, сбитых над Севастополем, упали в прибрежной зоне и районе Балаклавы. Ранее были уничтожены четыре цели над городом. Информация о возможном ущербе уточняется.", "web3.ru", "https://web3.ru"),
    ("title4", "Верховный суд США постановил, что бывший президент Дональд Трамп имеет право на уголовную неприкосновенность по делу о попытках повлиять на результаты выборов 2020 года. Верховный суд отверг интерпретацию, что президент обладает иммунитетом в отношении своих неофициальных действий.", "web4.ru", "https://web4.ru")
]  # create a list of tg-format articles from database
articles_to_send = []  # create a list of tg-format articles

for word in key_words:  # change the case of keywords letters
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
print(new_links)


try:  # collect already uploaded links from database and write them to links_from_db
    get_all_links_from_db(db_access_key, links_from_db)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get already uploaded urls")
print(links_from_db)


check_duplicate_links(new_links, links_from_db)  # delete duplicates urls
print(new_links)


for new_link in new_links:  # record unique links in the database and set status 'not_downloaded'
    try:
        record_new_url(db_access_key, new_link, str(datetime.datetime.now().today().replace(microsecond=0)))
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
                  "Can't connect to database to upload new links")

#  PARSER.PY
try:  # collect all links from database to download their text
    collect_links_for_parsing(db_access_key, webs, links_for_parsing)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all urls and download their text")
print(links_for_parsing)


for link in links_for_parsing:  # download links content to database
    try:
        get_text_from_link(db_access_key, link, key_words, stop_words)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), link,
                  "Can't download link content")


#  SUMMARY.PY
try:  # collect all content from database for summarising to content_for_translation
    collect_content_for_summarising(db_access_key, webs, content_for_translation)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all content")


translate_to_english(content_for_translation, english_content)  # translate content to english and write it to english_content


for article_block in english_content:  # compress articles in english
    try:
        compress_article(article_block, compressed_content)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), article_block[0],
                  "Can't compress the article")


translate_back(compressed_content, ready_content)  # translate compressed articles back


for article_block in ready_content:  # update summarised articles
    try:
        summarised_articles_db_upload(db_access_key, article_block[0], article_block[1])
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), article_block[0],
                      "Can't connect to database to upload summary")


#  TELEGRAM.PY
try:  # collect all summaries from database to summarized_articles
    collect_content_for_summarising(db_access_key, webs, summarized_articles)
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "---",
              "Can't connect to database to get all summaries")


try:
    get_telegram_format(summarized_articles, articles_to_send, language)  # set telegram format for each article
except:
    write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
              "telegram-format fault")


for article_block in articles_to_send:  # send all articles in tg channel
    try:
        link_text = article_block[2]
        link = article_block[3]
        title = article_block[0]
        text = article_block[1]
        send_message(link_text, link, title, text)
    except:
        write_log(str(datetime.datetime.now().today().replace(microsecond=0)), '---',
                  "telegram send fault")


