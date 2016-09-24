from json import load
from os import path

from orangecloud_client import URL_API, URL_UPLOAD, BASE_URI
from .fake_requests import MockResponse


class MockClient(object):
    def __init__(self, compare_json):
        self._get = {}
        self._post = {}
        self._delete = {}
        self.compare_json = compare_json

    @staticmethod
    def _append_params(uri_path, params):
        if params is None:
            return uri_path
        else:
            query = '&'.join(['%s=%s' % (k, v) for k, v in params.items()]) if params is not None else None
            return '%s?%s' % (uri_path, query)

    @staticmethod
    def _generate_url(uri_path, params=None):
        return '%s%s%s' % (URL_API, BASE_URI, MockClient._append_params(uri_path, params))

    def mock_delete(self, uri_path, status_code):
        response = MockResponse(MockClient._generate_url(uri_path), status_code, None)
        self._delete[response.url] = response
        return response

    def mock_get(self, uri_path, params, status_code, response_payload_path):
        with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as f:
            response = MockResponse(MockClient._generate_url(uri_path, params), status_code, f.read())
            self._get[response.url] = response
            return response

    def mock_post(self, uri_path, status_code, request_payload_path, response_payload_path):
        with open(path.join(path.dirname(__file__), '..', 'fixtures', *request_payload_path), 'r') as request:
            request_payload = load(request)
            with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as response:
                response = MockResponse(MockClient._generate_url(uri_path), status_code, response.read())

                def check_data(_, json, **kwargs):
                    if request_payload is not None:
                        self.compare_json(request_payload, json)

                response.check_data = check_data
                self._post[response.url] = response
                return response

    def mock_upload(self, uri_path, status_code, response_payload_path):
        with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as f:
            response = MockResponse('%s%s%s' % (URL_UPLOAD, BASE_URI, uri_path), status_code, f.read())
            self._post[response.url] = response
            return response

    def mock_download(self, download_url, status_code, response_payload_path):
        with open(path.join(path.dirname(__file__), '..', 'fixtures', *response_payload_path), 'r') as f:
            response = MockResponse(download_url, status_code, f.read())
            self._get[response.url] = response
            return response

    def delete(self, url):
        return self._delete[url]

    def get(self, url, params=None, **kwargs):
        response = self._get[MockClient._append_params(url, params)]
        response.check_data(None, None, **kwargs)
        return response

    def post(self, url, data=None, json=None, **kwargs):
        response = self._post[url]
        response.check_data(data, json, **kwargs)
        return response
