from typing import Dict, List, Tuple, Union
import sqlalchemy


# Dictionaries of the compulsory modules sorted by fpos
WINF = {"2015": {"1": ["Einführung in die Wirtschaftsinformatik",
                       "Inf-ProgOO: Programmierung",
                       "Grundlagen der Betriebswirtschaftslehre",
                       "Mathematik für die Informatik A"],
                 "2": ["Betriebliche Standardsoftware",
                       "Algorithmen und Datenstrukturen",
                       "Produktion und Logistik",
                       "Mathematik für die Informatik B",
                       "Informatikrecht"],
                 "3": ["Einführung in Operations Research",
                       "Computersysteme",
                       "Inf-IS: Informationssysteme",
                       "Buchführung und Abschluss"],
                 "4": ["Seminar",
                       "Softwaretechnik", "Wissenschaftliches Arbeiten",
                       "Betriebs- und Kommunikationssysteme",
                       "Jahresabschluss", "Finanzwirtschaft I"],
                 "5": ["Projekt",
                       "Einführung in die Volkswirtschaftslehre",
                       "Privatrecht für Wirtschaftswissenschaftler",
                       "Datenschutz"],
                 "6": ["Innovationsmanagement: Prozesse und Methoden",
                       "Methodenlehre der Statistik I"]},
        "2017": {"1": ["Einführung in die Wirtschaftsinformatik",
                       "Inf-ProgOO: Programmierung",
                       "Einführung in die Betriebswirtschaftslehre",
                       "Mathematik für die Informatik A"],
                 "2": ["Betriebliche Standardsoftware",
                       "Algorithmen und Datenstrukturen",
                       "Mathematik für die Informatik B",
                       "Informatikrecht"],
                 "3": ["Einführung in Operations Research",
                       "Computersysteme",
                       "Inf-IS: Informationssysteme",
                       "Externes Rechnungswesen"],
                 "4": ["Seminar", "Softwaretechnik",
                       "Betriebs- und Kommunikationssysteme",
                       "Entscheidungsrechnungen"],
                 "5": ["Projekt",
                       "Einführung in die Volkswirtschaftslehre",
                       "Privatrecht für Wirtschaftswissenschaftler",
                       "Datenschutz"],
                 "6": ["Innovationsmanagement: Prozesse und Methoden",
                       "Statistische Methoden"]},
        "2019": {"1": ["Einführung in die Wirtschaftsinformatik",
                       "Inf-ProgOO: Programmierung",
                       "Mathematik für die Informatik A",
                       "Einführung in die Betriebswirtschaftslehre"],
                 "2": ["Betriebliche Standardsoftware",
                       "Algorithmen und Datenstrukturen",
                       "Mathematik für die Informatik B",
                       "Informatikrecht"],
                 "3": ["Einführung in Operations Research",
                       "Einführung in die Funktionale Programmierung",
                       "Inf-IS: Informationssysteme",
                       "Privatrecht für Wirtschaftswissenschaftler",
                       "Externes Rechnungswesen"],
                 "4": ["Entscheidungsrechnungen",
                       "Softwaretechnik",
                       "Betriebs- und Kommunikationssysteme",
                       "Theoretische Grundlagen der Informatik - Einführung",
                       "Wissenschaftliches Arbeiten",
                       "Computer Networks"],
                 "5": ["Seminar", "Datenschutz",
                       "Projekt", "Einführung in die Volkswirtschaftslehre"],
                 "6": ["Innovationsmanagement: Prozesse und Methoden",
                       "Statistische Methoden"]},
        "2021": {"1": ["Einführung in die Wirtschaftsinformatik",
                       "Einführung in die Informatik",
                       "Einführung in die Betriebswirtschaftslehre",
                       "Informatikrecht"],
                 "2": ["Einführung in die Algorithmik",
                       "Objektorientierte Programmierung",
                       "Mathematik für die Informatik B",
                       "Entscheidungsrechnungen"],
                 "3": ["Statistische Methoden",
                       "Einführung in die Volkswirtschaftslehre",
                       "Externes Rechnungswesen"],
                 "4": ["Softwaretechnik", "Database Systems",
                       "Wissenschaftliches Arbeiten"],
                 }}

INF = {"2015": {"1": ["Inf-ProgOO: Programmierung",
                      "Computersysteme",
                      "Mathematik für die Informatik A"],
                "2": ["Algorithmen und Datenstrukturen",
                      "Betriebs- und Kommunikationssysteme",
                      "Mathematik für die Informatik B"],
                "3": ["Fortgeschrittene Programmierung",
                      "Inf-IS: Informationssysteme",
                      "Mathematik für die Informatik C"],
                "4": ["Softwaretechnik",
                      "Theoretische Grundlagen der Informatik",
                      "Numerische Programmierung"],
                "5": ["Seminar", "Logik in der Informatik", "Wissenschaftliches Arbeiten"],
                "6": []},
       "2019": {"1": ["Inf-ProgOO: Programmierung",
                      "Computersysteme",
                      "Mathematik für die Informatik A"],
                "2": ["Algorithmen und Datenstrukturen",
                      "Betriebs- und Kommunikationssysteme",
                      "Mathematik für die Informatik B"],
                "3": ["Fortgeschrittene Programmierung",
                      "Inf-IS: Informationssysteme",
                      "Mathematik für die Informatik C"],
                "4": ["Softwaretechnik",
                      "Theoretische Grundlagen der Informatik",
                      "Wissenschaftliches Arbeiten"],
                "5": ["Seminar", "Logik in der Informatik"],
                "6": []},
       "2021": {"1": ["Einführung in die Informatik",
                      "Computersysteme",
                      "Mathematik für die Informatik A"],
                "2": ["Einführung in die Algorithmik",
                      "Objektorientierte Programmierung",
                      "Mathematik für die Informatik B",
                      "Computer Networks"],
                "3": ["Deklarative Programmierung",
                      "Operating Systems",
                      "Berechnungen und Logik",
                      "Mathematik für die Informatik C"],
                "4": ["Softwaretechnik",
                      "Database Systems",
                      "Analyse von Algorithmen und Komplexität",
                      "Wissenschaftliches Arbeiten"],
                }}


def build_schedule(db: sqlalchemy.engine.Engine,
                   modules: Dict[str, List[str]],
                   winf_modules: bool = False
                   ) -> Dict[str, Dict[str, List[str]]]:
    """
    Collects the lecture keys from every semester for every study programme sorted by fpo


    :param db:           A sql database
    :param modules:      The modules of the faculties "Faculty of Engineering" and
                          "Faculty of Mathematics and Natural Sciences", if winf_modules set also "Faculty" of Law" and
                          "Faculty of Business, Economics, and Social Sciences"
    :param winf_modules: If set collects lecture from the course of study "Wirtschaftsinformatik",
                          otherwise from "Informatik"
    :return:             Dictionary containing the lecture's key for every lecture in a certain course of study
    """
    # choose the dictionaries containing the fpos
    fpo_modules = WINF if winf_modules else INF
    fpos = list(fpo_modules.keys())
    con = db.connect()
    schedule = {}
    # go through the semesters
    for semester in modules:
        # get the lectures keys of the all the lectures that could be relevant for us
        modules_to_check = tuple(modules[semester])
        # is the semester in winter or summer
        season = str(semester[-1])
        # get the year of the semester
        year = int(semester[:-1])
        info = []
        # get the title, name, key and type of the lectures in modules_to_check
        # that aren't registered as exercises in univis
        if len(modules_to_check) > 1:
            query = "SELECT classification, name, [@key], type " \
                    "FROM Lecture " \
                    "WHERE classification NOT NULL " \
                    "AND Lecture.semester = :sem " \
                    "AND type IN ('V', 'UE', 'S', 'V-UE') " \
                    "AND NOT (type = 'UE' AND [parent-lv] IS NOT NULL) " \
                    "AND [@key] IN " + str(modules_to_check) + \
                    " GROUP BY name, semester"
            info = con.execute(query, sem=semester)
        elif len(modules_to_check) == 1:
            query = "SELECT classification, name, [@key], type " \
                    "FROM Lecture " \
                    "WHERE classification NOT NULL " \
                    "AND Lecture.semester = :sem  " \
                    "AND type IN ('V', 'UE', 'S', 'V-UE')  AND NOT (type = 'UE' AND [parent-lv] IS NOT NULL) " \
                    "AND [@key] = :module " \
                    "GROUP BY name, semester"
            info = con.execute(query, sem=semester, module=modules_to_check[0])
        # go through the modules
        for title, name, key, lec_type in info:
            title_split = title.split(".")
            # flag to check if a module is offered by the faculty of engineering
            eng_faculty = title_split[1] == "techn"
            # from the faculty of engineering we only need the modules from the department of computer science
            if eng_faculty and (len(title_split) < 5 or title_split[2] != "infora"):
                continue
            # from the department of computer science we only need the modules for Wirtschaftsinformatik and Informatik
            if eng_faculty and (not (title_split[3] == 'bachel' or winf_modules and title_split[3] == 'bachel_1')):
                continue
            # gp through the different fpos
            for i in range(len(fpos)):
                fpo = fpos[i]
                fpo_year = int(fpo)
                # if the year of the current semester is before the year the fpo was published, we look at the next fpo
                if year < fpo_year or semester == "2015s":
                    continue
                if semester not in schedule:
                    schedule[semester] = {}
                # go through the study programme semesters
                for fpo_sem in fpo_modules[fpo]:
                    int_fpo_sem = int(fpo_sem)
                    # in summer, we can skip the study programme semesters 1, 3 and 5 and in winter 2, 4 and 6
                    if (season == "s" and int_fpo_sem % 2 == 1) or (season == "w" and int_fpo_sem % 2 == 0):
                        continue

                    # Computer Networks has to be treated differently because it is the replacement for BSKS
                    if eng_faculty and winf_modules and fpo_year == 2019 and year == 2022 and "Computer Networks" in name:
                        if "4" not in schedule[semester]:
                            schedule[semester]["4"] = [key]
                        else:
                            schedule[semester]["4"] += [key]
                        break

                    next_fpo = float('inf') if i == len(fpos) - 1 else int(list(fpos)[i+1])

                    # we have to see if the fpo is applicable for that study_sem and year
                    if fpo_year <= int(year - (int(fpo_sem) - 1) / 2) < next_fpo:

                        if fpo_sem not in schedule[semester]:
                            schedule[semester][fpo_sem] = []
                        # go through the lectures
                        for lecture in fpo_modules[fpo][fpo_sem]:
                            # The projects in the course of study "Wirtschaftsinformatik" has to be handled differently
                            # because there are offered more than one in a semester and we only want to add one project
                            # per semester
                            if lecture == "Projekt":
                                # The projects are scheduled for the study progamme semesetre 5
                                # and only for the Wirtschaftsinformatiker
                                if eng_faculty and lecture.casefold() in name.casefold() \
                                        and "P" not in schedule[semester] and fpo_sem == "5" \
                                        and title_split[3] == "bachel_1":
                                    schedule[semester][fpo_sem] += [key]
                                    # There is only one project per semester.
                                    # Save it in the dictionary so we don't add another one
                                    schedule[semester]["P"] = True
                                continue

                            # The seminars have to handled differently because in one semester there are offered more
                            # than one and in their name it's not specified that the lecture is a seminar
                            if lecture == "Seminar":
                                # Sometimes "Wissenschaftliches Arebiten" has the word "Seminar" in its title
                                if lec_type == 'S' and lecture.casefold() in name.casefold() \
                                        and "Wissenschaftliches Arbeiten".casefold() not in name.casefold():
                                    # Wirtschaftsinformatiker and Informatiker have separate seminars
                                    if eng_faculty and (winf_modules and title_split[3] == "bachel_1"
                                                        or not winf_modules and title_split[3] == "bachel"):
                                        if 'S' not in schedule[semester]:
                                            schedule[semester][fpo_sem] += [key]
                                            # There is only one seminar per semester.
                                            # Save it in the dictionary so we don't add another one
                                            schedule[semester]["S"] = True
                                continue

                            # skip the modules for 2-Fächler
                            if "(2F)".casefold() in name.casefold():
                                break
                            # We only want the module "Statistische Methoden" from the Faculty of engineering
                            if lecture == "Statistische Methoden" and title_split[1] == "mathe":
                                break

                            # We only want the module "Wissenschaftliches" from the Faculty of engineering
                            if lecture == "Wissenschaftliches Arbeiten" and lecture.casefold() in name.casefold() \
                                    and len(title_split) > 2 and title_split[2] != "infora":
                                break

                            # TGI for Wirtschaftsinformatiker is sometimes registered as its separate module
                            # and other times we have to use the module from Informatik
                            if lecture == "Theoretische Grundlagen der Informatik - Einführung" \
                                    and "Theoretische Grundlagen der Informatik".casefold() in name.casefold() \
                                    and semester == "2021s" and fpo_sem == '4':
                                schedule[semester][fpo_sem] += [key]
                                break
                            # If the current lecture and current module in the fpo don't match, continue
                            if lecture.casefold() not in name.casefold():
                                continue

                            # We only want to add the module "Einführung in die Volkswirtschaftslehre"
                            # once per study programme semester
                            vwl_key = 'Lecture.wirtsc.instit.zentr.evwl'
                            evwl_key = 'Lecture.wirtsc.instit.lehrst.einfhr'
                            eivwl_key = 'Lecture.wirtsc.instit.zentr.einfhr'
                            if key == vwl_key and (evwl_key in schedule[semester][fpo_sem] or eivwl_key in schedule[semester][fpo_sem]) \
                                    or key == evwl_key and (vwl_key in schedule[semester][fpo_sem] or eivwl_key in schedule[semester][fpo_sem]) \
                                    or key == eivwl_key and (vwl_key in schedule[semester][fpo_sem] or evwl_key in schedule[semester][fpo_sem]):
                                break

                            # if we found out that the current lecture is a compulsory lecture, put it in a new list
                            schedule[semester][fpo_sem] += [key]

                            break

    return schedule


def add_exercises_inf(schedule: Dict[str, Dict[str, List[str]]], db: sqlalchemy.engine.Engine):
    """
    Adds the exercises for the course of study Informatik to the schedules

    :param schedule: A dictionary containing the lectures, which exercises we are looking for
    :param db: sql connection
    """
    con = db.connect()
    # go through the semesters
    for sem in schedule:
        # go through the study programme semesters
        for i in schedule[sem]:
            # ignore the flags fpr projects and seminars
            if i in ["P", "S"]:
                continue
            # get the lectures
            modules = tuple(schedule[sem][i])

            info = []
            # get the exercises of the current semesters to our list of lectures
            if len(modules) > 1:
                query = "SELECT name, [@key], [parent-lv] " \
                        "FROM Lecture " \
                        "WHERE [parent-lv] NOT NULL " \
                        "AND Lecture.semester = :sem " \
                        "AND type NOT IN ('S', 'V-UE') " \
                        "AND [parent-lv] IN " + str(modules) + \
                        " GROUP BY name, [parent-lv]"
                info = con.execute(query, sem=sem)
            elif len(modules) == 1:
                query = "SELECT name, [@key], [parent-lv] " \
                        "FROM Lecture " \
                        "WHERE [parent-lv] NOT NULL " \
                        "AND Lecture.semester = :sem  " \
                        "AND type NOT IN ('S', 'V-UE') " \
                        "AND [parent-lv] = :module " \
                        "GROUP BY name, [parent-lv]"
                info = con.execute(query, sem=sem, module=modules[0])
            # go through the exercises
            for name, key, parent_lv in info:
                if parent_lv not in schedule[sem][i]:
                    continue
                # add the exercise to our schedule
                schedule[sem][i] += [key]

    return schedule


def add_exercises_winf(schedule: Dict[str, Dict[str, List[str]]], db: sqlalchemy.engine.Engine):
    """
    Adds the exercises for the course of study Wirtschaftsinformatik to the schedules

    :param schedule: A dictionary containing the lectures, which exercises we are looking for
    :param db: sql connection
    """
    con = db.connect()
    # go through the semesters
    for sem in schedule:
        # go through the study programme semesters
        for i in schedule[sem]:
            # ignore the flags fpr projects and seminars
            if i in ["P", "S"]:
                continue
            # get the lectures
            modules = tuple(schedule[sem][i])

            info = []
            # get the exercises of the current semesters to our list of lectures
            if len(modules) > 1:
                query = "SELECT name, [@key], [parent-lv] " \
                        "FROM Lecture " \
                        "WHERE [parent-lv] NOT NULL " \
                        "AND Lecture.semester = :sem " \
                        "AND type NOT IN ('S', 'V', 'V-UE') " \
                        "AND [parent-lv] IN " + str(modules) + \
                        " GROUP BY name, [parent-lv]"
                info = con.execute(query, sem=sem)
            elif len(modules) == 1:
                query = '''
                SELECT name, [@key], [parent-lv]
                FROM Lecture
                WHERE [parent-lv] NOT NULL
                    AND Lecture.semester = :sem 
                    AND type NOT IN ('S', 'V', 'V-UE')
                    AND [parent-lv] = :module
                GROUP BY name, [parent-lv]
                '''
                info = con.execute(query, sem=sem, module=modules[0])
            # go through the exercises
            for name, key, parent_lv in info:
                if parent_lv not in schedule[sem][i]:
                    continue
                # we don't want to add this exercise twice
                inno = 'Übung zur Vorlesung Innovationsmanagement: Prozesse und Methoden (BWL-InnoMProz)'
                inno_key = 'Lecture.wirtsc.instit_5.lehrst.statis'
                if inno_key in schedule[sem][i] and name == inno and sem == '2020s':
                    continue
                # we don't want to add this exercise twice
                prod = 'Übung zu \"Produktion und Logistik\" - Gruppe 2'
                if name == prod:
                    continue

                # add the exercise to our schedule
                schedule[sem][i] += [key]
    # we have to add this exercise manually
    schedule['2019w']['5'] += ['Lecture.wirtsc.instit.zentr.bungzu']

    return schedule


def get_dependencies(db: sqlalchemy.engine.Engine,
                     schedule: Dict[str, Dict[str, List[str]]],
                     raise_on_error: bool = False
                     ) -> Dict[str, Dict[str, List[List[str]]]]:
    """
    Finds a time schedule for a list of given lectures

    :param db:             The database connection
    :param schedule:       A dictionary containing the lectures of every study programme semester sorted by the fpo
    :param raise_on_error: If true, an exception will be raised if generating a schedule was not possible
    :return:               A dictionary containing the location of lectures ordered by the day and time they take place
                            on for every study programme semester and semester
    """
    con = db.connect()
    dependencies = {}
    # for each semester we have to find out the dependencies
    for sem in schedule:
        dependencies[sem] = {}
        for study_sem in schedule[sem]:
            # ignore the entries for projects and seminars
            if study_sem in ["P", "S"]:
                continue
            lectures = str(tuple(schedule[sem][study_sem]))
            query = f'''
            SELECT
                COALESCE(C.[@key], T.[@key])             AS '@key',
                CAST(SUBSTR(repeat, 4, 4) AS INT)        AS weekday,
                CAST(REPLACE(starttime, ':', '') AS INT) AS starttime,
                CAST(REPLACE(endtime, ':', '') AS INT)   AS endtime,
                new_address,
                type,
                [parent-lv],
                L.name                                   AS 'name'
            FROM terms T
                LEFT JOIN courses C
                    ON T.[@key] = C.course AND T.semester = C.semester
                LEFT JOIN Lecture L
                    ON (T.[@key] = L.[@key] OR C.course = L.[@key]) AND T.semester = L.semester
                LEFT JOIN Room R
                    ON T.room = R.[@key] AND T.semester = R.semester
                LEFT JOIN new_addresses N 
                    ON R.address = N.old_address
            WHERE T.semester = :sem
                AND T.enddate IS NULL
                AND starttime IS NOT NULL
                AND endtime IS NOT NULL
                AND repeat NOT NULL
                AND repeat != 'd1'
                AND (T.[@key] IN {lectures} OR C.[@key] IN {lectures})
            
            GROUP BY COALESCE(C.[@key], T.[@key]), weekday, starttime, endtime, address, type, [parent-lv], L.name
            ORDER BY weekday, starttime;
            '''

            terms = list(con.execute(query, sem=sem))

            # Create a virtual start term to compare the first real term with it
            empty = {'weekday': -1, 'endtime': float('inf')}
            ok, sched = example_schedule(empty, terms, [])

            if ok:
                dependencies[sem][study_sem] = sched
            elif raise_on_error:
                raise Exception(f'Could not find schedule for semester {sem} and study semester {study_sem}')
    return dependencies


def example_schedule(prev: Dict[str, Union[str, int]],
                     terms: List[Tuple[str, str, str, str, str, str, str]],
                     used_practicals: List[str],
                     ) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Tries to find a schedule using a given term.

    :param prev:            The previous term in the schedule.
    :param terms:           A list of all terms that are still left to schedule.
    :param used_practicals: A list of all practical classes that are already scheduled.
    :return:                A tuple containing a boolean that indicates if a schedule was found
                            and a dictionary of all days that got filled by the schedule
                            with the corresponding addresses in a list.
    """
    if len(terms) == 0:  # If no terms are left, everything is scheduled
        return True, {}

    # Take the first remaining term
    term = {'@key': terms[0][0], 'weekday': terms[0][1], 'starttime': terms[0][2],
            'endtime': terms[0][3], 'addr': terms[0][4], 'type': terms[0][5],
            'parent-lv': terms[0][6], 'name': terms[0][7]}

    # If the term is a practical class, check if it is already scheduled
    if term['parent-lv'] is not None and term['type'] not in ('V', 'S', 'V-UE') \
            or any(sub.casefold() in term['name'].casefold()
                   for sub in ['übung', 'praktikum', 'exercise', 'tutorium', 'repetitorium', 'kolloquium', 'tutorial']):

        if term['@key'] in used_practicals:  # If the practical class is already scheduled, skip it
            return example_schedule(prev, terms[1:], used_practicals)
        if term['weekday'] == prev['weekday'] \
                and term['starttime'] < prev['endtime']:  # If the practical class does not fit, skip it
            return example_schedule(prev, terms[1:], used_practicals)
        ok, sched = example_schedule(term, terms[1:], used_practicals + [term['@key']])  # check if works with practical
        if ok:
            # Add practical to schedule and return it
            if term['weekday'] not in sched:
                sched[term['weekday']] = []
            sched[term['weekday']].insert(0, term['addr'])
            return True, sched
        return example_schedule(prev, terms[1:], used_practicals)  # Return the schedule without the practical

    # If the term is a lecture, check if it fits
    if term['weekday'] <= prev['weekday'] and term['starttime'] < prev['endtime']:
        return False, {}  # Lectures are mandatory, so if it does not fit, return False
    # Otherwise, add it to the schedule and check if the rest fits
    ok, sched = example_schedule(term, terms[1:], used_practicals)
    if term['weekday'] not in sched:
        sched[term['weekday']] = []
    sched[term['weekday']].insert(0, term['addr'])
    return ok, sched
