import unittest

from orangecloud_client.api import ApiManager


class ApiManagerTest(unittest.TestCase):
    def setUp(self):
        self.api = ApiManager('client_id', 'client_secret', 'redirect uri')

    def test_folders(self):
        self.assertIsNotNone(self.api.folders)

    def test_freespace(self):
        self.assertIsNotNone(self.api.freespace)

    def test_files(self):
        self.assertIsNotNone(self.api.files)
