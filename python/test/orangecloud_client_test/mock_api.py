from json import dumps
from os import path

from oranglecloud_client import URL_SERVICE
from .fake_requests import MockResponse


class MockClient(object):
    def __init__(self, assert_equal):
        self._get = {}
        self._post = {}
        self._delete = {}
        self._delete = {}
        self.assert_equal = assert_equal

    @staticmethod
    def _append_params(uri_path, params):
        if params is None:
            return uri_path
        else:
            query = '&'.join(['%s=%s' % (k, v) for k, v in params.items()]) if params is not None else None
            return '%s?%s' % (uri_path, query)

    @staticmethod
    def _generate_url(uri_path, params=None):
        return '%s%s' % (URL_SERVICE, MockClient._append_params(uri_path, params))

    def mock_delete(self, uri_path, status_code):
        response = MockResponse(MockClient._generate_url(uri_path), status_code, None)
        self._delete[response.url] = response

    def mock_get(self, uri_path, params, status_code, response_payload_path):
        with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as f:
            response = MockResponse(MockClient._generate_url(uri_path, params), status_code, f.read())
            self._get[response.url] = response

    def mock_post(self, uri_path, status_code, request_payload_path, response_payload_path):
        request_payload = None
        response_payload = None
        if request_payload_path is not None:
            with open(path.join(path.dirname(__file__), '..', 'fixtures', *request_payload_path), 'r') as f:
                request_payload = f.read()
        if response_payload_path is not None:
            with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as f:
                response_payload = f.read()
        response = MockResponse(MockClient._generate_url(uri_path), status_code, response_payload)

        def check_data(data):
            if request_payload is None:
                self.assert_equal(request_payload, data)

        response.check_data = check_data
        self._post[response.url] = response

    def delete(self, url):
        return self._delete[url]

    def get(self, url, params):
        return self._get[MockClient._append_params(url, params)]

    def post(self, url, data=None, json=None):
        if json is not None:
            data = dumps(json)
        response = self._post[url]
        response.check_data(data)
        return response
