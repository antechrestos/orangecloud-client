import httplib
import unittest
from os import path
from json import loads
from requests_toolbelt.multipart.encoder import MultipartEncoder
from orangecloud_client_test.mock_api import MockClient
from oranglecloud_client.files import Files
from mock import create_autospec, mock


class MockFile(object):
    def __init__(self):
        self.buffer = []

    def write(self, s):
        self.buffer.append(s)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return False


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
        response_file = self.files.copy('file-id', 'new-parent-id', )
        self.assertEqual('new-file-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)

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
        mock_response = self.client.mock_upload('/files/content', httplib.CREATED,
                                                response_payload_path=('files', 'POST_response.json'))
        file_name = 'upload.jpg'
        mime_type = 'image/jpeg'
        file_path = path.join(path.dirname(__file__), '..', 'fixtures', 'files', file_name)
        folder_id = 'folder-id'

        def check_data(data, _, **kwargs):
            headers = kwargs.get('headers', None)
            self.assertIsNotNone(headers)
            self.assertIn('multipart/form-data; ', headers.get('Content-Type', None))
            self.assertIsInstance(data, MultipartEncoder)
            self.assertIsNotNone(data.fields)
            self.assertIn('description', data.fields)
            self.assertIn('file', data.fields)
            description = loads(data.fields['description'])
            file_sent = data.fields['file']
            self.assertIsInstance(description, dict)
            self.assertIsInstance(file_sent, tuple)
            self.assertEqual(description.get('name', None), file_name)
            self.assertEqual(description.get('folder', None), folder_id)
            self.assertEqual(len(file_sent), 3)
            self.assertEqual(file_sent[0], file_name)
            self.assertEqual(file_sent[2], mime_type)

        mock_response.check_data = check_data
        response_file = self.files.upload(file_path, folder_id)
        self.assertEqual('file-id', response_file.fileId)
        self.assertEqual('file-name', response_file.fileName)

    def test_download(self):

        url_download = 'http://some-url-for-dowload/som-path/file'
        mock_response = self.client.mock_download(url_download, httplib.OK,
                                                  response_payload_path=('files', 'download.txt'))

        def check_data(data, json, **kwargs):
            self.assertIn('stream', kwargs)
            self.assertTrue(kwargs['stream'])

        mock_response.check_data = check_data

        @mock.patch('__builtin__.open', spec=open, return_value=MockFile())
        def fire_test(mock_open):
            self.files.download(url_download, 'somewhere.txt')
            self.assertEqual(''.join(mock_open.return_value.buffer), 'Some data downloaded')

        fire_test()
