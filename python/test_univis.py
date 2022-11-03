import unittest
from unittest import mock
import univis
from urllib.parse import urlparse, parse_qs


def mocked_univis_response(*args, **kwargs):
    """
    Return a mocked response from the UnivIS API.

    :param args:   The args to pass to the requests.get function.
    :param kwargs: The kwargs to pass to the requests.get function.
    """
    class MockResponse:
        def __init__(self, url, text, status_code):
            self.text = text
            self.status_code = status_code
            self.url = url

    client_req = urlparse(args[0])

    if client_req.path == '/':
        options = ''.join([f'<option value="{s}">{s}s</option>' for s in ['2023s', '2022w', '2022s']])
        return MockResponse(args[0], f'<html><body><select name="semto">{options}</select></body></html>', 200)

    query = parse_qs(client_req.query)
    if query['search'][0] in ['thesis']:
        return MockResponse(
            args[0],
            f'<html><body><h1>Server Error: 500 FATAL ERROR: Database {query["search"][0].capitalize()} not found, '
            f'dbpath was /univis/nt/db:/univis/nt/db/{query["sem"][0]}</h1></body></html>',
            500
        )
    if not query['sem'][0][0].isdigit():
        return MockResponse(
            args[0],
            f'<html><body>{"<td></td>"*40}<td><b>UnivIS error, command \'search\':</b><br>semester must contain '
            f'a year </td></body></html>',
            200
        )
    if not query['sem'][0].endswith(('s', 'w')):
        return MockResponse(
            args[0],
            f'<html><body>{"<td></td>"*40}<td><b>UnivIS error, command \'search\':</b><br>semester must contain '
            f'season code </td></body></html>',
            200
        )
    if 'name' not in query or query['name'][0] == '^':
        return MockResponse(
            args[0],
            f'<html><body>{"<td></td>"*40}<td><b>UnivIS error, command \'search\':</b><br>please narrow your '
            f'search!</td></body></html>',
            200
        )
    return MockResponse(
        args[0],
        '<?xml version="1.0"?>\n<!DOCTYPE UnivIS SYSTEM "http://univis.uni-kiel.de/univis.dtd">\n<UnivIS '
        'version="1.6" semester="2022s" organisation="CAU Kiel">\n</UnivIS>\n',
        200
    )


def mocked_search(*args, **kwargs):
    pass


class TestUnivIS(unittest.TestCase):
    def test_base_url(self):
        self.assertEqual(univis.UnivIS().base_url,
                         'https://univis.uni-kiel.de/')
        self.assertEqual(univis.UnivIS('http', 'test.univis.uni-kiel.de').base_url,
                         'http://test.univis.uni-kiel.de/')
        self.assertEqual(univis.UnivIS(host='test.univis.uni-kiel.de').base_url,
                         'https://test.univis.uni-kiel.de/')

    @mock.patch('requests.get', side_effect=mocked_univis_response)
    def test_search(self, mock_get):
        self.assertEqual(
            univis.UnivIS().search(search_type=univis.SearchType.LECTURES, name='test', sem='2022s'),
            {'UnivIS': {'@version': '1.6', '@semester': '2022s', '@organisation': 'CAU Kiel'}})
        self.assertIn(mock.call(
                'https://univis.uni-kiel.de/prg?show=xml&noimports=1&search=lectures&name=test&sem=2022s'),
            mock_get.call_args_list)
        # Test Exceptions
        with self.assertRaises(univis.UnivISInvalidDatabaseException):
            univis.UnivIS().search(search_type=univis.SearchType.THESIS, name='test', sem='2022s')
        with self.assertRaises(univis.UnivISInvalidSemesterException):
            univis.UnivIS().search(search_type=univis.SearchType.LECTURES, name='test', sem='2022')
        with self.assertRaises(univis.UnivISInvalidSemesterException):
            univis.UnivIS().search(search_type=univis.SearchType.LECTURES, name='test', sem='test')
        with self.assertRaises(univis.UnivISException):
            univis.UnivIS().search(search_type=univis.SearchType.LECTURES, sem='2022w')

    @mock.patch('requests.get', side_effect=mocked_univis_response)
    def test_get_all_semesters(self, mock_get):
        self.assertEqual(set(univis.UnivIS().get_all_semesters()), {'2022s', '2022w', '2023s'})
        self.assertIn(mock.call('https://univis.uni-kiel.de/'), mock_get.call_args_list)

    @mock.patch('requests.get', side_effect=mocked_univis_response)
    @mock.patch('time.sleep')
    def test_find_all(self, mock_sleep, mock_get):
        self.assertEqual(univis.UnivIS().find_all(
            search_types=[univis.SearchType.LECTURES, univis.SearchType.THESIS],
            semesters=['2022s', 'test', '2023s'],
            search_terms=['test', 'test2', ''],
            sleep_freq=(42, 0)
        ), {'2022s': {}, '2023s': {}})
        # 3 for each valid semester, 1 for the invalid semester and 1 for the invalid database = 8 calls
        self.assertEqual(8, mock_get.call_count, 'there should be only 8 api calls')
        self.assertIn(mock.call(42), mock_sleep.call_args_list, 'sleep should be called with 42')
        self.assertEqual(8, mock_sleep.call_count, 'sleep should be called before every search)')


if __name__ == '__main__':
    unittest.main()
