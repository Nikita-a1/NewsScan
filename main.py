import yaml
import urls_collector

PATH = 'config.yml'  # specify the path for the file

try:  # try to open the yaml file
    with open(PATH, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    print("Can't find the file. Check the path.")

user_id = data['user_id']  # write data from the yml file to variables
webs = data['webs']
key_words = data['key_words']
stop_words = data['stop_words']
frequency = data['frequency']


urls_collector.UrlsCollector.all_urls()  # collect URLs from the main page of the site for subsequent parsing

