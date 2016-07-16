import json
import logging
from os import environ

from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

from oranglecloud_client import URL_API
from oranglecloud_client.folders import Folders
from oranglecloud_client.freespace import Freespace
from oranglecloud_client.files import Files

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
    """"
    Implementation of the OAUTH2 client according to the recommendations here: https://developer.orange.com/apis/cloud-france/api-reference
    """

    SCOPES = ['openid', 'cloud']

    def __init__(self, client_id, client_secret, redirect_uri):
        proxies = dict(http=environ.get('HTTP_PROXY', ''), https=environ.get('HTTPS_PROXY', ''))
        # some certificates such as netatmo are invalid
        super(ApiManager, self).__init__(
            ServiceInformation(
                '%s/oauth/v2/authorize' % URL_API,
                '%s/oauth/v2/token' % URL_API,
                client_id=client_id,
                client_secret=client_secret,
                scopes=ApiManager.SCOPES,
                skip_ssl_verifications=False),
            proxies)
        self.folders = Folders(self)
        self.freespace = Freespace(self)
        self.files = Files(self)
        self.redirect_uri = redirect_uri
