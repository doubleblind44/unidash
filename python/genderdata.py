import sqlalchemy
import pandas as pd
from python.faculty import Faculty


def get_gender_data(db: sqlalchemy.engine.base.Engine,
                    only_female: bool = True,
                    threshold: int = 50,
                    ignore_count: int = 0
                    ) -> pd.DataFrame():
    """
    Gets the gender Data per faculty from the database

    :param db:           The database to get the data from
    :param only_female:  If true, only names that got declared as female are plotted.
                         Otherwise, plots every name that was not strictly declared as male.
    :param threshold:    A threshold for the probability.
    :param ignore_count: A threshold for the count that got returned by the api for a name.
    :return:             The gender data for the given parameters as a pandas DataFrame
    """
    sql = '''
    CREATE VIEW IF NOT EXISTS genderdata AS
    SELECT semester, orgunit, firstname, G.gender, prob, count
    FROM Person P NATURAL JOIN orgunits
        LEFT JOIN genders G ON P.firstname = G.query
    WHERE firstname NOT NULL 
        AND SUBSTR(orgunit, -8, 8) = 'Fakultät';
    '''
    with db.connect() as con:
        con.execute(sql)

    of_not = '' if only_female else 'NOT '
    of_gender = '\'f\'' if only_female else '\'m\''

    faculty_list = str(tuple([str(f) for f in Faculty]))

    sql = f'''
    SELECT semester AS 'Semester', 
        orgunit AS 'Fakultät', 
        SUM({of_not}(gender = {of_gender} AND prob >= {threshold})) * 100.0 / COUNT(*) AS 'Prozentualer Anteil',
        SUM({of_not}(gender = {of_gender} AND prob >= {threshold})) AS 'Anzahl',
        COUNT(*) AS 'Gesamt'
    FROM genderdata
    WHERE count > {ignore_count} 
        AND orgunit IN {faculty_list}
    GROUP BY semester, orgunit;
    '''
    return pd.read_sql(sql, db)
