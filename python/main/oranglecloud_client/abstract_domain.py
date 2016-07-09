import logging

from oranglecloud_client import URL_SERVICE
from oranglecloud_client.error_handling import raise_error, raise_response_error


class JsonObject(object):
    pass


class AbstractDomain(object):
    def __init__(self, client, domain_name):
        self.client = client
        self.domain_name = domain_name
        self._logger = logging.getLogger('oranglecloud_client.%s' % domain_name)

    def _raise_error(self, msg, *args):
        raise_error(self.domain_name, msg, *args)

    def _raise_response_error(self, response, msg, *args):
        raise_response_error(response, self.domain_name, msg, *args)

    def _debug(self, msg, *args):
        self._debug(msg, *args)

    def _get(self, uri, params=None):
        return self._call(self.client.get, '%s%s' % (URL_SERVICE, uri), params=params)

    def _post(self, uri, json=None):
        return self._call(self.client.post, '%s%s' % (URL_SERVICE, uri), json=json)

    def _delete(self, uri):
        return self._call(self.client.delete, '%s%s' % (URL_SERVICE, uri))

    def _call(self, method, path, **kwargs):
        response = method(path, **kwargs)
        return self._check_response(response, path)

    def _check_response(self, response, uri):
        if response.status_code >= 300:
            raise_response_error(response, self.domain_name, 'Invalid status code %d on %s', response.status_code, uri)
        else:
            return response

    @staticmethod
    def _read_response(response):
        def _json_hook(pairs):
            result = JsonObject()
            for k in pairs:
                result.__setattr__(k[0], k[1])
            return result

        return response.json(object_pairs_hook=_json_hook)
