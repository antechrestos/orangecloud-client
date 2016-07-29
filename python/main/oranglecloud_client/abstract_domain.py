import json
import logging

from oranglecloud_client import URL_API, BASE_URI
from oranglecloud_client.error_handling import raise_error, raise_response_error


class JsonObject(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            super(JsonObject, self).__init__(**kwargs)
        else:
            super(JsonObject, self).__init__(seq)
        self.__dict__ = self

    def json(self):
        return json.dumps(self)


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
        self._logger.debug(msg, *args)

    @staticmethod
    def _build_uri(uri):
        return '%s%s%s' % (URL_API, BASE_URI, uri)

    def _get(self, uri, params=None, **kwargs):
        kwargs['params'] = params
        return self._call(self.client.get, AbstractDomain._build_uri(uri), **kwargs)

    def _post(self, uri, json=None, **kwargs):
        kwargs['json'] = json
        return self._call(self.client.post, AbstractDomain._build_uri(uri), **kwargs)

    def _delete(self, uri):
        return self._call(self.client.delete, AbstractDomain._build_uri(uri))

    def _call(self, method, url, **kwargs):
        response = method(url, **kwargs)
        return self._check_response(response, url)

    def _check_response(self, response, uri):
        if response.status_code >= 300:
            raise_response_error(response, self.domain_name, 'Invalid status code %d on %s', response.status_code, uri)
        else:
            return response

    @staticmethod
    def _read_response(response):
        return response.json(object_pairs_hook=lambda pairs: JsonObject(pairs))
