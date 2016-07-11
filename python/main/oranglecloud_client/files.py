from mimetypes import guess_type
from os.path import basename

from oranglecloud_client import URL_UPLOAD, BASE_URI
from oranglecloud_client.abstract_domain import AbstractDomain


class Files(AbstractDomain):
    def __init__(self, client):
        super(Files, self).__init__(client, 'files')

    def get(self, file_id):
        response = self._get('/files/%s' % file_id)
        return AbstractDomain._read_response(response)

    def delete(self, file_id):
        self._delete('/files/%s' % file_id)

    def move(self, file_id, destination_folder_id):
        response = self._post('/files/%s' % file_id, dict(parentFolderId=destination_folder_id, clone=False))
        return AbstractDomain._read_response(response)

    def rename(self, file_id, new_name):
        response = self._post('/files/%s' % file_id, dict(name=new_name, clone=False))
        return AbstractDomain._read_response(response)

    def copy(self, file_id, new_name, destination_folder_id):
        response = self._post('/files/%s' % file_id,
                              dict(name=new_name, parentFolderId=destination_folder_id, clone=True))
        return AbstractDomain._read_response(response)

    def upload(self, file_path, folder_id=None):
        mime_type, _ = guess_type(file_path)
        file_name = basename(file_path)
        params = dict(name=file_name)
        if folder_id is not None:
            params['folder'] = folder_id
        with open(file_path, 'rb') as f:
            uri = '/files/content'
            response = self.client.post('%s%s%s' % (URL_UPLOAD, BASE_URI, uri),
                                        data=None,
                                        json=None,
                                        params=params,
                                        files=dict(file=(file_name, f,
                                                         'application/octet-stream' if mime_type is None
                                                         else mime_type)))
            return self._check_response(response, uri)
