
import httplib
import unittest

from orangecloud_client_test.mock_api import MockClient
from oranglecloud_client.freespace import Freespace


class FreespaceTest(unittest.TestCase):
    def setUp(self):
        self.client = MockClient(self.assertEqual)
        self.freespace = Freespace(self.client)

    def test_freespace_succeed(self):
        self.client.mock_get('/freespace', None, httplib.OK, ('freespace', 'GET_response.json'))
        freespace = self.freespace.get()
        self.assertIsNotNone(freespace)
        self.assertEqual(1024, freespace.freespace)