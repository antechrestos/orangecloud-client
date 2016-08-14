import unittest

from oranglecloud_client.commands.shell.parser import parse_line, InvalidSynthax


class TestParser(unittest.TestCase):
    def test_simple_command(self):
        command, parameters = parse_line('cd somewhere')
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere', parameters[0])

    def test_quoted_space(self):
        command, parameters = parse_line('cd somewhere\ else')
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere else', parameters[0])

    def test_quoted_command(self):
        command, parameters = parse_line('cd "somewhere else"')
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere else', parameters[0])

    def test_escaped_quote_command(self):
        command, parameters = parse_line('cd somewhere\\"escaped')
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere"escaped', parameters[0])

    def test_quoted_and_escaped_quote_command(self):
        command, parameters = parse_line('cd "somewhere \\"escaped "')
        self.assertIsInstance(parameters, tuple)
        self.assertEqual(1, len(parameters))
        self.assertEqual('cd', command)
        self.assertEqual('somewhere "escaped ', parameters[0])

    def test_bad_quoted_command(self):
        self.assertRaises(InvalidSynthax, parse_line, 'cd "somewhere \\"')