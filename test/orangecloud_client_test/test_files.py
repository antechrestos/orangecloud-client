import httplib
import unittest
from os import path

import mock
from mock import mock

from orangecloud_client_test.fake_requests import mock_api_response, mock_upload_response, mock_response
from orangecloud_client.files import Files


class MockFile(object):
    def __init__(self):
        self.buffer = []

    def write(self, s):
        self.buffer.append(s)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def encode(self):
        return None


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.client = mock.MagicMock()
        self.files = Files(self.client)

    def test_delete(self):
        self.client.delete.return_value = mock_api_response('/files/file-id',
                                                            httplib.NO_CONTENT,
                                                            None)
        self.files.delete('file-id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_get(self):
        self.client.get.return_value = mock_api_response('/files/response_file-id',
                                                         httplib.OK,
                                                         None,
                                                         'files', 'GET_{id}_response.json')

        response_file = self.files.get('response_file-id')
        self.client.get.assert_called_with(self.client.get.return_value.url, params=None)
        self.assertIsNotNone(response_file)
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('file-name', response_file.name)
        self.assertEqual(0, response_file.size)
        self.assertEqual("http://somewhere.org", response_file.downloadUrl)

    def test_copy(self):
        self.client.post.return_value = mock_api_response('/files/file-id',
                                                          httplib.OK,
                                                          None,
                                                          'files', 'POST_{id}_copy_response.json')

        response_file = self.files.copy('file-id', 'new-parent-id')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(parentFolderId='new-parent-id', clone=True))
        self.assertEqual('new-file-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)

    def test_move(self):
        self.client.post.return_value = mock_api_response('/files/file-id',
                                                          httplib.OK,
                                                          None,
                                                          'files', 'POST_{id}_move_response.json')

        response_file = self.files.move('file-id', 'new-parent-id')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(parentFolderId='new-parent-id'))
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('name', response_file.name)
        self.assertEqual('new-parent-id', response_file.parentId)

    def test_rename(self):
        self.client.post.return_value = mock_api_response('/files/file-id',
                                                          httplib.OK,
                                                          None,
                                                          'files', 'POST_{id}_rename_response.json')

        response_file = self.files.rename('file-id', 'new-name')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(name='new-name'))
        self.assertEqual('file-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)

    def test_upload(self):
        self.client.post.return_value = mock_upload_response('/files/content',
                                                             httplib.CREATED,
                                                             None,
                                                             'files', 'POST_response.json')
        file_name = 'upload.jpg'
        file_path = path.join(path.dirname(__file__), '..', 'fixtures', 'files', file_name)
        folder_id = 'folder-id'

        @mock.patch('orangecloud_client.files.guess_type', return_value=('image/jpeg', 'binary'))
        @mock.patch('__builtin__.open', spec=open, return_value=MockFile())
        @mock.patch('orangecloud_client.files.MultipartEncoder', return_value=mock.Mock())
        def fire_test(mock_multipart_encoder, mock_open, _):
            data = mock_multipart_encoder()
            data.content_type = 'upload content type'
            response_file = self.files.upload(file_path, folder_id)
            self.client.post.assert_called_with(self.client.post.return_value.url,
                                                data=data,
                                                headers={'Content-Type': data.content_type})
            self.assertEqual('file-id', response_file.fileId)
            self.assertEqual('file-name', response_file.fileName)

        fire_test()

    def test_download(self):
        url_download = 'http://some-url-for-dowload/som-path/file'
        self.client.get.return_value = mock_response('http://some-url-for-dowload/som-path/file',
                                                     httplib.OK,
                                                     None,
                                                     'files', 'download.txt')

        def check_data(data, json, **kwargs):
            self.assertIn('stream', kwargs)
            self.assertTrue(kwargs['stream'])

        mock_response.check_data = check_data

        @mock.patch('__builtin__.open', spec=open, return_value=MockFile())
        def fire_test(mock_open):
            self.files.download(url_download, 'somewhere.txt')
            self.client.get.assert_called_with(self.client.get.return_value.url,
                                               stream=True)
            self.assertEqual(''.join(mock_open.return_value.buffer), 'Some data downloaded')

        fire_test()
