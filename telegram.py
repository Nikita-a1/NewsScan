from mysql.connector import connect
import requests
import time


class Sender:

    @staticmethod
    def get_summary_from_db(db_access_key, webs_list, articles_to_send):

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
            request = "select id, Title, Summary, Web, url from NS_table where Status = 'summarized' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(id, title, summary, website, url) for (id, title, summary, website, url) in result]
                for article_block in result:
                    articles_to_send.append(article_block)

    @staticmethod
    def send_msg(users_requests, articles_to_send, bot_token):

        for user_request in users_requests:
            urls_to_send = user_request['urls_to_send']
            sent_urls = user_request['sent_urls']
            channel_id = user_request['tg_channel']

            for article_block in articles_to_send:
                article_id = article_block[0]
                website = article_block[3]
                link = article_block[4]
                title = article_block[1]
                summary = article_block[2]

                if str(article_id) in urls_to_send and str(article_id) not in sent_urls:

                    message = f"[{website}]({link}) *{title}*\n{summary}"

                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    params = {'chat_id': channel_id, 'text': message, 'parse_mode': 'Markdown',
                              'disable_web_page_preview': True}

                    for i in range(2):
                        response = requests.post(url, data=params)

                        if response.status_code == 200:
                            user_request['sent_urls'].append(str(article_id))
                            print('article ' + str(article_id) + ' sent successfully')
                            break

                        elif response.status_code == 429:
                            retry_after = response.json().get('parameters', {}).get('retry_after', 45)
                            print(f"Too many requests. Retrying after {retry_after} seconds.")
                            time.sleep(retry_after)

    @staticmethod
    def update_sent_urls(db_access_key, user_request):
        user_id = user_request['user_id']
        sent_urls = user_request['sent_urls']
        sent_urls_str = ', '.join(sent_urls)

        if sent_urls:
            with connect(
                    host=db_access_key['host'],
                    port=db_access_key['port'],
                    user=db_access_key['user'],
                    password=db_access_key['password'],
                    database=db_access_key['database']
            ) as connection:
                request = """update Users_table set Sent_URLs = "{}" where id = "{}";""".format(sent_urls_str, user_id)
                print(request)
                with connection.cursor() as cursor:
                    cursor.execute(request)
                    connection.commit()



