import logging
import time

from requests.exceptions import ConnectionError

from orangecloud_client import URL_API, BASE_URI
from orangecloud_client.error_handling import raise_error, raise_response_error


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsonObject, self).__init__(*args, **kwargs)
        self.__dict__ = self


class AbstractDomain(object):
    MAX_RETRY = 10

    SLEEP_BEFORE_RETRY = 5

    def __init__(self, client, domain_name):
        self.client = client
        self.domain_name = domain_name
        self._logger = logging.getLogger('orangecloud_client.%s' % domain_name)

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
        number_retry = 0
        while True:
            try:
                response = method(url, **kwargs)
                return self._check_response(response, url)
            except ConnectionError, ex:
                number_retry += 1
                if number_retry > AbstractDomain.MAX_RETRY:
                    raise
                else:
                    self._logger.warning('%s - retrying in %d sec', str(ex), AbstractDomain.SLEEP_BEFORE_RETRY)
                    time.sleep(AbstractDomain.SLEEP_BEFORE_RETRY)

    def _check_response(self, response, uri):
        if response.status_code >= 300:
            raise_response_error(response, self.domain_name, 'Invalid status code %d on %s', response.status_code, uri)
        else:
            return response

    @staticmethod
    def _read_response(response):
        return response.json(object_pairs_hook=lambda pairs: JsonObject(pairs))
