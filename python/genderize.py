import requests as req
import time
from urllib.parse import urlencode
from typing import List, Optional, Iterable, Tuple
import sqlalchemy.engine
import re


def genderize(db: sqlalchemy.engine.Engine, gapi: "GenderAPI", verbose: bool = False):
    """
    Genderizing names from the database

    :param db:      The database
    :param gapi:    The gender API object
    :param verbose: Prints the progress
    """
    with db.connect() as con:
        sql = "CREATE TABLE IF NOT EXISTS genders (query TEXT, name TEXT, gender VARCHAR(1), prob FLOAT, count INT);"
        con.execute(sql)
        if verbose:
            print("Created table 'genders'")

        sql = "SELECT firstname FROM Person WHERE firstname NOT NULL GROUP BY firstname;"
        names = [x[0] for x in con.execute(sql)]
        if verbose:
            print(f'Got {len(names)} names from database')
        gapi.add_names(names)
        gapi.fetch()
        sql_insert = "INSERT INTO genders VALUES (:query, :name, :gender, :prob, :count);"
        for name in gapi.names.values():
            con.execute(sql_insert, query=name['q'], name=name['name'], gender=name['gender'][0],
                        prob=name['probability'], count=name['total_names'])
        if verbose:
            print("Inserted all names into the database")
        sql = '''
        SELECT firstname
        FROM Person
        WHERE firstname NOT IN (
            SELECT query
        FROM genders
        GROUP BY query
        )
        GROUP BY firstname;
        '''
        double_names = list(con.execute(sql))
        if verbose:
            print(f'Found {len(double_names)} names that are probably combinations of the names inside the database')

        for dn in double_names:
            name = dn[0]
            m = 0
            f = 0
            n = 0
            gobj = {'gender': 'n', 'prob': 0, 'count': 0}
            ns = name.split(' ')
            for comp in ns:
                if comp not in gapi.names:
                    n += 100
                    continue
                nobj = gapi.names[comp]
                if nobj['gender'][0] == 'm':
                    m += nobj['probability']
                elif nobj['gender'][0] == 'f':
                    f += nobj['probability']
                else:
                    n += nobj['probability']
                gobj['count'] += nobj['total_names']
            if m > f:
                gobj['gender'] = 'm'
                gobj['prob'] = (m - f) // len(ns)
            elif f > m:
                gobj['gender'] = 'f'
                gobj['prob'] = (f - m) // len(ns)
            else:
                gobj['gender'] = 'n'
                gobj['prob'] = n
            con.execute(sql_insert, query=name, name=name,
                        gender=gobj['gender'], prob=gobj['prob'], count=gobj['count'])


class GenderAPIException(Exception):
    """
    Exception for the GenderAPI
    """
    def __init__(self, errno: int, message: str):
        super().__init__(f'{errno}: {message}')


class GenderAPI:
    """
    Class to handle the requests to the genderize.io API.
    """
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False, auto_fetch: bool = True):
        """
        Initializes the class with the API key.

        :param api_key:    The API key.
        :param verbose:    If True, prints the progress.
        :param auto_fetch: If True, automatically fetches the names from the queue.
        """
        self.api_key = api_key
        self.queue = []
        self.names = {}
        self.queue_cache = set()
        self.verbose = verbose
        self.auto_fetch = auto_fetch

    def add_name(self, name: str):
        """
        Adds a name to the queue.

        :param name: The name to add to the queue.
        """
        self.add_names([name])

    def add_names(self, names: Iterable[str]):
        """
        Adds multiple names to the queue.

        :param names: The names to add to the queue.
        """
        for name in names:
            nms = name.split(' ')
            for n in nms:
                if re.search(r'\d', n):
                    continue
                if n not in self.queue_cache:
                    self.queue.append(n)
                    self.queue_cache.add(n)
        if self.verbose:
            print(f'Added names to the queue. The queue has now {len(self.queue)} names.')
        if self.auto_fetch and len(self.queue) >= 100:
            if self.verbose:
                print('The queue has more than 100 names. Fetching...')
            self.queue = self.request_names(self.queue)

    def fetch(self):
        """
        Fetches the names from the queue.
        """
        if self.verbose:
            print(f'Fetching {len(self.queue)} names from the queue')

        if len(self.queue) >= 100:
            self.queue = self.request_names(self.queue)
        if len(self.queue) > 0:
            self.queue = self.request_names(self.queue)

    def request_names(self, names: List[str], sleep_freq: Tuple[int, int] = (1, 10)) -> List[str]:
        """
        Sends API-requests.

        :param names:      The names to request.
        :param sleep_freq: The frequency with which to sleep between requests. The first value is the number of
                           seconds to sleep, the second value is the number of requests between sleeps.
        :return:           The names that are left in the queue.
        """

        r_count = 0
        while len(names) >= 100 or r_count == 0:
            req_names = names[:100]

            q = {'name[]': req_names}
            if self.api_key is not None:
                q['key'] = self.api_key

            query = urlencode(q, True)

            if sleep_freq[0] > 0 and r_count % sleep_freq[1] == 0:
                if self.verbose:
                    print(f'Sleeping for {sleep_freq[0]} seconds')
                time.sleep(sleep_freq[0])

            resp = req.post(f'https://genderapi.io/api/?{query}')
            r_count += 1

            resp_json = resp.json()

            if resp_json['status']:
                for name in resp_json['names']:
                    self.names[name['q']] = name

                names = names[100:]
                if self.verbose:
                    print(f'Fetched {len(req_names)} names. {len(names)} names left in queue.')
            else:
                if self.verbose:
                    print(f'Error on requesting the following names: {req_names}')
                raise GenderAPIException(resp_json['errno'], resp_json['errmsg'])
        return names
