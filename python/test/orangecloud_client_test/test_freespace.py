import httplib
import unittest

import mock

from orangecloud_client_test.fake_requests import mock_api_response
from oranglecloud_client.freespace import Freespace


class FreespaceTest(unittest.TestCase):
    def setUp(self):
        self.client = mock.MagicMock()
        self.freespace = Freespace(self.client)

    def test_freespace_succeed(self):
        self.client.get.return_value = mock_api_response('/freespace',
                                                         httplib.OK,
                                                         None,
                                                         'freespace', 'GET_response.json')
        freespace = self.freespace.get()
        self.client.get.assert_called_with(self.client.get.return_value.url, params=None)
        self.assertIsNotNone(freespace)
        self.assertEqual(1024, freespace.freespace)