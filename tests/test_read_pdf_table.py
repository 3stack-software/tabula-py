import json
import unittest

import tabula


class TestReadPdfTable(unittest.TestCase):
    def assertJsonEquals(self, expected_json, json_data):
        with open(expected_json) as json_file:
            data = json.load(json_file)
            self.assertEqual(json_data, data)

    def test_read_pdf_into_json(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_json = 'tests/resources/data_1.json'
        json_data = tabula.read_pdf(pdf_path, guess=True, stream=True)
        self.assertTrue(isinstance(json_data, list))
        self.assertJsonEquals(expected_json, json_data)

    def test_read_pdf_with_java_option(self):
        pdf_path = 'tests/resources/data.pdf'
        expected_json = 'tests/resources/data_1.json'
        json_data = tabula.read_pdf(pdf_path, guess=True, stream=True, pages=1, java_options=['-Xmx256m'])
        self.assertTrue(isinstance(json_data, list))
        self.assertJsonEquals(expected_json, json_data)

if __name__ == '__main__':
    unittest.main()
