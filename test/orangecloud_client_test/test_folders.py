import httplib
import unittest

import mock

from orangecloud_client_test.fake_requests import mock_api_response
from orangecloud_client.folders import Folders


class FoldersTest(unittest.TestCase):
    def setUp(self):
        self.client = mock.MagicMock()
        self.folders = Folders(self.client)

    def test_delete(self):
        self.client.delete.return_value = mock_api_response('/folders/folder-id',
                                                            httplib.NO_CONTENT,
                                                            None)
        self.folders.delete('folder-id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_get_root(self):
        self.client.get.return_value = mock_api_response('/folders',
                                                         httplib.OK,
                                                         None,
                                                         'folders', 'GET_response.json')
        root = self.folders.get()
        self.client.get.assert_called_with(self.client.get.return_value.url, params=None)
        self.assertIsNotNone(root)
        self.assertEqual('root-id', root.id)
        self.assertEqual('root', root.name)
        self.assertEqual(1, len(root.files))
        self.assertEqual('file-root', root.files[0].id)
        self.assertEqual(1, len(root.subfolders))
        self.assertEqual('first_folder', root.subfolders[0].id)
        self.assertEqual('root-id', root.subfolders[0].parentId)

    def test_get_folder(self):
        self.client.get.return_value = mock_api_response('/folders/folder-id',
                                                         httplib.OK,
                                                         None,
                                                         'folders', 'GET_{id}_response.json')
        folder = self.folders.get('folder-id')
        self.client.get.assert_called_with(self.client.get.return_value.url, params=None)
        self.assertIsNotNone(folder)
        self.assertEqual('folder-id', folder.id)
        self.assertEqual('folder-name', folder.name)
        self.assertEqual('root-id', folder.parentId)
        self.assertEqual(1, len(folder.files))
        self.assertEqual('file-id', folder.files[0].id)
        self.assertEqual(1, len(folder.subfolders))
        self.assertEqual('subfolder-id', folder.subfolders[0].id)
        self.assertEqual('folder-id', folder.subfolders[0].parentId)

    def test_create(self):
        self.client.post.return_value = mock_api_response('/folders',
                                                          httplib.OK,
                                                          None,
                                                          'folders', 'POST_response.json')
        folder = self.folders.create('name', 'parent-id')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(parentFolderId='parent-id', name='name'))
        self.assertIsNotNone(folder)
        self.assertEqual('folder-id', folder.id)
        self.assertEqual('folder-name', folder.name)
        self.assertEqual('parent-id', folder.parentId)
        self.assertEqual(0, len(folder.files))
        self.assertEqual(0, len(folder.subfolders))

    def test_copy(self):
        self.client.post.return_value = mock_api_response('/folders/folder-id',
                                                          httplib.OK,
                                                          None,
                                                          'folders', 'POST_{id}_copy_response.json')
        response_file = self.folders.copy('folder-id', 'new-parent-id')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(parentFolderId='new-parent-id', clone=True))
        self.assertEqual('new-folder-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)

    def test_move(self):
        self.client.post.return_value = mock_api_response('/folders/folder-id',
                                                          httplib.OK,
                                                          None,
                                                          'folders', 'POST_{id}_move_response.json')
        response_file = self.folders.move('folder-id', 'new-parent-id')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(parentFolderId='new-parent-id'))
        self.assertEqual('folder-id', response_file.id)
        self.assertEqual('name', response_file.name)
        self.assertEqual('new-parent-id', response_file.parentId)

    def test_rename(self):
        self.client.post.return_value = mock_api_response('/folders/folder-id',
                                                          httplib.OK,
                                                          None,
                                                          'folders', 'POST_{id}_rename_response.json')
        response_file = self.folders.rename('folder-id', 'new-name')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(name='new-name'))
        self.assertEqual('folder-id', response_file.id)
        self.assertEqual('new-name', response_file.name)
        self.assertEqual('parent-id', response_file.parentId)
