from transformers import AutoTokenizer, BartForConditionalGeneration
from mysql.connector import connect
from googletrans import Translator

class Summary:

    @staticmethod
    def content_db_download(db_access_key, webs_list, content_for_translation):

        for i in range(len(webs_list)):
            webs_list[i] = webs_list[i].split('/')[2]

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
            request = "select URL, Content from NS_table where Status = 'downloaded' and Web in {}".format(webs_list)
            with connection.cursor() as cursor:
                cursor.execute(request)
                result = cursor.fetchall()
                result = [(url, content) for (url, content) in result]
                for article_block in result:
                    content_for_translation.append(article_block)

    @staticmethod
    def trans_to_english(content_for_translation, english_content):
        translator = Translator()
        for article_block in content_for_translation:
            english_text = translator.translate(article_block[1], dest='en').text
            english_content.append((article_block[0], english_text))

    @staticmethod
    def compress_article(article_block, compressed_content):
        model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6")
        tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

        article_to_summarise = article_block[1]

        inputs = tokenizer([article_to_summarise], return_tensors="pt")
        summary_ids = model.generate(inputs["input_ids"], num_beams=3, min_length=0)
        output = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        compressed_content.append((article_block[0], output))

    @staticmethod
    def trans_back(compressed_content, ready_content):
        translator = Translator()
        for article_block in compressed_content:
            result = translator.translate(article_block[1], dest='ru').text
            while ' .' in result:
                result = result.replace(' .', '.')
            ready_content.append((article_block[0], result))
            print(result)

    @staticmethod
    def summarised_articles_db_uploader(db_access_key, link, article):
        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "update NS_table set Summary = '{}', Status = 'summarized' where URl = '{}';".format(
                article, link)
            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()



#
# text_to_trans = """Новолипецкий металлургический комбинат (НЛМК) атаковал рой беспилотных летательных аппаратов (БПЛА). Об этом сообщает ТАСС со ссылкой на представителя российского предприятия.
#
# НЛМК производит гражданскую продукцию. В воскресенье, 30 июня, по его территории ударили дроны. Представитель компании отметил, что атака оказалась бессмысленна, так как ни к чему, кроме роста сварочных работ, не привела.
#
# Ранее в этот же день губернатор Липецкой области Игорь Артамонов сообщил, что над промышленной зоной Липецка сбили девять беспилотников. Он назвал прошедшую ночь непростой и неспокойной.
#
# Позже издание Baza сообщило, что в два часа ночи семь украинских БПЛА атаковали Новолипецкий металлургический комбинат. Они кружили возле предприятия около часа. В результате один из упавших дронов повредил гараж. Еще четыре беспилотника пытались повредить здание кислородной станции. Один дрон нарушил целостность установки разделения кислорода."""
#
# english_text = translator.translate(text_to_trans, dest='en').text
#
#
# model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
# tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
# input_ids = tokenizer(english_text, return_tensors="tf").input_ids
# output = model.generate(input_ids, min_length=175, num_beams=5, early_stopping=True)
#
# summarised_text = tokenizer.decode(output[0], skip_special_tokens=True)
#
# output = translator.translate(summarised_text, dest='ru')
#
# print(output.text)