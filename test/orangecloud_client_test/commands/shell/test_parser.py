import unittest

from orangecloud_client.commands.shell.parser import parse_line, InvalidSynthax


class TestParser(unittest.TestCase):
    def test_simple_command(self):
        parameters = parse_line('cd somewhere')
        self.assertIsInstance(parameters, list)
        self.assertEqual(2, len(parameters))
        self.assertEqual('cd', parameters[0])
        self.assertEqual('somewhere', parameters[1])

    def test_quoted_space(self):
        parameters = parse_line('cd somewhere\ else')
        self.assertIsInstance(parameters, list)
        self.assertEqual(2, len(parameters))
        self.assertEqual('cd', parameters[0])
        self.assertEqual('somewhere else', parameters[1])

    def test_quoted_command(self):
        parameters = parse_line('cd "somewhere else"')
        self.assertIsInstance(parameters, list)
        self.assertEqual(2, len(parameters))
        self.assertEqual('cd', parameters[0])
        self.assertEqual('somewhere else', parameters[1])

    def test_escaped_quote_command(self):
        parameters = parse_line('cd somewhere\\"escaped')
        self.assertIsInstance(parameters, list)
        self.assertEqual(2, len(parameters))
        self.assertEqual('cd', parameters[0])
        self.assertEqual('somewhere"escaped', parameters[1])

    def test_quoted_and_escaped_quote_command(self):
        parameters = parse_line('cd "somewhere \\"escaped "')
        self.assertIsInstance(parameters, list)
        self.assertEqual(2, len(parameters))
        self.assertEqual('cd', parameters[0])
        self.assertEqual('somewhere "escaped ', parameters[1])

    def test_bad_quoted_command(self):
        self.assertRaises(InvalidSynthax, parse_line, 'cd "somewhere \\"')