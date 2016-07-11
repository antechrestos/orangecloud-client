import httplib
import unittest
from oranglecloud_client import URL_UPLOAD, BASE_URI
from orangecloud_client_test.fake_requests import MockResponse
from orangecloud_client_test.mock_api import MockClient
from oranglecloud_client.files import Files


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self.assertEqual)
        self.files = Files(self.client)

    def test_delete(self):
        self.client.mock_delete('/files/file-id', httplib.NO_CONTENT)
        self.files.delete('file-id')

    def test_get(self):
        self.client.mock_get('/files/response_file-id', None, httplib.OK,
                             response_payload_path=('files', 'GET_{id}_response.json'))
        response_file = self.files.get('response_file-id')
        self.assertIsNotNone(response_file)
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('file-name', response_file.name)
        self.assertEqual(0, response_file.size)
        self.assertEqual("http://somewhere.org", response_file.downloadUrl)

    def test_copy(self):
        self.client.mock_post('/files/file-id', httplib.OK,
                              request_payload_path=('files', 'POST_{id}_copy_request.json'),
                              response_payload_path=('files', 'POST_{id}_copy_response.json'))
        response_file = self.files.copy('file-id', 'new-name', 'new-parent-id')
        self.assertEqual('new-file-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('new-parent-id', response_file.parentId)

    def test_move(self):
        self.client.mock_post('/files/file-id', httplib.OK,
                              request_payload_path=('files', 'POST_{id}_move_request.json'),
                              response_payload_path=('files', 'POST_{id}_move_response.json'))
        response_file = self.files.move('file-id', 'new-parent-id')
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('name', response_file.name)
        self.assertEqual('new-parent-id', response_file.parentId)

    def test_rename(self):
        self.client.mock_post('/files/file-id', httplib.OK,
                              request_payload_path=('files', 'POST_{id}_rename_request.json'),
                              response_payload_path=('files', 'POST_{id}_rename_response.json'))
        response_file = self.files.rename('file-id', 'new-name')
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)

    def test_upload(self):
        response = MockResponse('%s%s' % (URL_UPLOAD, BASE_URI), status_code, response_payload)


        return , MockClient._append_params(uri_path, params))
