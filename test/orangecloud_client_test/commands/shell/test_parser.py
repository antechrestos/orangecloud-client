import unittest

from oranglecloud_client.commands.shell.parser import parse_line


class TestParser(unittest.TestCase):
    def test_simple_command(self):
        command, parameters = parse_line('cd somewhere')
        self.assertIsNotNone(command)
        self.assertIsNotNone(parameters)
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere', parameters[0])

    def test_escaped_commands(self):
        pass
