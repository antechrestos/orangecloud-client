from orangecloud_client.abstract_domain import AbstractDomain


class Freespace(AbstractDomain):
    def __init__(self, client):
        super(Freespace, self).__init__(client, 'freespace')

    def get(self):
        self._debug('get')
        response = self._get('/freespace')
        self._debug('freespace - %s', response.text)
        return AbstractDomain._read_response(response)
