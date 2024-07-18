from mysql.connector import connect
import requests


class Sender:

    @staticmethod
    def get_summary_from_db(db_access_key, webs_list, summarized_articles):

        if len(webs_list) == 1:
            webs_list = "('{}')".format(webs_list[0])
        else:
            webs_list = tuple(webs_list)

        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "select id, Title, Summary, Web, url from NS_table where Status = 'summarized' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(id, title, summary, website, url) for (id, title, summary, website, url) in result]
                for article_block in result:
                    summarized_articles.append(article_block)

    @staticmethod
    def get_urls_to_send_from_db(db_access_key, user_request):
        user_id = user_request['user_id']
        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "select URLs_to_send from Users_table where id = '{}';".format(user_id)
            with connection.cursor() as cursor:
                cursor.execute(request)
                urls_to_send = cursor.fetchone()[0].split(' ')
                for url_to_send in urls_to_send:
                    user_request['urls_to_send'].append(url_to_send)

    @staticmethod
    def telegram_format(summarized_articles, articles_to_send):
        for article_block in summarized_articles:
            article_id = article_block[0]
            title = article_block[1]
            summary = article_block[2]
            website = article_block[3]
            link = article_block[4]

            new_article = ""
            sentences = summary.split('. ')
            for i in range(len(sentences)):
                sentence = sentences[i]
                while '.' in sentence:
                    sentence = sentence.replace('.', '')
                if sentence and sentence != ' ':
                    new_article = new_article + '- ' + sentence + '.' + '\n'
            articles_to_send.append([article_id, website, link, title, new_article])

    @staticmethod
    def send_msg(users_requests, articles_to_send, bot_token):

        for user_request in users_requests:
            urls_to_send = user_request['urls_to_send']
            sent_urls = user_request['sent_urls']
            channel_id = user_request['tg_channel']

            for article_block in articles_to_send:
                article_id = article_block[0]
                website = article_block[1]
                link = article_block[2]
                title = article_block[3]
                summary = article_block[4]

                if str(article_id) in urls_to_send and str(article_id) not in sent_urls:

                    message = f"[{website}]({link}) *{title}*\n{summary}"

                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    params = {'chat_id': channel_id, 'text': message, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
                    requests.post(url, data=params)

                    user_request['sent_urls'].append(str(article_id))

    @staticmethod
    def update_sent_urls(db_access_key, user_request):
        user_id = user_request['user_id']
        sent_urls = user_request['sent_urls']
        sent_urls_str = ' '.join(sent_urls)

        if sent_urls:
            with connect(
                    host=db_access_key['host'],
                    user=db_access_key['user'],
                    password=db_access_key['password'],
                    database=db_access_key['database']
            ) as connection:
                request = """update Users_table set Sent_URLs = "{}" where id = "{}";""".format(sent_urls_str, user_id)
                with connection.cursor() as cursor:
                    cursor.execute(request)
                    connection.commit()



