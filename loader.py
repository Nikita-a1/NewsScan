import yaml
import os
from mysql.connector import connect


class Load:

    @staticmethod
    def get_users_requests(users_directory):
        webs_all = []
        users_requests = []

        yml_files = [file for file in os.listdir(users_directory) if
                     os.path.isfile(os.path.join(users_directory, file))]

        yml_files = [f for f in yml_files if f.endswith('.yml')]

        for yml_file in yml_files:
            path = os.path.join(users_directory, yml_file)
            with open(path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

                if all(data[element] for element in data):

                    for web in data['webs']:
                        webs_all.append(web)

                    data['key_words'] = list(map(str, data['key_words']))
                    data['stop_words'] = list(map(str, data['stop_words']))

                    users_requests.append(
                        {'user_id': data['user_id'],
                         'tg_channel': data['tg_channel'],
                         'webs': data['webs'],
                         'key_words': data['key_words'],
                         'stop_words': data['stop_words'],
                         'urls_to_send': [],
                         'sent_urls': []})

        return webs_all, users_requests

    @staticmethod
    def get_keys_data(path_keys):
        with open(path_keys, 'r', encoding='utf-8') as file:
            keys_data = yaml.safe_load(file)
            return keys_data['database']

    @staticmethod
    def get_api_key(path_keys):
        with open(path_keys, 'r', encoding='utf-8') as file:
            keys_data = yaml.safe_load(file)
            return keys_data['api_key'], keys_data['prompt'], keys_data['bot_token']

    @staticmethod
    def update_users_table(db_access_key, user_request):
        user_id = user_request['user_id']
        tg_channel = user_request['tg_channel']
        key_words = user_request['key_words']
        stop_words = user_request['stop_words']

        key_words_str = ', '.join(key_words)
        stop_words_str = ', '.join(stop_words)

        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = f"""INSERT INTO Users_table (id, tg_channel, key_words, stop_words)
VALUES ({user_id}, '{tg_channel}', '{key_words_str}', '{stop_words_str}') 
ON DUPLICATE KEY UPDATE tg_channel = VALUES(tg_channel), key_words = VALUES(key_words), stop_words = VALUES(stop_words);"""

            with connection.cursor() as cursor:
                cursor.execute(request)
                connection.commit()

    @staticmethod
    def get_sent_urls(db_access_key, user_request):
        with connect(
                host=db_access_key['host'],
                port=db_access_key['port'],
                user=db_access_key['user'],
                password=db_access_key['password'],
                database=db_access_key['database']
        ) as connection:
            request = f"select sent_urls from Users_table where id = {user_request['user_id']}"
            with connection.cursor() as cursor:
                cursor.execute(request)
                sent_urls = cursor.fetchone()[0].split(', ')
                for sent_url in sent_urls:
                    if sent_url:
                        user_request['sent_urls'].append(sent_url)
