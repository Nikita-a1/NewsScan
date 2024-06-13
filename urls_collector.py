import yaml

PATH = 'config.yml'  # specify the path for the file

try:  # try to open the yaml file
    with open(PATH, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    print("Can't find the file. Check the path.")

urls_list = []  # create a list of URLS


class UrlsCollector:  # collect all links from websites
    @staticmethod
    def all_urls():
        for el in data['webs']:
            urls_list.append(el)

    @staticmethod  # check links for duplicate links available in the database
    def urls_duplicate_check():
        for el in urls_list:
            pass

    @staticmethod  # record unique links in the database
    def urls_record():
        pass
