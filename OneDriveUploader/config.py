from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(find_dotenv())

client = dict(id = 'e2767e53-fc10-405d-9f95-b7ab04fd2f13')

urls = dict(redirect = 'http://localhost:8081',
    discovery = 'https://api.office.com/discovery/',
    auth_server = 'https://login.microsoftonline.com/common/oauth2/authorize',
    auth_token = 'https://login.microsoftonline.com/common/oauth2/token')