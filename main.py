import yaml

PATH = 'config.yml'

try:
    with open(PATH, 'r') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    print("Can't find the file. Check the path.")

user_id = data['user_id']
webs = data['webs']
key_words = data['key_words']
stop_words = data['stop_words']
frequency = data['frequency']