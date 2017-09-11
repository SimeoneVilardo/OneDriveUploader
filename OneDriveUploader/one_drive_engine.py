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
    def get_dir_components(self, path):
        return os.path.normpath(path).split(os.path.sep)

    '''
    Ottiene una lista di stringhe che contiene tutte le cartelle contenute nella cartella specificata nel parametro path.
    ATTENZIONE: La ricerca avviene su tutti i livelli, partendo dal livello più esterno specificato nel parametro path
    e proseguendo fino alla cartella più interna.
    '''
    def get_all_dirs(self, path):
        dirs = list()
        for root, subdirs, files in os.walk(path):
            dirs.append(root)
        return dirs

    '''
    Ottiene un oggetto di tipo cartella da OneDrive il cui id corrisponde all'id specificato nel parametro id.
    '''
    def get_folder_by_id(self, id):
        return self.client.item(drive='me', id=id)

    '''
    Ottiene l'oggetto di tipo cartella da OneDrive il cui id è root.
    '''
    def get_root_folder(self):
        return self.get_folder_by_id('root')

    '''
    Ottiene un oggetto di tipo cartella da OneDrive dato il nome della cartella da trovare ed eventualmente
    un oggetto di tipo cartella da cui partire (nel caso non sia specificato sarà utilizzato l'oggetto root).
    ATTENZIONE: Questa funzione analizza solo un livello, che può essere il root o quello diversamente specificato
    dal parametro start_folder. Il parametro start_folder deve essere un oggetto di tipo cartella.
    '''
    def get_folder_by_dirname(self, dir_name, start_folder=None):
        current_folder = start_folder if start_folder != None else self.get_root_folder()
        if current_folder.children != None:
            for item in current_folder.children.get():
                if item.folder != None and dir_name == item.name:
                    return self.get_folder_by_id(item.id)
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
    def get_folder_by_path(self, folder_path, start_folder=None):
        current_folder = start_folder if start_folder != None else self.get_root_folder()
        dir_components = self.get_dir_components(folder_path)
        while len(dir_components) > 0:
            temp_folder = self.get_folder_by_dirname(dir_components[0], current_folder)
            if temp_folder == None:
                return (False, current_folder, dir_components)
            current_folder = temp_folder
            dir_components.pop(0)
        return (True, current_folder, None)


    '''
    Crea un oggetto di tipo cartella il cui valore della proprietà name è quello specificato nel parametro name
    e lo inserisce tra gli oggetti figli dell'oggetto specificato nel parametro parent.
    Il dato ritornato è l'oggetto di tipo cartella appena inserito.
    '''
    def create_folder_by_name(self, parent, name):
        f = onedrivesdk.Folder()
        i = onedrivesdk.Item()
        i.name = name
        i.folder = f
        new_folder = parent.children.add(i)
        return self.get_folder_by_id(new_folder.id)

    '''
    Crea l'intera struttura ad albero delle cartelle partendo dalla cartella specificata nel parametro dir_path all'interno
    della root o eventualmente all'interno dell'oggetto di tipo cartella specificato nel parametro start_folder.
    '''
    def create_folder_structure(self, dir_path, start_folder_path=None):
        start_folder = self.get_folder_by_path(start_folder_path) if start_folder_path != None else self.get_root_folder()
        for root, subdirs, files in os.walk(dir_path):
            current_folder_path = root.replace(dir_path, '')[1:] if len(root.replace(dir_path, '')) > 0 else None
            current_folder = self.get_folder_by_path(current_folder_path, start_folder)[1] if current_folder_path != None else self.get_root_folder() #Controllare che self.get_folder_by_path(current_folder_path, start_folder)[0] sia True
            for subdir in subdirs:
                self.create_folder_by_name(current_folder, subdir)
                
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


    def upload_file(self, path):
        folders = self.get_folders_from_path(path)
        filename = os.path.basename(path)
        client.item(drive='me', id='root').children[file_info[1]].upload(file_info[0])