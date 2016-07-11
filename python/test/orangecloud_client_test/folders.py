
import httplib
import unittest

from orangecloud_client_test.mock_api import MockClient
from oranglecloud_client.folders import Folders


class FoldersTest(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self.assertEqual)
        self.folders = Folders(self.client)

    def test_delete(self):
        self.client.mock_delete('/folders/folder-id', httplib.NO_CONTENT)
        self.folders.delete('folder-id')

    def test_get_root(self):
        self.client.mock_get('/folders', None, httplib.OK, ('folders', 'GET_response.json'))
        root = self.folders.get()
        self.assertIsNotNone(root)
        self.assertEqual('root-id', root.id)
        self.assertEqual('root', root.name)
        self.assertEqual(1, len(root.files))
        self.assertEqual('file-root', root.files[0].id)
        self.assertEqual(1, len(root.subFolders))
        self.assertEqual('first_folder', root.subFolders[0].id)
        self.assertEqual('root-id', root.subFolders[0].parentId)

    def test_get_folder(self):
        self.client.mock_get('/folders/folder-id', None, httplib.OK,
                             response_payload_path=('folders', 'GET_{id}_response.json'))
        folder = self.folders.get('folder-id')
        self.assertIsNotNone(folder)
        self.assertEqual('folder-id', folder.id)
        self.assertEqual('folder-name', folder.name)
        self.assertEqual('root-id', folder.parentId)
        self.assertEqual(1, len(folder.files))
        self.assertEqual('file-id', folder.files[0].id)
        self.assertEqual(1, len(folder.subFolders))
        self.assertEqual('subfolder-id', folder.subFolders[0].id)
        self.assertEqual('folder-id', folder.subFolders[0].parentId)

    def test_create(self):
        self.client.mock_post('/folders', httplib.OK,
                              request_payload_path=('folders', 'POST_request.json'),
                              response_payload_path=('folders', 'POST_response.json'))
        folder = self.folders.create('name', 'parent-id')
        self.assertIsNotNone(folder)
        self.assertEqual('folder-id', folder.id)
        self.assertEqual('folder-name', folder.name)
        self.assertEqual('parent-id', folder.parentId)
        self.assertEqual(0, len(folder.files))
        self.assertEqual(0, len(folder.subFolders))
