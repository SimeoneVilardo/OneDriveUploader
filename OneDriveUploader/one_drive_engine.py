import os
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk.helpers.resource_discovery import ResourceDiscoveryRequest

class OneDriveEngine():
    client = None
    def login_business(self, redirect_uri, client_id, client_secret, discovery_uri, auth_server_url, auth_token_url):
        http = onedrivesdk.HttpProvider()
        auth = onedrivesdk.AuthProvider(http,
                                        client_id,
                                        auth_server_url=auth_server_url,
                                        auth_token_url=auth_token_url)
        auth_url = auth.get_auth_url(redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
        auth.authenticate(code, redirect_uri, client_secret, resource=discovery_uri)
        services = ResourceDiscoveryRequest().get_service_info(auth.access_token)
        if len(services) == 0:
            print('No service avaible. A bad thing. Really. Call Vilardo now!')
        else:
            service_info = ResourceDiscoveryRequest().get_service_info(auth.access_token)[0]
            auth.redeem_refresh_token(service_info.service_resource_id)
            client = onedrivesdk.OneDriveClient(service_info.service_resource_id + '/_api/v2.0/', auth, http)
            self.client = client

    def login(self, redirect_uri, client_id, client_secret):
        scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
        client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)
        auth_url = client.auth_provider.get_auth_url(redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
        client.auth_provider.authenticate(code, redirect_uri, client_secret)
        self.client = client

    def create_dir_structure(self, path):
        for root, subdirs, files in os.walk(path):
            self.create_dir(root)
    
    def create_dir(self, path, current_od_folder=None):
        if current_od_folder == None:
            current_od_folder = self.client.item(drive='me', id='root')
        folders = os.path.normpath(path).split(os.path.sep)[1:]
        if len(folders) == 0:
            return
        else:
            if(current_od_folder.children != None):
                exists = False
                for od_item in current_od_folder.children.get():
                    if od_item.folder != None and folders[0] == od_item.name:        
                        exists = True
                        current_od_folder = self.client.item(drive='me', id=od_item.id)
                        break
            if not exists:
                f = onedrivesdk.Folder()
                i = onedrivesdk.Item()
                i.name = folders[0]
                i.folder = f
                returned_item = current_od_folder.children.add(i)
                current_od_folder = self.client.item(drive='me', id=returned_item.id)
            path = path.replace('\\' + folders[0], '')
            self.create_dir(path, current_od_folder)