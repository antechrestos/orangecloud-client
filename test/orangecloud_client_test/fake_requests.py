import httplib
import os
from json import loads

from orangecloud_client import URL_API, URL_UPLOAD, BASE_URI


class MockResponse(object):
    def __init__(self, url, status_code, text, headers=None):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers = dict()
        self.is_redirect = status_code == httplib.SEE_OTHER
        if headers is not None:
            self.headers.update(headers)

    def check_data(self, data, json, **kwargs):
        pass

    def json(self, **kwargs):
        return loads(self.text, **kwargs)

    def __iter__(self):
        for b in self.text:
            yield b


def mock_response(url, status_code, headers, *path_parts):
    if len(path_parts) > 0:
        file_name = path_parts[len(path_parts) - 1]
        extension_idx = file_name.rfind('.')
        binary_file = extension_idx >= 0 and file_name[extension_idx:] == '.bin'
        with(open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', *path_parts),
                  'rb' if binary_file else 'r')) as f:
            return MockResponse(url=url,
                                status_code=status_code,
                                text=f.read(),
                                headers=headers)
    else:
        return MockResponse(url=url,
                            status_code=status_code,
                            text='')


def mock_api_response(uri, status_code, headers, *path_parts):
    return mock_response('%s%s%s' % (URL_API, BASE_URI, uri), status_code, headers, *path_parts)


def mock_upload_response(uri, status_code, headers, *path_parts):
    return mock_response('%s%s%s' % (URL_UPLOAD, BASE_URI, uri), status_code, headers, *path_parts)
