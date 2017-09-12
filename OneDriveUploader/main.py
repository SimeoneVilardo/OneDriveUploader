import config
import os
from enums import Login
from one_drive_engine import OneDriveEngine

def main():
    od_engine = OneDriveEngine()
    login_mode = None
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    while login_mode == None or (int(login_mode) != Login.CONSUMER.value and int(login_mode) != Login.BUSINESS.value):
        print('*** Menu Login ***')
        print(str(Login.CONSUMER.value) + ' - Consumer')
        print(str(Login.BUSINESS.value) + ' - Business')
        login_mode = input('Login mode: ')
    if int(login_mode) == Login.CONSUMER.value:
        logged = od_engine.login(config.urls['redirect'], config.client['id'], CLIENT_SECRET)
    elif int(login_mode) == Login.BUSINESS.value:
        logged = od_engine.login_business(config.urls['redirect'], config.client['id'], CLIENT_SECRET, config.urls['discovery'], config.urls['auth_server'], config.urls['auth_token'])
    print('Login completed') if logged == True else print('Login failed')
    input_path = input('Path: ')
    od_engine.create_folder_structure(input_path)
    print('Tree structure created')
  
if __name__ == "__main__":
  main()