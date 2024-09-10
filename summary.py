from mysql.connector import connect
from openai import OpenAI
import re


class Summary:

    @staticmethod
    def content_db_download(db_access_key, webs_list, downloaded_articles):

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
            request = "select id, Content, status from NS_table where Status in ('downloaded', 'summarized') and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(id, content, status) for (id, content, status) in result]
                for article_block in result:
                    downloaded_articles.append(article_block)

    @staticmethod
    def detect_interesting_articles(downloaded_articles, content_for_summarization, users_requests):

        for article_block in downloaded_articles:
            article_id = article_block[0]
            article = article_block[1]
            article = article.lower()
            status = article_block[2]

            good_article = True

            for user_request in users_requests:

                key_words = user_request['key_words']
                stop_words = user_request['stop_words']

                for key_word in key_words:
                    if key_word:
                        key_word = key_word.lower()
                        key_pattern = r'\b' + re.escape(key_word) + r'\b'
                        if re.search(key_pattern, article.lower()):

                            for stop_word in stop_words:
                                if stop_word:
                                    stop_word = stop_word.lower()
                                    stop_pattern = r'\b' + re.escape(stop_word) + r'\b'
                                    if re.search(stop_pattern, article.lower()):
                                        good_article = False
                                        break

                            if good_article:
                                if str(article_id) not in user_request['urls_to_send']:
                                    user_request['urls_to_send'].append(str(article_id))
                                if article_block not in content_for_summarization and status == 'downloaded':
                                    content_for_summarization.append(article_block)
                            break

    @staticmethod
    def compress_article(article_block, compressed_content, api_key, prompt):
        article_id = article_block[0]
        article = article_block[1]
        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": article}
            ]
        )
        summarized_article = completion.choices[0].message.content
        compressed_content.append((article_id, summarized_article))

    @staticmethod
    def summarized_articles_db_uploader(db_access_key, id, article):
        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "update NS_table set Summary = '{}', Status = 'summarized' where id = '{}';".format(
                article, id)
            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()

    @staticmethod
    def urls_to_send_db_uploader(db_access_key, user_request):
        user_id = user_request['user_id']
        urls_to_send = user_request['urls_to_send']
        urls_to_send_str = ' '.join(urls_to_send)

        if urls_to_send_str:
            with connect(
                    host=db_access_key['host'],
                    port=db_access_key['port'],
                    user=db_access_key['user'],
                    password=db_access_key['password'],
                    database=db_access_key['database']
            ) as connection:
                request = """update Users_table set URLs_to_send = "{}" where id = "{}";""".format(
                    urls_to_send_str, user_id)
                print(request)
                with connection.cursor() as cursor:
                    cursor.execute(request)
                    connection.commit()
