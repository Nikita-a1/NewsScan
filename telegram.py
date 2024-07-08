from mysql.connector import connect
import requests
from googletrans import Translator


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
            request = "select Title, Summary, Web, url from NS_table where Status = 'summarized' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(title, summary, website, url) for (title, summary, website, url) in result]
                for article_block in result:
                    summarized_articles.append(article_block)


    @staticmethod
    def telegram_format(summarized_articles, articles_to_send, language):
        for article_block in summarized_articles:
            title = article_block[0]
            summary = article_block[1]
            website = article_block[2]
            link = article_block[3]
            translator = Translator()

            new_article = ""
            sentences = summary.split('. ')
            for i in range(len(sentences)):
                sentence = sentences[i]
                if i < len(sentences) - 1 and sentences[i + 1][0].isupper():
                    sentence += '.'
                new_article = new_article + '- ' + sentence + '\n'

            new_article = translator.translate(new_article, dest=language).text
            new_title = translator.translate(title, dest=language).text
            articles_to_send.append((new_title, new_article, website, link))

    @staticmethod
    def send_msg(title, summary, website, link):
        bot_token = '7359065426:AAH7DTsO5vgmwvSU1d110CEiPHi64nI1lUo'
        channel_id = '-1002229910677'

        message = f"[{website}]({link}) *{title}* \n {summary}"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {'chat_id': channel_id, 'text': message, 'parse_mode': 'Markdown'}
        requests.post(url, data=params)



