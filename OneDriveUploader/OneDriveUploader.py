import config
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk.helpers.resource_discovery import ResourceDiscoveryRequest

def main():
    redirect_uri = config.urls['redirect']
    client_id = config.client['id']
    client_secret = config.client['secret']
    discovery_uri = config.urls['discovery']
    auth_server_url = config.urls['auth_server']
    auth_token_url = config.urls['auth_token']

    http = onedrivesdk.HttpProvider()
    auth = onedrivesdk.AuthProvider(http,
                                    client_id,
                                    auth_server_url=auth_server_url,
                                    auth_token_url=auth_token_url)
    auth_url = auth.get_auth_url(redirect_uri)
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
    auth.authenticate(code, redirect_uri, client_secret, resource=discovery_uri)
    # If you have access to more than one service, you'll need to decide
    # which ServiceInfo to use instead of just using the first one, as below.
    service_info = ResourceDiscoveryRequest().get_service_info(auth.access_token)[0]
    auth.redeem_refresh_token(service_info.service_resource_id)
    client = onedrivesdk.OneDriveClient(service_info.service_resource_id + '/_api/v2.0/', auth, http)
  
if __name__== "__main__":
  main()