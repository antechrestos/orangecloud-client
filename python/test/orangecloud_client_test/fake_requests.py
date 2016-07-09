import json
import httplib


class MockResponse(object):
    def __init__(self, url, status_code, text, headers=None):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers = dict()
        self.is_redirect = status_code == httplib.SEE_OTHER
        if headers is not None:
            self.headers.update(headers)

    def check_data(self, **kwargs):
        pass

    def json(self):
        return json.loads(self.text)


class MockSession(object):
    def __init__(self, real_session):
        self._get = dict()
        self._post = dict()
        self._inner_session = real_session

    def mock_get(self, url, status_code, text, headers=None, check_data_callback=None):
        self._get[url] = MockSession._build_response(url, status_code, text, headers, check_data_callback)

    def mock_post(self, url, status_code, text, headers=None, check_data_callback=None):
        self._post[url] = MockSession._build_response(url, status_code, text, headers, check_data_callback)

    def get(self, url, **kwargs):
        return MockSession._handle_mock('get', self._get, url, **kwargs)

    def post(self, url, **kwargs):
        return MockSession._handle_mock('post', self._post, url, **kwargs)

    @staticmethod
    def _build_response(url, status_code, text, headers=None, check_data_callback=None):
        response = MockResponse(url, status_code, text, headers)
        if check_data_callback is not None:
            response.check_data = check_data_callback
        return response

    @staticmethod
    def _handle_mock(method, mocked_data, url, **kwargs):
        idx_params = url.find('?')
        mocked_response = mocked_data.get(url[:idx_params] if idx_params != -1 else url, None)
        if mocked_response is None:
            raise Exception('Not mocked: %s - %s - %s' % (method, url, str(kwargs)))
        else:
            mocked_response.check_data(**kwargs)
            return mocked_response
