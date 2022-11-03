from enum import Enum
from typing import Dict, List, Optional
import sqlalchemy
import re
import python.parse_addr
from python.faculty import Faculty
from python.geomanager import GeoManager


def get_lectures(db: sqlalchemy.engine.Engine,
                 sem: Optional[str] = None,
                 filter_practical: bool = False
                 ) -> Dict[str, Dict[str, List[str]]]:
    """
    Collects lectures for each faculty.

    :param db: the sql database
    :param sem: if set only returns lecture of that semester
    :param filter_practical: if set filter the practicals
    :return: a dictionary that maps lecture keys to their faculties and semesters if wanted
    example: {"Technische Fakultät: {2019s: [Programmierung, Computersysteme], 2018s: [...] }, "Medizinische Fakultät": 2020s : [...], ...}
    """
    # dict to save the lectures
    lectures_faculties = {}
    with db.connect() as con:
        # get the different semesters
        semesters = con.execute('SELECT `semester` FROM `Lecture` GROUP BY semester;')
        # look at the lectures of every semester
        for semester in list(semesters):
            semester = semester[0]
            # for each lecture look at the assigned organisations
            for f in Faculty:
                fac = str(f)
                lectures = con.execute("SELECT [@key] "
                                       "FROM orgunits NATURAL JOIN Lecture L "
                                       "WHERE semester = :sem "
                                       "AND `orgunit` = :unit AND (:boo = 1 AND type IN ('V', 'S', 'V-UE') OR :boo = 0)",
                                       sem=semester, unit=fac, boo=int(filter_practical))

                # for every faculty save the lecture's key in a dictionary
                if fac not in lectures_faculties:
                    lectures_faculties[fac] = {}
                if semester not in lectures_faculties[fac]:
                    lectures_faculties[fac][semester] = [x[0] for x in lectures]
    # return the dict if sem isn't set or None
    if sem is None:
        return lectures_faculties
    else:
        # if sem is set, save the lectures of that semester in a separate dictionary to return
        res = {}
        for fac in lectures_faculties:
            if sem in lectures_faculties[fac]:
                res[fac] = {sem: lectures_faculties[fac][sem]}
        return res


def get_rooms_per_faculty(db: sqlalchemy.engine.Engine):
    """
    gets all the rooms of the faculties
    :param db: sql database
    :return: a dictionary containing the rooms of every faculty sorted by semester
    """
    # dict to save the lectures
    rooms_faculties = {}
    with db.connect() as con:
        # get the rooms for every faculty
        query = "SELECT TeOr.semester, orgunit, room, COUNT(*) " \
               "FROM (terms NATURAL JOIN orgunits) TeOr " \
               "LEFT JOIN Lecture ON TeOR.[@key] = Lecture.[@key] AND TeOr.semester = Lecture.semester " \
               "WHERE room NOT NULL " \
               "AND SUBSTR(orgunit, -8, 8) = 'Fakultät' " \
               "GROUP BY TeOr.semester, orgunit, room"
        info = con.execute(query)
        # go through the rooms
        for semester, fac, room, number in info:
            # save the room key and the number of uses in a dictionary
            if semester not in rooms_faculties:
                rooms_faculties[semester] = {}
            if fac not in rooms_faculties[semester]:
                rooms_faculties[semester][fac] = {}
            if room not in rooms_faculties[semester][fac]:
                rooms_faculties[semester][fac][room] = number
    return rooms_faculties


# sql-Variante
def get_rooms_for_faculty(lectures: Dict[str, Dict[str, List[str]]], db: sqlalchemy.engine.Engine) -> List[str]:
    """
    gets the room keys for a list of lectures, only for one faculty

    :param lectures: dictionary of lecture keys with their semester whose rooms we want to get.
                     example: lectures = {sem: [lectureA key, lectureB key,...],...}
    :param db:      data returned by the univis module
    :return:         list of room keys
    """
    rooms = []
    con = db.connect()

    # only look at the lectures of the semesters we need
    for sem in lectures:
        rms = []
        # get the rooms to our lectures of the current semesters
        if len(lectures[sem]) > 1:

            modules = tuple(lectures[sem])
            query = "SELECT room " \
                    "FROM terms " \
                    "WHERE room NOT NULL " \
                    "AND semester = :s " \
                    "AND [@key] IN " + str(modules)

            rms = con.execute(query, s=sem)

        elif len(lectures[sem]) == 1:
            query = "SELECT room " \
                    "FROM terms " \
                    "WHERE room NOT NULL " \
                    "AND semester = :s " \
                    "AND [@key] = :lecture_key"
            rms = con.execute(query, s=sem, lecture_key=lectures[sem][0])
        # save the rooms in a list
        rooms += [x[0] for x in rms]
    return rooms


def get_addr_of_rooms(rooms: List[str], db: sqlalchemy.engine.Engine) -> List[str]:
    """
    gets the addresses of rooms
    :param rooms: room keys
    :param db: sql database
    :return: list containing the addresses
    """
    con = db.connect()

    rms = tuple(rooms)
    # get the address
    query = "SELECT address " \
            "FROM Room " \
            "WHERE address NOT NULL AND [@key] IN " + str(rms) + " GROUP BY [@key]"

    addr = con.execute(query)
    # return the addresses in a list
    return [x[0] for x in addr]


def addr_per_faculty_now(db, geoman: GeoManager):
    """
    get the addresses and coordinates from all the rooms where lectures were hold, sorted per semester and faculty
    :param db: sql database
    :param geoman: the GeoManager object to get the coordinates
    :return: a dictionary containing the address and cooridinates of the rooms
    where lectures were hold, sorted per semester and faculty
    """
    # dict to save the addresses and coordinates
    addr_faculties = {}
    con = db.connect()
    # get the addresses of the rooms used by the faculties
    query = "SELECT TeOr.semester, orgunit, room, COUNT(*), new_address, Room.short " \
            "FROM (terms NATURAL JOIN orgunits) TeOr " \
            "LEFT JOIN Lecture ON TeOR.[@key] = Lecture.[@key] AND TeOr.semester = Lecture.semester " \
            "LEFT JOIN Room ON TeOr.room = Room.[@key] AND TeOr.semester = Room.semester " \
            "LEFT JOIN new_addresses ON Room.address = old_address "\
            "WHERE room NOT NULL " \
            "AND SUBSTR(orgunit, -8, 8) = 'Fakultät' " \
            "GROUP BY TeOr.semester, orgunit, room " \
            "ORDER BY TeOr.semester"
    info = con.execute(query)
    # go through the rooms
    for semester, fac, room, number, address, short_name in info:

        # parse the address so the coordinates can be found
        coords = None

        # get the coordinates
        if address:
            coords = geoman.get_coords(address)

        # for every faculty save the coordinates and some other information in the dict
        if semester not in addr_faculties:
            addr_faculties[semester] = {}
        if fac not in addr_faculties[semester]:
            addr_faculties[semester][fac] = {}
        if room not in addr_faculties[semester][fac]:
            addr_faculties[semester][fac][room] = {'count': number, 'coords': coords, 'name': short_name, 'has_addr': address is not None, 'addr': address}

    return addr_faculties
