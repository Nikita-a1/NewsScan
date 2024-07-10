import yaml
import os
from mysql.connector import connect


class Load:
    @staticmethod
    def get_users_requests(users_directory):
        webs = []
        users_requests = []

        yml_files = [file for file in os.listdir(users_directory) if
                     os.path.isfile(os.path.join(users_directory, file))]

        yml_files = [f for f in yml_files if f.endswith('.yml')]

        for yml_file in yml_files:
            path = os.path.join(users_directory, yml_file)
            with open(path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

                for web in data['webs']:
                    webs.append(web)

                users_requests.append(
                    {'user_id': data['user_id'], 'webs': data['webs'], 'key_words': data['key_words'],
                     'stop_words': data['stop_words'], 'language': data['language'], 'urls_to_send': [],
                     'sent_urls': []})

        return webs, users_requests

    @staticmethod
    def get_keys_data(path_keys):
        with open(path_keys, 'r', encoding='utf-8') as file:
            keys_data = yaml.safe_load(file)
            return keys_data['database']

    @staticmethod
    def update_users_table(db_access_key, user_request):
        user_id = user_request['user_id']
        key_words = user_request['key_words']
        stop_words = user_request['stop_words']
        language = user_request['language']
        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = """update Users_table set Key_words = "{}", Stop_words = "{}", Language = "{}" where id = "{}";""".format(
                key_words, stop_words, language, user_id)
            with connection.cursor() as cursor:
                cursor.execute(request)
                cursor.fetchall()
                connection.commit()

    @staticmethod
    def get_sent_urls(db_access_key, user_request):
        with connect(
                host=db_access_key['host'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = "select sent_URLs from Users_table where id = '{}'".format(user_request['user_id'])
            with connection.cursor() as cursor:
                cursor.execute(request)
                urls_sent = cursor.fetchall()
                user_request['urls_sent'] = urls_sent
                connection.commit()
