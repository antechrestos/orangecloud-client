import json
import logging
from os import environ

from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

_logger = logging.getLogger(__name__)


class InvalidStatusCode(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.body is None:
            return '%d' % self.status_code
        elif type(self.body) == str:
            return '%d : %s' % (self.status_code, self.body)
        else:
            return '%d : %s' % (self.status_code, json.dumps(self.body))


class ApiManager(CredentialManager):
    ''''
    Implementation of the OAUTH2 client according to the recommendations here: https://developer.orange.com/apis/cloud-france/api-reference
    '''
    URL_SERVICE = 'https://api.orange.com'

    SCOPES = ['openid', 'cloud']

    def __init__(self, client_id, client_secret):
        proxies = dict(http=environ.get('HTTP_PROXY', ''), https=environ.get('HTTPS_PROXY', ''))
        # some certificates such as netatmo are invalid
        super(ApiManager, self).__init__(
            ServiceInformation(
                '%s/oauth/v2/authorize' % ApiManager.URL_SERVICE,
                '%s/oauth/v2/token' % ApiManager.URL_SERVICE,
                client_id=client_id,
                client_secret=client_secret,
                scopes=ApiManager.SCOPES,
                skip_ssl_verifications=False),
            proxies)
