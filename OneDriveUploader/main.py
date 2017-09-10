import config
import config_secrets
from enums import Login
from one_drive_engine import OneDriveEngine

def main():
    od_engine = OneDriveEngine()
    login_mode = None
    while login_mode == None or (int(login_mode) != Login.CONSUMER.value and int(login_mode) != Login.BUSINESS.value):
        print('*** Menu Login ***')
        print(str(Login.CONSUMER.value) + ' - Consumer')
        print(str(Login.BUSINESS.value) + ' - Business')
        login_mode = input('Login mode: ')
    if int(login_mode) == Login.CONSUMER.value:
        od_engine.login(config.urls['redirect'], config.client['id'], config_secrets.client['secret'])
    elif int(login_mode) == Login.BUSINESS.value:
        od_engine.login_business(config.urls['redirect'], config.client['id'], config_secrets.client['secret'], config.urls['discovery'], config.urls['auth_server'], config.urls['auth_token'])
    print('Login completed')
    input_path = input('Path: ')
    od_engine.create_dir_structure(input_path)
    print('Tree structure created')
  
if __name__ == "__main__":
  main()