import yaml
from yaml import Loader

with open('.github/workflows/config.yml') as f:
    print(yaml.load(f, Loader=Loader))
