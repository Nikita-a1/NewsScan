from transformers import AutoTokenizer, BartForConditionalGeneration
from mysql.connector import connect
from googletrans import Translator
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
    def detect_interesting_articles(downloaded_articles, content_for_translation, users_requests):

        for article_block in downloaded_articles:
            article_id = article_block[0]
            article = article_block[1]
            status = article_block[2]
            for user_request in users_requests:

                for key_word in user_request['key_words']:
                    if str(key_word) in article:
                        if article_id not in user_request['urls_to_send']:
                            user_request['urls_to_send'].append(str(article_id))
                        if article_block not in content_for_translation and status == 'downloaded':
                            content_for_translation.append(article_block)
                        continue
                for stop_word in user_request['stop_words']:
                    if str(stop_word) in article:
                        if article_block in content_for_translation:
                            content_for_translation.remove(article_block)
                        if article_id in user_request['urls_to_send']:
                            user_request['urls_to_send'].remove(article_id)
                        continue

    @staticmethod
    def split_long_sentences(sentence):
        result = []
        if len(sentence) > 1024:
            sub_sentences = re.split(r'(?<=[.!?]) +', sentence)
            current_sentence = sub_sentences[0]
            for sub_sentence in sub_sentences[1:]:
                if len(current_sentence) + len(sub_sentence) > 1024:
                    result.append(current_sentence)
                    current_sentence = sub_sentence
                else:
                    current_sentence += " " + sub_sentence
            result.append(current_sentence)
        else:
            result.append(sentence)
        return result

    @staticmethod
    def trans_to_english(content_for_translation, english_content):

        translator = Translator()
        for article_block in content_for_translation:
            id = article_block[0]
            text = article_block[1]
            en_text = ""

            paragraphs = text.split('<paragraph>')

            for paragraph in paragraphs:
                if paragraph:
                    if len(paragraph) > 1000:
                        sentences = Summary.split_long_sentences(paragraph)
                        for sentence in sentences:
                            translated_sentence = translator.translate(sentence, dest='en').text
                            en_text += translated_sentence + ' '
                        en_text += '<paragraph>'
                    else:
                        translated_paragraph = translator.translate(paragraph, dest='en').text
                        en_text += translated_paragraph + '<paragraph>'

            re.sub(r'(?<=[.!?])(?=[^\s])', ' ', en_text)
            english_content.append((id, en_text))

    @staticmethod
    def compress_article(article_block, compressed_content):
        model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6")
        tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
        id = article_block[0]
        content_to_summarize = article_block[1]
        summarized_content = ""

        split_content = content_to_summarize.split('<paragraph>')

        for paragraph in split_content:
            if paragraph:
                if len(paragraph) < 1000:
                    inputs = tokenizer([paragraph], return_tensors="pt")
                    summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=0, max_length=30)
                    paragraph = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
                    summarized_content = summarized_content + paragraph + '<paragraph>'
                else:
                    sentences = Summary.split_long_sentences(paragraph)
                    for sentence in sentences:
                        inputs = tokenizer([sentence], return_tensors="pt")
                        summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=0)
                        sentence = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
                        summarized_content = summarized_content + ' ' + sentence
                    summarized_content += '<paragraph>'

        compressed_content.append((id, summarized_content))
        print('done')

    @staticmethod
    def trans_back(compressed_content, ready_content):
        translator = Translator()
        for article_block in compressed_content:
            id = article_block[0]
            text = article_block[1]
            split_text = text.split('<paragraph>')
            result = ""

            for paragraph in split_text:
                if paragraph:
                    paragraph = translator.translate(paragraph, dest='ru').text
                    paragraph = re.sub(r'(?<=[^.])([.!?])', r'\1 ', paragraph)
                    paragraph = ' '.join(paragraph.split())
                    result += paragraph + ' '

            ready_content.append((id, result))

    @staticmethod
    def summarized_articles_db_uploader(db_access_key, id, article):
        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "update NS_table set Summary = '{}', Status = 'summarized' where id = '{}';".format(
                article, id)
            print(request)
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
                    user=db_access_key['user'],
                    password=db_access_key['password'],
                    database=db_access_key['database']
            ) as connection:
                request = """update Users_table set URLs_to_send = "{}" where id = "{}";""".format(
                    urls_to_send_str, user_id)
                with connection.cursor() as cursor:
                    cursor.execute(request)
                    connection.commit()
