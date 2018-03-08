import configparser
import os.path

_base_dir = '/data/'
_config_file = os.path.join(_base_dir, 'miss_spsu.ini')

config = configparser.ConfigParser()
with open(_config_file) as f:
    config.read_file(f)

NUMBERS_FILE = os.path.join(_base_dir, config['files']['numbers_file'])
GIRLS_FILE = os.path.join(_base_dir, config['files']['girls_file'])

SECRET = config['app']['secret']
ADMIN_KEY = config['app']['admin_password']

TIMEOUT = config.getint('timeout','timeout')
TIMEOUT_IP = config.getint('timeout', 'timeout_ip')

DEBUG = config.getboolean('app', 'debug')
