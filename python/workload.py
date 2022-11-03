import pandas as pd
import sqlalchemy
from python.faculty import Faculty


def workloads(db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    computes the average workload of a teaching person for every semester sorted by faculty

    :param db: sql database
    :return: dictionary containing the average workload for every semester sorted by faculty
    """
    con = db.connect()
    faculties = str(tuple([str(x) for x in Faculty]))
    # get the average workload for every semester sorted by faculty
    sql = f'''
    SELECT AVG(anzahl) AS Arbeitsbelastung, semester AS Semester, orgunit AS Fakultät
    FROM (
        SELECT LD.semester, orgunit, Person.[@key], COUNT(*) AS anzahl 
        FROM (Lecture NATURAL JOIN dozs) LD 
            LEFT JOIN Person ON Person.[@key] = LD.doz AND Person.semester = LD.semester 
            LEFT JOIN orgunits o on LD.semester = o.semester and LD.[@key] = o.[@key] 
        WHERE Person.title NOT NULL 
            AND Person.lehr = 1 
            AND orgunit IN {faculties}
            AND LD.type NOT IN ('AG', 'FPUE', 'KL', 'KO', 'UAK', 'KU', 'SPUE', 'P', 'P-SEM', 'PRUE', 'TU', 'broken')
            GROUP BY LD.semester, orgunit, Person.[@key]
    ) 
    GROUP BY semester, orgunit;
    '''
    return pd.read_sql(sql, db)
