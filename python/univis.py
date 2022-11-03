import base64
import json
import os
import numpy as np
import time
import requests as req
import xmltodict
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from enum import Enum
import re
import string
from typing import List, Dict, Any, Union, Tuple, Optional
import sqlalchemy
import textwrap

# A regex to check if a string is a real number
_is_number = re.compile(r"^\d*[.,]?\d*$")

# A regex to check if a string is an univis reference and to extract the reference type
_is_univisref = re.compile(r"\((.*)\|UnivISRef\)")


class UnivISException(Exception):
    """
    A custom exception to handle errors from the UnivIS API.
    """

    def __init__(self, message: str, url: str):
        """
        Initialize the exception.

        :param message: The message returned by the API.
        :param url:     The URL that was requested.
        """
        self.message = f'{message} ({url})'
        super().__init__(self.message)

    @classmethod
    def from_response(cls, response_text: str, response_url: str) -> 'UnivISException':
        """
        Return a UnivISException based on the response from the API.

        :param response_text: The text of the API response.
        :param response_url:  The url of the API response.
        :return:              The UnivISException.
        """
        soup = BeautifulSoup(response_text, 'html.parser')
        univis_h1 = soup.select('h1')
        if univis_h1:
            # Handles server errors (e.g. 500 - Database not found)
            univis_msg = univis_h1[0].text.split(':', 2)[-1].strip()
            return UnivISInvalidDatabaseException(univis_msg, response_url)
        # Handles UnivIS search errors
        univis_msg = soup.select('td')[40].text.split(':')[-1].strip()

        if univis_msg.startswith('semester'):
            return UnivISInvalidSemesterException(univis_msg, response_url)

        return cls(univis_msg, response_url)


class UnivISInvalidDatabaseException(UnivISException):
    """
    A custom exception to handle errors from the UnivIS API when the database is invalid.
    """
    pass


class UnivISInvalidSemesterException(UnivISException):
    """
    A custom exception to handle errors from the UnivIS API when the semester is invalid.
    """
    pass


class SearchType(Enum):
    """
    Valid UnivIS search values.
    """
    LECTURES = 'lectures'
    PERSONS = 'persons'
    CHAPTERS = 'chapters'
    DEPARTMENTS = 'departments'
    CALENDAR = 'calendar'
    ROOMS = 'rooms'
    ALLOCATIONS = 'allocations'
    PUBLICATIONS = 'publications'
    PROJECTS = 'projects'
    FUNCTIONS = 'functions'
    EVENTS = 'events'
    THESIS = 'thesis'
    ICONTACTS = 'icontacts'
    USERS = 'users'

    def __str__(self) -> str:
        return f'{self.value}'


def univis_to_sql(univis_instance: 'UnivIS', db: sqlalchemy.engine.Engine, verbose: bool = False):
    """
    Fetches all the data from the univis_instance and stores it in the database

    :param univis_instance: The univis instance to fetch the data from
    :param db:              An sqlalchemy engine
    :param verbose:         If True, print the progress
    """
    # Collects all data from the UnivIS instance and stores it in the database
    dfs = univis_instance.find_all(verbose=verbose)

    # Create all tables
    with db.connect() as con:
        for k, v in generate_sql_scheme(univis_instance.scheme).items():
            sql = f'CREATE TABLE IF NOT EXISTS `{k}` ( \n{textwrap.indent(v, " " * 4)} \n); \n'
            con.execute(sql)
            if verbose:
                print(f'Created empty table {k}')

    for table, df in dfs['all'].items():
        df.to_sql(name=table, con=db, if_exists='append', index=False)
        if verbose:
            print(f'Converted {table} to SQL')


def sqlize_dfs(dfs: Dict[str, pd.DataFrame],
               semester: str,
               scheme: Dict[str, Dict[str, Union[bool, str, List[str]]]]
               ) -> Dict[str, pd.DataFrame]:
    """
    Converts dataframes to a SQL-friendly format.

    :param dfs:      The dataframes to convert.
    :param semester: The semester to use.
    :param scheme:   The scheme of the univis.
    :return:         The SQL-friendly dataframes.
    """
    dfs_sql = {}
    new_tables = []
    for table_name, df in dfs.items():
        # Clones the dataframe to avoid changing the original one.
        df = df.copy()
        for col in df:
            # Add undocumented columns to the scheme
            if col not in scheme:
                scheme[col] = {
                    'is_list': False,
                    'is_ref': False,
                    'type': 'TEXT',
                    'attr': ['#PCDATA']
                }
                scheme[table_name]['attr'].append(col)

            # Update the type of the scheme:
            # If every element in the column is a number, the type must be a real number.
            # If none of those numbers includes a decimal point, the type must be an integer.
            if df[col].apply(lambda x: pd.isnull(x) or type(x) is str and bool(_is_number.match(x))).all():
                scheme[col]['type'] = 'REAL'
                if pd.to_numeric(df[col].fillna(0), errors='coerce').notnull().all():
                    scheme[col]['type'] = 'INTEGER'

            #  If every element in the column is a boolean, the type must be bool.
            elif df[col].isin(['ja', 'nein', 'anon', np.nan]).all():
                scheme[col]['type'] = 'BOOLEAN'

            elif scheme[col]['is_list']:
                for i in df.index:
                    cell = df.at[i, col]

                    # Skip nan values
                    if type(cell) is not dict:
                        continue

                    attr = scheme[col]['attr'][0]
                    tmp_cell = cell[attr]
                    # Convert the cell to a list if it is not one already.
                    if type(tmp_cell) is list:
                        new_cell = tmp_cell
                    else:
                        new_cell = [tmp_cell]

                    # Create new tables for the list if it does not exist.
                    if col not in dfs_sql:
                        dfs_sql[col] = pd.DataFrame()
                        new_tables += [col]

                    # Add the list items to the new table.
                    for elem in new_cell:
                        tmp = pd.DataFrame({'semester': [semester], '@key': [i]})
                        if not scheme[attr]['is_ref'] and type(elem) is dict:
                            for k, v in elem.items():
                                tmp[k] = [v]
                                if k not in scheme[attr]['attr']:
                                    scheme[attr]['attr'].append(k)
                        else:
                            tmp[attr] = [elem]
                        dfs_sql[col] = pd.concat([dfs_sql[col], tmp])
                df = df.drop(col, axis=1)  # Remove the list column from the table.
            else:
                is_ref = True
                for i in df.index:
                    cell = df.at[i, col]
                    if not (pd.isnull(cell) or type(cell) is dict and 'UnivISRef' in cell):
                        is_ref = False
                        break
                scheme[col]['is_ref'] = is_ref
            # Handle references.
            if scheme[col]['is_ref']:
                for i in df.index:
                    cell = df.at[i, col]
                    if type(cell) is dict:
                        df.at[i, col] = cell['UnivISRef']['@key']
                        scheme[col]['attr'] = [cell['UnivISRef']['@type']]
            # Convert the columns values to their type.
            match scheme[col]['type']:
                case 'BOOLEAN':
                    df[col] = df[col].map({'ja': True, 'nein': False, 'anon': None, np.nan: None})
                case 'REAL':
                    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), downcast='float')
                case 'INTEGER':
                    df[col] = pd.to_numeric(df[col].str.split(',', 1).str[0], downcast='integer')

        df['semester'] = semester
        # Reset index and only keep it if the index was set to '@key'.
        dfs_sql[table_name] = df.reset_index(level=0, drop=df.index.name != '@key')

    # Handle the newly created dataframes.
    if len(new_tables) > 0:
        tmp_dfs = {}
        for table_name in new_tables:
            tmp_dfs[table_name] = dfs_sql[table_name].reset_index(drop=True)
        tmp_dfs = sqlize_dfs(tmp_dfs, semester, scheme)
        for table_name in tmp_dfs:
            dfs_sql[table_name] = tmp_dfs[table_name]
    return dfs_sql


def generate_sql_scheme(scheme: Dict[str, Dict[str, Union[bool, str, List[str]]]]) -> Dict[str, str]:
    """
    Generate the SQL scheme from the UnivIS scheme.

    :param scheme: The UnivIS scheme.
    :return:       The SQL scheme for each table.
    """
    sql_scheme = {}
    ignore = []
    for table_name, data in scheme.items():
        values = data['attr']

        if table_name in ignore or values[0] in ['#PCDATA', 'EMPTY'] or data['is_ref']:
            continue

        if data['is_list']:
            list_elements = scheme[values[0]]['attr']
            ignore += [values[0]]
            if values[0] in sql_scheme:
                del sql_scheme[values[0]]
            if len(list_elements) > 1:
                values = list_elements

        table_scheme = f'`semester` VARCHAR(5) NOT NULL, \n' \
                       f'`@key` VARCHAR(255) NOT NULL, \n'
        table_constrains = ''
        for element in set(values):
            if element in ['semester', '@key']:
                continue
            if element not in scheme:
                table_scheme += f'`{element}` TEXT, \n'
                continue
            if scheme[element]['is_list']:
                continue
            if scheme[element]['is_ref']:
                table_scheme += f'`{element}` TEXT, \n'
                table_constrains += f'FOREIGN KEY (`{element}`) REFERENCES {scheme[element]["attr"][0]}(`@key`), \n'
            else:
                table_scheme += f'`{element}` {scheme[element]["type"]}, \n'
        sql_scheme[table_name] = f'{table_scheme}{table_constrains}'[: -3]
    return sql_scheme


class UnivIS:
    """
    A class to get data from UnivIS.
    """

    def __init__(self,
                 scheme: str = 'https',
                 host: str = 'univis.uni-kiel.de',
                 path: str = '/',
                 cache_path: Optional[str] = None):
        """
        Initialize a new UnivIS instance.

        :param scheme:     The scheme to use.
        :param host:       The hostname of the UnivIS instance.
        :param path:       The path to the UnivIS instance.
        :param cache_path: The path to the cache directory or None, if the cache is deactivated.
        """
        self.base_url = f'{scheme}://{host}{path}'
        self.scheme = self.get_database_scheme()
        self.cache = cache_path is not None
        if self.cache:
            self.cache_path = cache_path
            if not os.path.exists(self.cache_path):
                os.makedirs(self.cache_path, exist_ok=True)

    def search(self, search_type: SearchType, **kwargs: Any) -> Dict[str, Any]:
        """
        Send an API-request to UnivIS.

        :param search_type:      The search type to use.
        :param kwargs:           Any additional get-parameters to send to UnivIS.
        :return:                 A dictionary of the response from UnivIS.
        :raises UnivISException: If the search failed.
        """
        query = urllib.parse.urlencode({k: v for k, v in kwargs.items() if v})

        url = f'{self.base_url}prg?show=xml&noimports=1&search={search_type}&{query}'

        fp = None
        if self.cache:
            fn = base64.b64encode(url.encode('utf-8'), altchars=b'-_').decode()
            fp = f'{self.cache_path}{fn}.json'

        if not self.cache or self.cache and not os.path.exists(fp):
            raw = req.get(url).text
            if self.cache:
                with open(fp, 'w') as f:
                    json.dump(raw, f)
        else:
            with open(fp) as f:
                raw = json.load(f)

        # UnivIS returns an XML document, which is not valid XML. This is why we have to fix it.
        filtered = raw
        for c in ['&#x0C;', '&#x0B;']:
            filtered = filtered.replace(c, '')

        # If the API responds xml, return the parsed XML-response. Otherwise, raise an exception.
        if raw.startswith('<?xml'):
            return xmltodict.parse(filtered)
        raise UnivISException.from_response(raw, url)

    def get_all_semesters(self) -> List[str]:
        """
        Get all semesters of a UnivIS instance.

        :return: A list of all semester strings.
        """
        soup = BeautifulSoup(req.get(self.base_url).text, 'html.parser')
        dom_list = soup.select('select[name="semto"] option')
        return [dom.get('value') for dom in dom_list]

    def find_all(self,
                 search_types: List[SearchType] = None,
                 semesters: List[str] = None,
                 search_terms: Union[str, List[str]] = None,
                 sleep_freq: Tuple[int, int] = (1, 10),
                 sqlize: bool = True,
                 verbose: bool = False
                 ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Find all entries in UnivIS. **This is a very expensive operation.**

        :param search_types: The search types to use. If None, all search types are used.
        :param semesters:    The semesters to use. If None, all semesters are used.
        :param search_terms: The search terms to use. If None, `string.ascii_lowercase` and `string.digits` are used.
        :param sleep_freq:   The frequency with which to sleep between requests. The first value is the number of
                             seconds to sleep, the second value is the number of requests between sleeps.
        :param sqlize:       Whether to reformat the dataframes to an SQL-friendly format before returning them.
        :param verbose:      Whether to print the progress.
        :return:             A dictionary of dataframes that include every entry.
        """

        if not search_types:
            search_types = list(SearchType)
        if not semesters:
            semesters = self.get_all_semesters()
        if not search_terms:
            search_terms = [f'^{c}' for c in string.ascii_lowercase] + list(string.digits) + list('()*/\'"!-,:')

        req_num = 0

        dfs: Dict[str, Dict[str, pd.DataFrame]] = {}

        for search_type in search_types:
            invalid_db = False
            for s in semesters:
                if s not in dfs:
                    dfs[s] = {}
                for c in search_terms:
                    # Sleep after a certain amount of requests for a certain amount of time
                    if req_num >= sleep_freq[1]:
                        time.sleep(sleep_freq[0])
                        req_num = -1
                    req_num += 1

                    try:
                        res = self.search(search_type, sem=s, name=c)
                    except UnivISInvalidDatabaseException:
                        invalid_db = True
                        break
                    except UnivISInvalidSemesterException:
                        del dfs[s]
                        break
                    except UnivISException:
                        continue

                    # Store response in dataframes
                    for name, data in res['UnivIS'].items():
                        # Skip attributes of the root element (like version, semester, etc.)
                        if name[0] == '@':
                            continue

                        if type(data) != list:
                            data = [data]

                        df = pd.DataFrame().from_records(data).set_index(['@key'])

                        # Append the data to the dataframe. If it doesn't exist yet, create an empty dataframe first.
                        if name not in dfs[s]:
                            dfs[s][name] = pd.DataFrame()
                        new_df = pd.concat([dfs[s][name], df])
                        # Remove duplicates by applying a mask
                        dfs[s][name] = new_df[~new_df.index.duplicated(keep='first')]

                    if verbose:
                        print(f'Finished fetching {c}, {s}, {search_type}.')
                # If the UnivISInvalidDatabaseException was raised before, break out of the semester loop
                if invalid_db:
                    break

        if sqlize:
            dfs['all'] = {}
            for semester in dfs:
                if semester == 'all':
                    continue

                dfs[semester] = sqlize_dfs(dfs[semester], semester, self.scheme)
                for table in dfs[semester]:
                    if table not in dfs['all']:
                        dfs['all'][table] = pd.DataFrame()
                    dfs['all'][table] = pd.concat([dfs['all'][table], dfs[semester][table]])
                if verbose:
                    print(f'Finishing SQLizing {semester}.')
        return dfs

    def get_database_scheme(self) -> Dict[str, Dict[str, Union[bool, str, List[str]]]]:
        """
        Get the database scheme of the UnivIS instance.

        :return: A dictionary of the database scheme.
        """
        resp = req.get(f'{self.base_url}/univis.dtd')
        raw = resp.text.split('\n')

        schemes = {}
        for line in raw[2:]:
            if not line.startswith('<!ELEMENT'):
                continue
            is_list = False
            is_ref = False
            _, table_name, scheme = line.strip('>').split(' ')
            if scheme[-1] == '+':
                is_list = True
                scheme = scheme[:-1]
            if 'UnivISRef' in scheme:
                is_ref = True
                scheme = _is_univisref.search(scheme).group(1)
            for c in '()?|':
                scheme = scheme.replace(c, '')
            schemes[table_name] = {
                'is_list': is_list,
                'is_ref': is_ref,
                'type': 'TEXT',
                'attr': scheme.split(',')
            }
        return schemes
