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
            request = "select id, Content from NS_table where Status = 'downloaded' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(id, content) for (id, content) in result]
                for article_block in result:
                    downloaded_articles.append(article_block)

    @staticmethod
    def detect_interesting_articles(downloaded_articles, content_for_translation, key_words, stop_words):
        for article_block in downloaded_articles:
            article = article_block[1]
            for stop_word in stop_words:
                if stop_word in article:
                    downloaded_articles.remove(article_block)
                    continue
        for article_block in downloaded_articles:
            article = article_block[1]
            for key_word in key_words:
                if key_word in article:
                    content_for_translation.append(article_block)
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

            if len(text) > 1000:
                text = Summary.split_long_sentences(text)
            else:
                text = [text]

            for paragraph in text:
                translated_paragraph = translator.translate(paragraph, dest='en').text
                en_text = en_text + translated_paragraph

            english_content.append((id, en_text))

    @staticmethod
    def compress_article(article_block, compressed_content):
        model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6")
        tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

        id = article_block[0]
        content_to_summarize = article_block[1]
        summarized_content = ""

        while len(summarized_content) == 0 or len(summarized_content) > 3000 and len(content_to_summarize) > 0:
            content_to_summarize = Summary.split_long_sentences(content_to_summarize)
            summarized_content = ""
            for paragraph in content_to_summarize:
                inputs = tokenizer([paragraph], return_tensors="pt")
                summary_ids = model.generate(inputs["input_ids"], num_beams=3, min_length=0, max_length=15)
                paragraph = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
                summarized_content += paragraph
            content_to_summarize = summarized_content

        compressed_content.append((id, summarized_content))
        print('done')


    @staticmethod
    def trans_back(compressed_content, ready_content):
        translator = Translator()
        for article_block in compressed_content:
            id = article_block[0]
            text = article_block[1]
            result = translator.translate(text, dest='ru').text
            while ' .' in result:
                result = result.replace(' .', '.')
            ready_content.append((id, result))

    @staticmethod
    def summarised_articles_db_uploader(db_access_key, id, article):
        with connect(
                host=db_access_key['host'],
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
