import os
import platform
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk.helpers.resource_discovery import ResourceDiscoveryRequest

class OneDriveEngine():

    client = None


    '''
    Ottiene una lista di stringhe che contiene tutte le cartelle che formano il percorso del parametro path.
    '''
    def get_path_components(self, path):
        return [x for x in os.path.normpath(path).split(os.path.sep) if x != ''] if path else []


    def get_basename(self, path):
        return os.path.basename(path).replace(os.path.sep, '')


    def get_common_path(self, path1, path2):
        common_path = ''
        path1_len = len(path1)
        path2_len = len(path2)
        for i in range(path1_len if path1_len >= path1_len else path2_len):
            if path1[i] == path2[i]:
                common_path = common_path + path1[i]
            else:
                break
        return common_path
              

    def get_diff_paths(self, path1, path2, root_path=''):
        if path1[-1] == os.path.sep:
            path1 = path1[:-1]
        if path2[-1] == os.path.sep:
            path2 = path2[:-1]
        path1 = path1.replace(root_path, '')
        path2 = path2.replace(root_path, '')
        common_path = self.get_common_path(path1, path2)
        path1 = path1.replace(common_path, '')
        path2 = path2.replace(common_path, '')
        path1_depth = len(self.get_path_components(path1))
        path2_depth = len(self.get_path_components(path2))
        if path1_depth == path2_depth:
            return (0, '', 0)
        elif path1_depth > path2_depth:
            path_diff = path1.replace(path2, '')
            return (1, path_diff, len(self.get_path_components(path_diff)))
        elif path2_depth > path1_depth:
            path_diff = path2.replace(path1, '')
            return (2, path_diff, len(self.get_path_components(path_diff)))


    '''
    Ottiene una lista di stringhe che contiene tutte le cartelle contenute nella cartella specificata nel parametro path.
    ATTENZIONE: La ricerca avviene su tutti i livelli, partendo dal livello più esterno specificato nel parametro path
    e proseguendo fino alla cartella più interna.
    '''
    def get_all_dirs(self, path):
        return [root for root, subdirs, files in os.walk(path)]


    '''
    Ottiene un oggetto di tipo cartella da OneDrive il cui id corrisponde all'id specificato nel parametro id.
    '''
    def get_object_by_id(self, id, drive='me'):
        return self.client.item(drive=drive, id=id)


    '''
    Ottiene l'oggetto di tipo cartella da OneDrive il cui id è root.
    '''
    def get_root_folder(self):
        return self.get_object_by_id('root')


    '''
    Ottiene un oggetto di tipo cartella da OneDrive dato il nome della cartella da trovare ed eventualmente
    un oggetto di tipo cartella da cui partire (nel caso non sia specificato sarà utilizzato l'oggetto root).
    ATTENZIONE: Questa funzione analizza solo un livello, che può essere il root o quello diversamente specificato
    dal parametro start_folder. Il parametro start_folder deve essere un oggetto di tipo cartella.
    '''
    def get_folder_by_name(self, name, start_folder=None):
        current_folder = start_folder if start_folder != None else self.get_root_folder()
        if current_folder.children != None:
            for item in current_folder.children.get():
                if item.folder != None and name == item.name:
                    return self.get_object_by_id(item.id)
        return None


    '''
    Ottiene un oggetto di tipo cartella da OneDrive dato il path della cartella da trovare ed eventualmente
    un oggetto di tipo cartella da cui partire (nel caso non sia specificato sarà utilizzato l'oggetto root).
    ATTENZIONE: Il dato ritornato non è un oggetto di tipo cartella, ma una tupla contente tre elementi:
    1) Valore booleano, se impostato a True significa che il secondo oggetto della tupla è l'oggetto di tipo
    cartella cercato, se invece è impostato a False significa che il secondo oggetto della tupla è il primo
    oggetto di tipo cartella di livello superiore a quello cercato.
    2) Oggetto, è l'oggetto di tipo cartella recuperato da OneDrive. Il suo significato dipende dal valore
    booleano del primo elemento della tupla.
    3) Lista di stringhe, è la sequenza di cartelle che NON sono state trovate, quindi non esistono su OneDrive.
    '''
    def get_folder_by_path(self, path, start_folder=None):
        current_folder = start_folder if start_folder != None else self.get_root_folder()
        path_components = self.get_path_components(path)
        while len(path_components) > 0:
            temp_folder = self.get_folder_by_name(path_components[0], current_folder)
            if temp_folder == None:
                return (False, current_folder, path_components)
            current_folder = temp_folder
            path_components.pop(0)
        return (True, current_folder, None)


    '''
    Crea un oggetto di tipo cartella il cui valore della proprietà name è quello specificato nel parametro name
    e lo inserisce tra gli oggetti figli dell'oggetto specificato nel parametro parent.
    Il dato ritornato è l'oggetto di tipo cartella appena inserito.
    '''
    def create_folder_by_name(self, name, parent=None, ignore_exists=True):
        parent = parent if parent != None else self.get_root_folder()
        if (not ignore_exists) and self.get_folder_by_name(name, parent) != None:
            raise Exception('Folder already exists and overwrite flag is set to false.')
        f = onedrivesdk.Folder()
        i = onedrivesdk.Item()
        i.name = name
        i.folder = f
        new_folder = parent.children.add(i)
        return self.get_object_by_id(new_folder.id)


    def create_folder_by_path(self, path, start_folder=None, ignore_exists=True):
        current_folder = start_folder if start_folder != None else self.get_root_folder()
        path_components = self.get_path_components(path)
        created = False
        for folder_name in path_components:
            current_folder_temp = self.get_folder_by_name(folder_name, current_folder) # creato allo scopo di non far eseguire il codice due volte nella prossima riga
            if folder_name == path_components[-1]:
                if current_folder_temp != None:
                    current_folder = current_folder_temp
                    created = False
                    if not ignore_exists:
                        raise Exception('Folder already exists and overwrite flag is set to false.')
                else:
                    current_folder = self.create_folder_by_name(folder_name, current_folder)
                    created = True
        return [created, current_folder]


    '''
    Crea l'intera struttura ad albero delle cartelle partendo dalla cartella specificata nel parametro dir_path all'interno
    della root o eventualmente all'interno dell'oggetto di tipo cartella specificato nel parametro start_folder.
    '''
    def create_folder_structure(self, dir_path, start_folder_path=None, ignore_exists=True):
        current_folder = self.get_folder_by_path(start_folder_path) if start_folder_path != None else self.get_root_folder()
        folders_cache = list()
        all_dirs = self.get_all_dirs(dir_path)
        current_folder_path = all_dirs[0]
        folder_name = self.get_basename(current_folder_path)
        current_folder = self.create_folder_by_name(folder_name, current_folder, ignore_exists)
        all_dirs = all_dirs[1:]
        for i in range(len(all_dirs)):
            folder_name = self.get_basename(all_dirs[i])
            self.create_folder_by_name(folder_name, current_folder, ignore_exists)
            if i < len(all_dirs)-1:
                path_diff = self.get_diff_paths(current_folder_path, all_dirs[i+1], dir_path)
                if path_diff[0] == 2 and path_diff[2] > 1:
                    current_folder_path = all_dirs[i]
                    folders_cache.append(current_folder)
                    current_folder = self.get_folder_by_name(folder_name, current_folder)
                elif path_diff[0] == 0:
                    current_folder_path = current_folder_path.replace(os.path.sep + self.get_path_components(current_folder_path)[-1], '')
                    current_folder = folders_cache[-1]
                    folders_cache = folders_cache[:-1]
                elif path_diff[0] == 1 and path_diff[2] > 1:
                    current_folder_path = current_folder_path.replace(path_diff[1], '')
                    current_folder = folders_cache[-path_diff[2]]
                    folders_cache = folders_cache[:-path_diff[2]]
               
                 
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
        for service in services:
            if service.service_id == 'O365_SHAREPOINT':    
                auth.redeem_refresh_token(service.service_resource_id)
                client = onedrivesdk.OneDriveClient(service.service_resource_id + '/_api/v2.0/', auth, http)
                self.client = client
                return True
        return False                


    def login(self, redirect_uri, client_id, client_secret):
        scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
        client = onedrivesdk.get_default_client(client_id=client_id, scopes=scopes)
        auth_url = client.auth_provider.get_auth_url(redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
        client.auth_provider.authenticate(code, redirect_uri, client_secret)
        self.client = client
        return True


    def upload_file(self, path):
        folders = self.get_folders_from_path(path)
        filename = os.path.basename(path)
        client.item(drive='me', id='root').children[file_info[1]].upload(file_info[0])