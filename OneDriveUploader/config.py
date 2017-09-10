from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(find_dotenv())

client = dict(id = '8dfcc6ca-304f-4351-a2c9-299e72eb8605')

urls = dict(redirect = 'http://localhost:8080',
    discovery = 'https://api.office.com/discovery/',
    auth_server = 'https://login.microsoftonline.com/common/oauth2/authorize',
    auth_token = 'https://login.microsoftonline.com/common/oauth2/token')