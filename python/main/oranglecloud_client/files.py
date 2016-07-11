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
