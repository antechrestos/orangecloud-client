import os
import json
import sys
import stat
import random
import logging
from oauth2_client.credentials_manager import OAuthError
from orangecloud_client.api import ApiManager

_configuration_directory = os.path.join(os.path.expanduser('~'), '.orangecloud-client')
_configuration_file = os.path.join(_configuration_directory, 'configuration.json')


_logger = logging.getLogger(__name__)


class _CommandClient(ApiManager):
    def __init__(self, client_id, client_secret, redirect_uri):
        super(_CommandClient, self).__init__(client_id, client_secret, redirect_uri)

    def set_tokens(self, access_token, refresh_token):
        self.refresh_token = refresh_token
        self._init_session()
        self._set_access_token(access_token)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == OAuthError:
            _logger.error('OAuth error. Configuration will be erased')
            os.remove(_configuration_file)
        else:
            self.save_configuration()

    def save_configuration(self):
        with open(_configuration_file, 'w') as f:
            access_token = None
            if self._session is not None:
                authorization = self._session.headers.get('Authorization')
                if authorization is not None:
                    access_token = authorization[len('Bearer '):]
            configuration = dict(client_id=self.service_information.client_id,
                                 client_secret=self.service_information.client_secret,
                                 redirect_uri=self.redirect_uri)
            if self.refresh_token is not None:
                configuration['refresh_token'] = self.refresh_token
            if access_token is not None:
                configuration['access_token'] = access_token
            json.dump(configuration, f, indent=1)


def _init_oauth_process(client):
    url_to_open = client.init_authorize_code_process(client.redirect_uri, state=str(random.random()))
    _logger.warning('***** OPEN THIS URL IN YOUR BROWSER *****\n\t%s', url_to_open)
    code = client.wait_and_terminate_authorize_code_process()
    client.init_with_authorize_code(redirect_uri=client.redirect_uri, code=code)


def _init_client():
    global _configuration_directory

    def prompt(msg):
        sys.stdout.write('%s: ' % msg)
        response = sys.stdin.readline()
        return response.rstrip('\r\n')

    client_id = prompt('Client Id')
    client_secret = prompt('Client Secret')
    redirect_uri = prompt('Redirect Uri')
    if not os.path.exists(_configuration_directory):
        os.mkdir(_configuration_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    client = _CommandClient(client_id, client_secret, redirect_uri)
    _init_oauth_process(client)
    # save first time, meaning configuration works
    client.save_configuration()
    return client


def load_client():
    global _configuration_file
    try:
        with open(_configuration_file, 'r') as f:
            configuration = json.load(f)
            if type(configuration) is not dict:
                return _init_client()
            client_id = configuration.get('client_id')
            client_secret = configuration.get('client_secret')
            redirect_uri = configuration.get('redirect_uri')
            access_token = configuration.get('access_token')
            refresh_token = configuration.get('refresh_token')
            if client_id is None or client_secret is None or redirect_uri is None:
                return _init_client()
            result = _CommandClient(client_id, client_secret, redirect_uri)
            if refresh_token is not None:
                # do not accept access without refresh token
                if access_token is not None:
                    result.set_tokens(access_token, refresh_token)
                else:
                    result.init_with_token(refresh_token)
            else:
                _init_oauth_process(result)
            return result
    except IOError:
        return _init_client()
