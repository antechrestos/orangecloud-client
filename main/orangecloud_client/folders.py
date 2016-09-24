from orangecloud_client.abstract_domain import AbstractDomain


class Folders(AbstractDomain):
    def __init__(self, client):
        super(Folders, self).__init__(client, 'folders')

    def get(self, folder_id=None, **kwargs):
        folder_name = folder_id if folder_id is not None else 'root'
        self._debug('get - %s', folder_name)
        parameters = None if len(kwargs) == 0 else kwargs
        if folder_id is None:
            response = self._get('/folders', params=parameters)
        else:
            response = self._get('/folders/%s' % folder_id, params=parameters)
        self._debug('get - %s - %s', folder_name, response.text)
        return AbstractDomain._read_response(response)

    def delete(self, folder_id):
        self._debug('delete - %s', folder_id)
        self._delete('/folders/%s' % folder_id)

    def create(self, name, parent_id=None):
        self._debug('create - %s => %s', name, parent_id if parent_id is not None else 'root')
        data = dict(name=name)
        if parent_id is not None:
            data['parentFolderId'] = parent_id
        response = self._post('/folders', data)
        self._debug('create - %s - %s', name, response.text)
        return AbstractDomain._read_response(response)

    def move(self, folder_id, destination_folder_id):
        self._debug('move - %s => %s', folder_id, destination_folder_id)
        response = self._post('/folders/%s' % folder_id, dict(parentFolderId=destination_folder_id))
        self._debug('move - %s - %s', folder_id, response.text)
        return AbstractDomain._read_response(response)

    def rename(self, folder_id, new_name):
        self._debug('rename - %s => %s', folder_id, new_name)
        response = self._post('/folders/%s' % folder_id, dict(name=new_name))
        self._debug('rename - %s - %s', folder_id, response.text)
        return AbstractDomain._read_response(response)

    def copy(self, folder_id, destination_folder_id):
        self._debug('copy - %s => %s', folder_id, destination_folder_id)
        response = self._post('/folders/%s' % folder_id,
                              dict(parentFolderId=destination_folder_id, clone=True))
        self._debug('copy - %s - %s', folder_id, response.text)
        return AbstractDomain._read_response(response)