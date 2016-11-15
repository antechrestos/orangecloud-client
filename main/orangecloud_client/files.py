import errno
import httplib
import json
import os
from mimetypes import guess_type

from requests.exceptions import ConnectionError
from requests.packages.urllib3.exceptions import ProtocolError
from requests_toolbelt.multipart.encoder import MultipartEncoder

from orangecloud_client import URL_UPLOAD, BASE_URI
from orangecloud_client.abstract_domain import AbstractDomain
from orangecloud_client.error_handling import ClientError


class Files(AbstractDomain):

    def __init__(self, client):
        super(Files, self).__init__(client, 'files')

    def get(self, file_id):
        self._debug('get - %s', file_id)
        response = self._get('/files/%s' % file_id)
        self._debug('get - %s - %s', file_id, response.text)
        return AbstractDomain._read_response(response)

    def delete(self, file_id):
        self._debug('delete - %s', file_id)
        self._delete('/files/%s' % file_id)

    def move(self, file_id, destination_folder_id):
        self._debug('move - %s => %s', file_id, destination_folder_id)
        response = self._post('/files/%s' % file_id, dict(parentFolderId=destination_folder_id))
        self._debug('move - %s - %s', file_id, response.text)
        return AbstractDomain._read_response(response)

    def rename(self, file_id, new_name):
        self._debug('rename - %s => %s', file_id, new_name)
        response = self._post('/files/%s' % file_id, dict(name=new_name))
        self._debug('rename - %s - %s', file_id, response.text)
        return AbstractDomain._read_response(response)

    def copy(self, file_id, destination_folder_id):
        self._debug('copy - %s => %s', file_id, destination_folder_id)
        response = self._post('/files/%s' % file_id,
                              dict(parentFolderId=destination_folder_id, clone=True))
        self._debug('copy - %s - %s', file_id, response.text)
        return AbstractDomain._read_response(response)

    def download(self, download_url, destination_path):
        with open(destination_path, 'wb') as f:
            self._debug('download - %s', os.path.basename(destination_path))
            response = self._call(self.client.get, download_url, stream=True)
            for chunk in response:
                f.write(chunk)

    def upload(self, file_path, folder_id=None):
        mime_type, _ = guess_type(file_path)
        mime_type = 'application/octet-stream' if mime_type is None else mime_type
        file_name = os.path.basename(file_path)
        self._debug('upload - %s(%s) => %s', file_name, mime_type,
                    folder_id if folder_id is not None else 'root')
        file_stats = os.stat(file_path)
        file_name_encoded = unicode(file_name, "utf-8", errors="ignore")
        description = dict(name=file_name_encoded, size=str(file_stats.st_size))
        if folder_id is not None:
            description['folder'] = folder_id

        def send():
            with open(file_path, 'rb') as f:
                uri = '/files/content'
                m = MultipartEncoder(
                    fields=dict(description=json.dumps(dict(description)),
                                file=(file_name_encoded, f, mime_type))
                )
                response = self._call(self.client.post, '%s%s%s' % (URL_UPLOAD, BASE_URI, uri),
                                      data=m,
                                      headers={'Content-Type': m.content_type})
                self._debug('upload - %s - %s', file_name, response.text)
                return AbstractDomain._read_response(response)

        try:
            return send()
        except ClientError, ex:
            if Files._is_token_expired_on_upload(ex.response):
                self._logger.info('upload  - token invalid - refreshing token')
                self.client._refresh_token()
                send()
            else:
                raise
        except ConnectionError, conn:
            if len(conn.args) == 1 and type(conn.args[0]) == ProtocolError :
                protocol_error = conn.args[0]
                if len(protocol_error.args) == 2:
                    str_error, error = protocol_error.args
                    if error.errno == errno.ECONNRESET:
                        self._logger.info('upload  - connection reset - refreshing token')
                        self.client._refresh_token()
                        self._logger.info('upload  - resending the payload')
                        return send()
            raise
        except BaseException, ex:
            self._logger.error('upload - unmanaged exception - %s', type(ex))

    @staticmethod
    def _is_token_expired_on_upload(response):
        if response.status_code == httplib.UNAUTHORIZED:
            try:
                json_data = response.json()
                error = json_data.get('error')
                # {"error":{"code":"PDK_RP_0004","label":"INVALID_TOKEN","details":"OIDC rejected the token"}}
                return error is not None and error.get('label') == 'INVALID_TOKEN'
            except:
                return False
        else:
            return False
