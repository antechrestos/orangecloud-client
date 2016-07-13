from oranglecloud_client.abstract_domain import AbstractDomain


class Folders(AbstractDomain):
    def __init__(self, client):
        super(Folders, self).__init__(client, 'folders')

    def get(self, folder_id=None, filtered_params=None):
        folder_name = folder_id if folder_id is not None else 'root'
        self._debug('get - %s', folder_name)
        if folder_id is None:
            response = self._get('/folders', filtered_params)
        else:
            response = self._get('/folders/%s' % folder_id, filtered_params)
        self._debug('get - %s - %s', folder_name, response.text)
        return AbstractDomain._read_response(response)

    def delete(self, folder_id):
        self._debug('delete - %s')
        self._delete('/folders/%s' % folder_id)

    def create(self, name, parent_id=None):
        self._debug('create - %s => %s', name, parent_id if parent_id is not None else 'root')
        data = dict(name=name)
        if parent_id is not None:
            data['parentFolderId'] = parent_id
        response = self._post('/folders', data)
        self._debug('create - %s - %s', name, response.text)
        return AbstractDomain._read_response(response)
