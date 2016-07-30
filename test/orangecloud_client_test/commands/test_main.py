import os
import sys
import unittest

import mock

import oranglecloud_client.commands.main as main
from oranglecloud_client.abstract_domain import JsonObject


class TestMain(unittest.TestCase):
    MOCK_FILE = JsonObject(name='test-file-name', downloadUrl='somewhere.org/file')

    @mock.patch.object(sys, 'argv', ['main', 'freespace'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_freespace(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.freespace.get.assert_called_with()

    @mock.patch.object(sys, 'argv', ['main', 'shell'])
    @mock.patch('oranglecloud_client.commands.main.shell')
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_shell(self, mock_client_loader, fake_shell):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_shell.assert_called_with(fake_client)

    @mock.patch.object(sys, 'argv', ['main', 'mkdir', '-name', 'test-name', '-parent_id', 'test-parent'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_mkdir_with_parent(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.folders.create.assert_called_with('test-name', 'test-parent')

    @mock.patch.object(sys, 'argv', ['main', 'mkdir', '-name', 'test-name'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_mkdir_without_parent(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.folders.create.assert_called_with('test-name', None)

    @mock.patch.object(sys, 'argv', ['main', 'mkdir'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_mkdir_invalid_without_name(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        self.assertRaises(SystemExit, main.main)
        fake_client.folders.create.assert_not_called()

    @mock.patch.object(sys, 'argv', ['mockmain', 'ls', 'test-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_ls_file(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.files.get.assert_called_with('test-id')

    @mock.patch.object(sys, 'argv', ['main', 'ls', '-r', 'test-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_ls_directory(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.folders.get.assert_called_with('test-id')

    @mock.patch.object(sys, 'argv', ['main', 'ls', '-r'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_ls_invalid_without_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        self.assertRaises(SystemExit, main.main)
        fake_client.folders.get.assert_not_called()

    @mock.patch.object(sys, 'argv', ['maifake_clientn', 'rm', 'test-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_rm_file(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.files.delete.assert_called_with('test-id')

    @mock.patch.object(sys, 'argv', ['main', 'rm', '-r', 'test-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_rm_directory(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.folders.delete.assert_called_with('test-id')

    @mock.patch.object(sys, 'argv', ['main', 'rm', '-r'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_rm_invalid_without_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        self.assertRaises(SystemExit, main.main)
        fake_client.folders.delete.assert_not_called()

    @mock.patch.object(sys, 'argv', ['main', 'upload', 'test-path-file'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_upload_no_parent_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.files.upload.assert_called_with('test-path-file', None)

    @mock.patch.object(sys, 'argv', ['main', 'upload', '-folder', 'test-folder-id', 'test-path-file'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_upload_with_parent_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        main.main()
        fake_client.files.upload.assert_called_with('test-path-file', 'test-folder-id')

    @mock.patch.object(sys, 'argv', ['main', 'upload', '-folder', 'test-folder-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_upload_invalid_without_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        self.assertRaises(SystemExit, main.main)
        fake_client.files.upload.assert_not_called()

    @mock.patch.object(sys, 'argv', ['main', 'download', 'test-file-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_download_no_output_dir(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        fake_client.files.get.return_value = JsonObject(name='test-file-name', downloadUrl='somewhere.org/file')
        main.main()
        fake_client.files.get.assert_called_with('test-file-id')
        fake_client.files.download.assert_called_with('somewhere.org/file',
                                                      os.path.join(os.path.curdir, 'test-file-name'))

    @mock.patch.object(sys, 'argv', ['main', 'download', '-output_dir', 'a/path/to/store/the/file', 'test-file-id'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_download_with_output_dir(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        fake_client.files.get.return_value = JsonObject(name='test-file-name', downloadUrl='somewhere.org/file')
        main.main()
        fake_client.files.get.assert_called_with('test-file-id')
        fake_client.files.download.assert_called_with('somewhere.org/file',
                                                      os.path.join('a/path/to/store/the/file', 'test-file-name'))

    @mock.patch.object(sys, 'argv', ['main', 'download', '-output_dir', 'a/path/to/store/the/file'])
    @mock.patch('oranglecloud_client.commands.main.load_client')
    def test_download_invalid_without_id(self, mock_client_loader):
        fake_client = self._configure_mock_client(mock_client_loader)
        self.assertRaises(SystemExit, main.main)
        fake_client.files.download.assert_not_called()

    @staticmethod
    def _configure_mock_client(mock_client_loader):
        fake_client = mock_client_loader()
        fake_client.__enter__.return_value = fake_client
        return fake_client
