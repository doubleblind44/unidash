from typing import Dict, Tuple
import sqlalchemy
from python.faculty import Faculty


def rollis(db: sqlalchemy.engine.base.Engine) -> Dict[str, Dict[str, Tuple[int, int, float]]]:
    """
    Returns the total and relative number of wheelchair friendly rooms used by a faculty in a semester.

    :param db: The database connection.
    :return:   A dictionary with the faculties as keys and a dictionary with the semester as keys and a tuple with the
               total number of wheelchair friendly rooms, the total number of rooms and the relative number of
               wheelchair friendly rooms as values.
    """
    con = db.connect()
    rolli_lectures = {}
    faculties = str(tuple([str(x) for x in Faculty]))
    # get the number of wheelchair friendy rooms, semester, orgunit and compute the relative number
    query = f'''
    SELECT OT.semester, orgunit, SUM(rolli), COUNT(*), ROUND(SUM(rolli) * 100.0 / COUNT(*), 2)
    FROM (terms NATURAL JOIN orgunits) OT
        LEFT JOIN Lecture ON OT.semester = Lecture.semester AND OT.[@key] = Lecture.[@key]
        LEFT JOIN Room ON OT.room = Room.[@key] AND OT.semester = Room.semester
    WHERE orgunit IN {faculties}
        AND SUBSTR(OT.[@key], 0, INSTR(OT.[@key], '.')) = 'Lecture'
    GROUP BY OT.semester, orgunit;
    '''

    info = con.execute(query)
    # add the information in the dictionary
    for sem, fac, rolli_sum, total, ratio in info:
        if sem not in rolli_lectures:
            rolli_lectures[sem] = {}
        rolli_lectures[sem][fac] = (rolli_sum, total, ratio)

    return rolli_lectures
