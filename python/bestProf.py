import datetime
import sqlalchemy.engine
import pandas as pd
import plotly.express as px
import python.moduldbparser as moduldbparser

# List of all Best Prof Award winners: (name, year, place).
winner = [("Landsiedel", "Olaf", 2019, 1), ("Langfeld", "Barbara", 2019, 2), ("Mühling", "Andreas", 2019, 3),
          ("Schimmler", "Manfred", 2018, 1), ("von Hanxleden", "Reinhard", 2018, 2), ("Hanus", "Michael", 2018, 3),
          ("Huch", "Frank", 2017, 1), ("Mühling", "Andreas", 2017, 2), ("Schimmler", "Manfred", 2017, 3),
          ("Schimmler", "Manfred", 2016, 1), ("Huch", "Frank", 2016, 2), ("Wilke", "Thomas", 2016, 3),
          ("Wilke", "Thomas", 2015, 1), ("Braune", "Gert", 2015, 2), ("von Hanxleden", "Reinhard", 2015, 3),
          ("Speck", "Andreas", 2014, 1), ("Langfeld", "Barbara", 2014, 2), ("Wilke", "Thomas", 2014, 3),
          ("Börm", "Steffen", 2013, 1), ("von Hanxleden", "Reinhard", 2013, 2), ("Slawig", "Thomas", 2013, 3),
          ("Berghammer", "Rudolf", 2012, 1), ("Schimmler", "Manfred", 2012, 2), ("Hanus", "Michael", 2012, 3),
          ("Huch", "Frank", 2011, 1), ("Wilke", "Thomas", 2011, 2), ("von Hanxleden", "Reinhard", 2011, 3),
          ("von Hanxleden", "Reinhard", 2010, 1), ("Langfeld", "Barbara", 2010, 2), ("Wilke", "Thomas", 2010, 3)]

# List of exam periods.
# Tuple format = (semester, first period with start day, start month, end day, end month & second period).
exam_periods = [("2009w", 11, 2, 24, 2, 29, 3, 9, 4),
                ("2010s", 19, 7, 30, 7, 11, 10, 22, 10),
                ("2010w", 9, 2, 22, 2, 28, 3, 8, 4),
                ("2011s", 11, 7, 22, 7, 10, 10, 21, 10),
                ("2011w", 13, 2, 24, 2, 26, 3, 5, 4),
                ("2012s", 2, 7, 13, 7, 8, 10, 19, 10),
                ("2012w", 11, 2, 22, 2, 25, 3, 5, 4),
                ("2013s", 1, 7, 12, 7, 14, 10, 25, 10),
                ("2013w", 10, 2, 22, 2, 31, 3, 12, 4),
                ("2014s", 14, 7, 26, 7, 13, 10, 25, 10),
                ("2014w", 9, 2, 21, 2, 30, 3, 11, 4),
                ("2015s", 13, 7, 25, 7, 12, 10, 24, 10),
                ("2015w", 11, 2, 24, 2, 28, 3, 9, 4),
                ("2016s", 18, 7, 30, 7, 10, 10, 22, 10),
                ("2016w", 7, 2, 20, 2, 27, 3, 8, 4),
                ("2017s", 17, 7, 29, 7, 9, 10, 21, 10),
                ("2017w", 8, 2, 21, 2, 26, 3, 7, 4),
                ("2018s", 16, 7, 28, 7, 8, 10, 20, 10),
                ("2018w", 11, 2, 23, 2, 25, 3, 6, 4),
                ("2019s", 8, 7, 20, 7, 7, 10, 19, 10)]

# TODO für Yorik: moduldbparser einbauen
def create_df_modul_db() -> pd.DataFrame:
    """"
    This function creates a data frame from all modul db data.
    :return: A Data Frame with all modul_db data
    """
    # TODO für später: Pfad rausnehmen
    df_modul_db = pd.read_csv("..\\..\\Test\\data\\moduldb_df.csv")
    return df_modul_db

def sql_query_lecture(semester: str, prof_name: str, prof_firstname: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that retrieves all lectures held by a professor in a semester.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param prof_name: Last name of the professor for the search query.
    :param prof_firstname: First name of the professor for the search query.
    :param db A SQL database.
    :return: The lectures given by the :prof in the :semester.
    """
    result = db.execute("SELECT Lecture.name "
                        "FROM Dozs INNER JOIN Person INNER JOIN Lecture "
                        "ON dozs.doz = person.'@key' AND dozs.semester = lecture.semester AND dozs.semester = person.semester "
                        "AND dozs.'@key' = lecture.'@key'"
                        "WHERE lecture.semester =? AND person.lastname =? AND person.firstname =?", (semester, prof_name, prof_firstname))

    return result

def create_lecture_df(db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a data frame from all lectures given by Best Profs in their winning year.
    :param db A SQL database.
    :return: A Data Frame with the lectures given by the :prof in the :semester.
    """
    # Data Frame, which stores the winning lectures with place and year.
    df_lec = pd.DataFrame()

    # Iterates through winner and determines winner's lectures for each semester.
    for elem in winner:
        # Lastname of the professor.
        prof_lastname = elem[0]
        # Lastname of the professor.
        prof_firstname = elem[1]
        # Year of the award.
        year = elem[2]
        # Matching winter semester to year. Award refers to winter semester started last year.
        winter_sem = str(elem[2] - 1) + "w"
        # Matching summer semester to year. Award refers to the current summer semester.
        summer_sem = str(elem[2]) + "s"
        # Award placement.
        place = elem[3]

        # SQL query result, which determines the lectures given by the winning professors for each semester.
        result_summer = sql_query_lecture(summer_sem, prof_lastname, prof_firstname, db)
        result_winter = sql_query_lecture(winter_sem, prof_lastname, prof_firstname, db)

        # Saves the result of the SQL query to a list.
        lectures_summer = [elem[0] for elem in result_summer]
        lectures_winter = [elem[0] for elem in result_winter]

        # Filters all exercises
        filtered_lectures_winter = []
        for ele in lectures_winter:
            if "Übung" not in ele:
                if "übung" not in ele:
                    if "Exercise" not in ele:
                        filtered_lectures_winter.append(ele)

        filtered_lectures_summer = []
        for ele in lectures_summer:
            if "Übung" not in ele:
                if "übung" not in ele:
                    if "Exercise" not in ele:
                        filtered_lectures_summer.append(ele)

        # Creates and stores all found lectures in a temporary data frame with the matching year and placement.
        df_temp_winter = pd.DataFrame()
        df_temp_summer = pd.DataFrame()

        df_temp_winter['Vorlesungen'] = filtered_lectures_winter
        df_temp_winter['Jahr'] = year
        df_temp_winter['Semester'] = winter_sem
        df_temp_winter['Platz'] = place

        df_temp_summer['Vorlesungen'] = filtered_lectures_summer
        df_temp_summer['Jahr'] = year
        df_temp_summer['Semester'] = summer_sem
        df_temp_summer['Platz'] = place

        # Combines the temporary data frame with the lecture data frame.
        df_temp = pd.concat([df_temp_summer, df_temp_winter])
        df_lec = pd.concat([df_lec, df_temp])

    # Prints the data frame and removes missing values.
    return df_lec.dropna()

def sql_query_all_moduls(semester: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that searches out all ECTS of the winning lectures.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param db A SQL database.
    :return: The lecture name, ects, expected number of participants, lecturer last name and first name for all computer science moduls for given :semester.
    """
    result = db.execute("SELECT L.name, L.Ects_cred, turnout, p.lastname, p.firstname "
                        "FROM Lecture L INNER JOIN orgunits o on L.semester = o.semester and L.'@key' = o.'@key' "
                        "INNER JOIN dozs d on L.semester = d.semester and L.'@key' = d.'@key' "
                        "INNER JOIN Person P on d.doz = P.'@key' AND d.semester = P.semester "
                        "WHERE o.Semester = ? AND orgunit = 'Institut für Informatik' ", semester)
    return result

def create_df_all_moduls(db: sqlalchemy.engine.Engine):
    """
    This function creates a data frame with data on all computer science modules offered in the Best Prof Award years.
    :param db A SQL database.
    :return: A data frame, that stores all lecture names, lecturer last name and first name, ects, expected number of participants, year and semester.
    """
    # Data Frame, which stores all modul data.
    df_all_moduls = pd.DataFrame()

    for x in winner:
        # Year of the award.
        year = x[2]
        # Matching winter semester to year. Award refers to winter semester started last year.
        winter_sem = str(x[2] - 1) + "w"
        # Matching summer semester to year. Award refers to the current summer semester.
        summer_sem = str(x[2]) + "s"

        # SQL query result that determines all lectures of the Institute of Computer Science for each semester.
        result_winter = sql_query_all_moduls(winter_sem, db)
        result_summer = sql_query_all_moduls(summer_sem, db)

        # Saves the result of the SQL query to a list.
        result_winter = [x for x in result_winter]
        result_summer = [x for x in result_summer]

        # Filters all exercises
        filtered_list_summer = []
        for ele in result_summer:
            if "Übung" not in ele[0]:
                if "übung" not in ele[0]:
                    if "Exercise" not in ele[0]:
                        filtered_list_summer.append(ele)

        filtered_list_winter = []
        for ele in result_winter:
            if "Übung" not in ele[0]:
                if "übung" not in ele[0]:
                    if "Exercise" not in ele[0]:
                        filtered_list_winter.append(ele)

        df_temp = pd.DataFrame()

        for y in filtered_list_summer:
            df_temp1 = pd.DataFrame()
            df_temp1['Vorlesungen'] = [y[0]]
            df_temp1['Nachname'] = [y[3]]
            df_temp1['Vorname'] = [y[4]]
            df_temp1['Teilnehmerzahl'] = [y[2]]
            df_temp1['ECTS'] = [y[1]]
            df_temp1['Jahr'] = [year]
            df_temp1['Semester'] = [summer_sem]
            df_temp1['Platz'] = "Durchschnitt aller Module"

            df_temp = pd.concat([df_temp, df_temp1])

        df_temp3 = pd.DataFrame()

        for y in filtered_list_winter:
            df_temp2 = pd.DataFrame()
            df_temp2['Vorlesungen'] = [y[0]]
            df_temp2['Nachname'] = [y[3]]
            df_temp2['Vorname'] = [y[4]]
            df_temp2['Teilnehmerzahl'] = [y[2]]
            df_temp2['ECTS'] = [y[1]]
            df_temp2['Jahr'] = [year]
            df_temp2['Semester'] = [winter_sem]
            df_temp2['Platz'] = "Durchschnitt aller Module"

            df_temp3 = pd.concat([df_temp3, df_temp2])

        # Combines the temporary data frame with the modul data frame.
        df_all_moduls = pd.concat([df_temp, df_temp3, df_all_moduls])

    return df_all_moduls

def calculates_num_of_moduls(df_lecture: pd.DataFrame, df_all_moduls: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the number of modules that took place in the winning year.
    :param df_lecture: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param df_all_moduls: Data frame with all computer science moduls data (get by create_df_all_moduls()).
    :return: The number of modules given by a prof in the year.
    """
    # Data Frame, which stores the year, place and the number of modules that took place in the winning year.
    df_count_lec = pd.DataFrame(columns=['Jahr', 'Platz', 'Modulanzahl'])
    # index
    i = 0

    # Iterates through winner and determines Number of modules per year and place.
    for x in winner:
        # Year of the award.
        year = x[2]
        # Award placement.
        place = x[3]

        # Data frame containing all modules of one year and one place.
        df_sort = df_lecture.loc[df_lecture.Jahr.eq(year) & df_lecture.Platz.eq(place)]

        # Adds a new column to df_count_lec.
        df_count_lec.loc[i] = [year, str(place), len(df_sort)]

        i += 1

    # Calculates the average total number of all modules of a person per year
    df_count_all = df_all_moduls.groupby(['Nachname', 'Vorname', 'Jahr', 'Platz'])['Nachname'].count().reset_index(name='Anzahl Module')
    df_sum = df_count_all.groupby(['Jahr', 'Platz'])['Anzahl Module'].sum().reset_index(name='Summe')
    df_count = df_count_all.groupby(['Jahr', 'Platz'])['Anzahl Module'].count().reset_index(name='Anzahl')
    df_count['Modulanzahl'] = df_sum['Summe']/df_count['Anzahl']
    del df_count['Anzahl']

    # Combines the two data frames.
    df_count_lec = pd.concat([df_count, df_count_lec], ignore_index=True)

    return df_count_lec

def sql_query_ects(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that searches out all ECTS of the winning lectures.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: The ECTS given by the :lecture in the :semester.
    """
    result = db.execute("SELECT Ects_cred FROM Lecture "
                        "WHERE Semester = ? AND Name = ? ", (semester, lecture_name))
    return result

def create_ects_df(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a list of data frames sorted by place from all
    ects of lectures given by Best Profs in their winning year.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A data frame from all ects of lectures.
    """
    # Data frame that stores the ECTS with the placement.
    df_ects = pd.DataFrame()

    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = x[2]
        # Award placement.
        place = x[3]

        # SQL query result, which determines the lectures given by the winning professors for each semester.
        result = sql_query_ects(semester, lec, db)

        # Saves the result of the SQL query to a list.
        ects = [x[0] for x in result]

        # Creates and stores all found lectures in a temporary data frame with the matching year and placement.
        df_temp = pd.DataFrame()
        df_temp['ECTS'] = ects
        df_temp['Jahr'] = year
        df_temp['Semester'] = semester
        df_temp['Platz'] = str(place)

        # Combines the temporary data frame with the ects data frame.
        df_ects = pd.concat([df_ects, df_temp])

    # Creates DataFrames with a continuous index.
    ects = df_ects.values.tolist()
    df_ects = pd.DataFrame(ects, columns=['ECTS', 'Jahr', 'Semester', 'Platz'])

    # Prints the data frame and removes missing values.
    return df_ects.dropna()

def sql_query_language(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that outputs whether a given module has English or German as the teaching language in a semester.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: 1 if the language is english, otherwise 0
    """
    result = db.execute("SELECT englisch FROM Lecture "
                        "WHERE Semester = ? AND name = ?", (semester, lecture_name))
    return result

def create_lecture_language(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a data frame that finds out for all lectures whether they were held in English or not.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A data frame that stores to lectures 1 for English speaking, 0 otherwise.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the winning lectures with place and year.
    df_lan = pd.DataFrame()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = x[2]
        # Award placement.
        place = x[3]

        # SQL query result that determines the language for lectures of the winning professors for each semester.
        result = sql_query_language(semester, lec, db)

        # Saves the result of the SQL query to a list.
        english = [x[0] for x in result]

        # Creates and stores all found lectures in a temporary data frame with the matching year and placement.
        df_temp = pd.DataFrame()
        for y in english:
            if y == 1:
                df_temp['Englisch'] = [1]
                df_temp['Deutsch'] = [0]
            else:
                df_temp['Englisch'] = [0]
                df_temp['Deutsch'] = [1]
            df_temp['Jahr'] = [year]
            df_temp['Semester'] = [semester]
            df_temp['Platz'] = [place]

        # Combines the temporary data frame with the lecture data frame.
        df_lan = pd.concat([df_lan, df_temp])

    # Creates DataFrames with a continuous index.
    language = df_lan.values.tolist()
    df_language = pd.DataFrame(language, columns=['Englisch', 'Deutsch', 'Jahr', 'Semester', 'Platz'])

    # Prints the data frame and removes missing values.
    return df_language.dropna()

def count_lecture_language(df_language: pd.DataFrame) -> pd.DataFrame:
    """
    This function count the number of modules they were held in English or not.
    :param df_language: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_language()).
    :return: The number of englisch & german modules given in the year.
    """
    # Data Frame, which stores the year, place and the number of modules that took place in the winning year.
    df_count_language = pd.DataFrame(columns=['Jahr', 'Anzahl', 'Sprache'])

    # Index of the data frame.
    i = 0
    # A list of all best Prof award years.
    year_list = [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]

    # Iterates through winner and determines Number of modules per year and place.
    for year in year_list:
        # Data frame containing all modules of one year and one place.
        count_eng = df_language[(df_language.Englisch == 1) & (df_language.Jahr == year)].sum().tolist()
        count_ger = df_language[(df_language.Deutsch == 1) & (df_language.Jahr == year)].sum().tolist()

        # Adds a new column to df_countLec.
        df_count_language.loc[i] = [year, count_ger[1], "deutsch"]
        df_count_language.loc[i + 1] = [year, count_eng[0], "englisch"]
        # Increments the index by one
        i += 2

    return df_count_language

def sql_query_num_of_participants(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that searches out the expected number of participants for the modules.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: The expected number of participants.
    """
    result = db.execute("SELECT turnout FROM Lecture "
                        "WHERE Semester = ? AND Name = ? ", (semester, lecture_name))
    return result

def create_num_of_participants(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a data frame, with the expected number of participants for the modules.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A data frame that stores the expected number of participants for the modules.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the winning lectures with place and year.
    df_num = pd.DataFrame()

    previous_year = 2019
    previous_place = 1
    count_numbers = 0
    length = len(lecture_list)

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for i in range(length):
        # Name of the lecture.
        lec = lecture_list[i][0]
        # Year of the award.
        year = lecture_list[i][1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = lecture_list[i][2]
        # Award placement.
        place = lecture_list[i][3]

        # SQL query result that determines the language for lectures of the winning professors for each semester.
        result = sql_query_num_of_participants(semester, lec, db)

        # Saves the result of the SQL query to a list.
        number = [x[0] for x in result]
        df_temp = pd.DataFrame()
        if i == (length - 1):
            if number[0] is not None:
                count_numbers += number[0]

            df_temp['Teilnehmerzahl'] = [count_numbers]
            df_temp['Jahr'] = [year]
            df_temp['Platz'] = [str(place)]
        else:
            if (year == previous_year) & (place == previous_place):
                if number[0] is not None:
                    count_numbers += number[0]
            else:
                # Creates and stores all found numbers in a temporary data frame with the matching year and placement.
                df_temp['Teilnehmerzahl'] = [count_numbers]
                df_temp['Jahr'] = [previous_year]
                df_temp['Platz'] = [str(previous_place)]

                if number[0] is not None:
                    count_numbers = number[0]

                previous_year = year
                previous_place = place

        # Combines the temporary data frame with the lecture data frame.
        df_num = pd.concat([df_num, df_temp])

    # Creates DataFrames with a continuous index.
    language = df_num.values.tolist()
    df_participants = pd.DataFrame(language, columns=['Teilnehmerzahl', 'Jahr', 'Platz'])

    # Prints the data frame and removes missing values.
    return df_participants.dropna()

def sql_query_orgname(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that searches out the associated orgname for the modules.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: The associated orgname for the modules
    """
    result = db.execute("SELECT orgname FROM Lecture "
                        "WHERE Semester = ? AND Name = ? ", (semester, lecture_name))
    return result
def create_orgname(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a data frame, with the associated orgname for the modules.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A data frame that stores the associated orgname for the modules.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the orgname with place and year.
    df_org = pd.DataFrame()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = x[2]
        # Award placement.
        place = x[3]

        # SQL query result that determines the orgname for lectures of the winning professors for each semester.
        result = sql_query_orgname(semester, lec, db)

        # Saves the result of the SQL query to a list.
        orgname = [x[0] for x in result]

        # Creates and stores all found lectures in a temporary data frame with the matching year and placement.
        df_temp = pd.DataFrame()
        for y in orgname:
            df_temp['Organisation'] = [y]
            df_temp['Jahr'] = [str(year)]
            df_temp['Platz'] = [str(place)]

        # Combines the temporary data frame with the lecture data frame.
        df_org = pd.concat([df_org, df_temp])

    # Since 2018 computer engineering means distributed systems
    df_org.loc[df_org.Organisation == "Technische Informatik", 'Organisation'] = 'Verteilte Systeme'
    df_org.loc[df_org.Organisation == "Technische Informatik [ab dem 1.10.2018: Verteilte Systeme]", 'Organisation'] = 'Verteilte Systeme'
    df_org.loc[df_org.Organisation == "Fachdidaktik Informatik", 'Organisation'] = 'Didaktik der Informatik'
    # Shorten the names for better presentation.
    df_org.loc[df_org.Organisation == "Institut für Experimentelle und Angewandte Physik (Sektion Physik)", 'Organisation'] = 'Institut für Experimentelle & Angewandte Physik'
    df_org.loc[df_org.Organisation == "Algorithmische Optimale Steuerung - CO2-Aufnahme des Meeres", 'Organisation'] = 'Algorithmische Optimale Steuerung'
    df_org.loc[df_org.Organisation == "Programmiersprachen und Übersetzerkonstruktion", 'Organisation'] = 'Programmiersprachen & Übersetzerkonstruktion'
    df_org.loc[df_org.Organisation == "Integrated School of Ocean Sciences (ISOS)", 'Organisation'] = 'Integrated School of Ocean Sciences'
    # Prints the data frame and removes missing values.
    return df_org.groupby(['Jahr', 'Platz', 'Organisation'])['Organisation'].count().reset_index(name='Anzahl')

def sql_query_modul_time(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that outputs weekdays, start and end time of a module.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: Weekdays, start and end time of a module.
    """
    result = db.execute("SELECT terms.starttime, terms.endtime, terms.repeat "
                        "FROM Lecture INNER JOIN  terms on Lecture.'@key' = terms.'@key' "
                        "WHERE lecture.semester =? AND lecture.name= ? AND Lecture.semester = terms.semester", (semester, lecture_name))
    return result

def create_modul_time(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> pd.DataFrame:
    """
    This function creates a data frame with the lecture times.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A data frame that stores times for the modules.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the times with place and year.
    df_time = pd.DataFrame()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = x[2]
        # Award placement.
        place = x[3]

        # SQL query result that determines the times for lectures of the winning professors for each semester.
        result = sql_query_modul_time(semester, lec, db)

        # Saves the result of the SQL query to a list.
        modul_time = [x for x in result]

        # Converts the database description for days to day names.
        temp = []
        for y in modul_time:
            time = None
            match y[0]:
                case "8:00" | "8:15" | "8:30" | "9:00":
                    time = "8:00"
                case "10:00" | "10:05" | "10:15" | "10:30":
                    time = "10:00"
                case "12:00" | "12:05" | "12:15" | "12:30" | "13:00":
                    time = "12:00"
                case "14:00" | "14:14" | "15:00":
                    time = "14:00"
                case "16:00" | "16:05" | "16:15":
                    time = "16:00"
                case "18:00" | "18:15":
                    time = "18:00"

            match y[2]:
                case "w1 1" | "w2 1":
                    days = "Montag"
                    temp += [(year, str(place), time, y[1], days)]
                case "w1 2" | "w2 2":
                    days = "Dienstag"
                    temp += [(year, str(place), time, y[1], days)]
                case "w1 3" | "w2 3":
                    days = "Mittwoch"
                    temp += [(year, str(place), time, y[1], days)]
                case "w1 4" | "w2 4":
                    days = "Donnerstag"
                    temp += [(year, str(place), time, y[1], days)]
                case "w1 5" | "w2 5":
                    days = "Freitag"
                    temp += [(year, str(place), time, y[1], days)]
                case "w1 6" | "w2 6":
                    days = "Samstag"
                    temp += [(year, str(place), time, y[1], days)]

        # Creates and stores all found times in a temporary data frame with the matching year and placement.
        df_temp = pd.DataFrame(temp, columns=['Jahr', 'Platz', 'Startzeit', 'Endzeit', 'Tag'])

        # Combines the temporary data frame with the time data frame.
        df_time = pd.concat([df_time, df_temp])

    # Creates DataFrames with a continuous index.
    time_list = df_time.values.tolist()
    df_modul_time = pd.DataFrame(time_list, columns=['Jahr', 'Platz', 'Startzeit', 'Endzeit', 'Tag'])

    # Prints the data frame and removes missing values.
    return df_modul_time.dropna()

def sql_query_exam_date(semester: str, lecture_name: str, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that outputs exam dates.
    :param semester: Semester for the search query in the format '2021w' for winter and '2021s' for summer.
    :param lecture_name: Name of the lecture for the search query.
    :param db A SQL database.
    :return: The exam dates for a module.
    """
    result = db.execute("SELECT E.startdate "
                        "FROM Lecture INNER JOIN Event E on Lecture.'@key' = E.dbref "
                        "WHERE Lecture.semester = ? AND lecture.name = ? AND Lecture.semester = E.semester ", (semester, lecture_name))
    return result

def create_exam_date(df_lec: pd.DataFrame, db: sqlalchemy.engine.Engine) -> [pd.DataFrame]:
    """
    This function creates a data frame with the Distribution of examinations in the examination period.
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :param db A SQL database.
    :return: A list of data frames that stores times and counts for the modules.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the dates with place and year.
    df_exam = pd.DataFrame()
    df_count = pd.DataFrame()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Matching semester to year. Award refers to winter semester started last year.
        semester = x[2]
        # Award placement.
        place = x[3]

        # SQL query result that determines exam dates for lectures of the winning professors for each semester.
        result = sql_query_exam_date(semester, lec, db)

        # Saves the result of the SQL query to a list.
        exam_dates_list = [x[0] for x in result]
        # Converts a list to a set
        exam_dates_set = set(exam_dates_list)

        # Calculates number of days remaining until the test from the beginning of the period.
        exam_list = []
        count_list = []
        for y in exam_dates_set:
            # "2021-08-19" --> ['2021', '08', '19']
            exam_date_list = y.split('-')
            exam_date_list[0] = int(exam_date_list[0])
            exam_date_list[1] = int(exam_date_list[1])
            exam_date_list[2] = int(exam_date_list[2])
            # (2021, 8, 19) --> 2021-08-19
            exam_date = datetime.date(exam_date_list[0], exam_date_list[1], exam_date_list[2])

            # The exam date is for the lecture in this year.
            if exam_date_list[0] == year:
                # Determines correct examination period.
                for z in exam_periods:      # ("2009w", 11, 2, 24, 2, 29, 3, 9, 4)
                    # Checks if you are in the right semester of the exam period.
                    if semester == z[0]:
                        first_period_start = datetime.date(year, z[2], z[1])
                        first_period_end = datetime.date(year, z[4], z[3])
                        second_period_start = datetime.date(year, z[6], z[5])
                        second_period_end = datetime.date(year, z[8], z[7])
                        # The exam date is in the first period.
                        if (exam_date >= first_period_start) & (exam_date <= first_period_end):
                            number = exam_date - first_period_start
                            exam_list += [(year, str(place), number.days)]
                        # The exam date is in the second period.
                        elif (exam_date >= second_period_start) & (exam_date <= second_period_end):
                            number = exam_date - second_period_start
                            exam_list += [(year, str(place), number.days)]
                        # The exam date is not in a period.
                        else:
                            count_list += [(year, str(place), 1)]

        # Creates and stores all found times in a temporary data frame with the matching year and placement.
        df_temp1 = pd.DataFrame(exam_list, columns=['Jahr', 'Platz', 'Anzahl'])
        df_temp2 = pd.DataFrame(count_list, columns=['Jahr', 'Platz', 'Anzahl außerhalb PZ'])

        # Combines the temporary data frame with the exam data frame.
        df_exam = pd.concat([df_exam, df_temp1])
        df_count = pd.concat([df_count, df_temp2])

    # Prints the data frame and removes missing values.
    return [df_exam.dropna(), df_count.dropna()]

def create_required_moduls(df_modul_db: pd.DataFrame, df_lec: pd.DataFrame) -> pd.DataFrame:
    """
    This function checks if a module is a mandatory module and stores all mandatory modules per year in a dataframe.
    :param df_modul_db: A Data Frame with all modul_db data (get by create_df_modul_db()).
    :param df_lec: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    :return: A data frame with all required moduls per year.
    """
    # Creates a list from the data frame of all winning lectures.
    lecture_list = df_lec.values.tolist()

    # Data Frame, which stores the dates with place and year.
    df_required_moduls = pd.DataFrame()

    # Iterates through lecture_list and determines winner's lectures for each semester.
    for x in lecture_list:
        # Name of the lecture.
        lec = x[0]
        # Year of the award.
        year = x[1]
        # Award placement.
        place = x[3]

        lecture_split = lec.split(":")

        # Checks if module is a required module
        contain_values = df_modul_db[df_modul_db['Unnamed: 0'].str.contains(lecture_split[0], regex=False)]
        df_temp = contain_values[contain_values['kategorien'].str.contains('Pflichtmodul', regex=False)]
        df_temp1 = contain_values[contain_values['kategorien'].str.contains('Grundmodul', regex=False)]
        df_temp2 = contain_values[contain_values['kategorien'].str.contains('Aufbaumodul', regex=False)]
        df_temp3 = contain_values[contain_values['kategorien'].str.contains('Vertiefungsmodule', regex=False)]

        df_required = pd.concat([pd.concat([df_temp, df_temp1]), pd.concat([df_temp2, df_temp3])])

        if df_required.empty:
            df_temp4 = pd.DataFrame([(year, str(place), lec, 0)], columns=['Jahr', 'Platz', 'Modulname', 'Pflichtmodul'])
        else:
            df_temp4 = pd.DataFrame([(year, str(place), lec, 1)], columns=['Jahr', 'Platz', 'Modulname', 'Pflichtmodul'])

        # Combines the temporary data frame with the exam data frame.
        df_required_moduls = pd.concat([df_required_moduls, df_temp4])

    return df_required_moduls

def visualization_num_of_moduls(df_count_lec: pd.DataFrame):
    """
    This function visualizes the number of modules that took place in the winning year.
    :param df_count_lec: Data Frame, which stores the year, place and the number of modules that
                        took place in the winning year (get by calculates_num_of_moduls())
    """
    # Visualization of the number of modules held in the winning year.
    fig = px.bar(df_count_lec, x="Jahr", y="Modulanzahl", color="Platz", barmode='group', title="Anzahl der Module", color_discrete_map={
        '1': 'blue', '2': 'red', '3': 'green', 'Durchschnitt aller Module': 'yellow'})
    return fig

def visualization_num_of_moduls_trend(df_count_lec: pd.DataFrame):
    """
    This function visualizes the trend of the number of modules that took place in the winning year.
    :param df_count_lec: Data Frame, which stores the year, place and the number of modules that
                        took place in the winning year (get by calculates_num_of_moduls())
    """
    fig = px.scatter(df_count_lec, x="Jahr", y="Modulanzahl", color='Platz', title="Trend für Anzahl der Module", trendline='lowess',
                     range_y=[0, 20], color_discrete_map={'1': 'blue', '2': 'red', '3': 'green', 'Durchschnitt aller Module': 'yellow'})
    return fig

def visualization_lecture(df_lecture: pd.DataFrame):
    """
    This function visualizes the most common modules.
    :param df_lecture: Data frame from all lectures given by Best Profs in their winning year (get by create_lecture_df()).
    """
    df_count = df_lecture.groupby(['Vorlesungen'])['Vorlesungen'].count().reset_index(name='Anzahl')
    # Shows all modules that occur more than 3 times.
    df_vis = df_count.query('Anzahl > 3')
    fig = px.bar(df_vis, x='Vorlesungen', y='Anzahl', barmode="group", title="Die häufigsten Module",
                 color_discrete_sequence=px.colors.sequential.Rainbow_r)
    return fig

def visualization_ects_lineplot_year(df_ects: pd.DataFrame, df_all_moduls: pd.DataFrame):
    """
    This function visualizes all ects of lectures given by Best Profs in their winning year with a lineplot.
    :param df_ects: Data frame from all ects of lectures (get by create_ects_df()).
    :param df_all_moduls: Data frame with all computer science moduls data (get by create_df_all_moduls()).
    """
    # Calculates the ECTS average value per year for all best Prof moduls.
    df_sum = df_ects.groupby(['Jahr', 'Platz'])['ECTS'].sum().reset_index(name='Summe')
    df_count = df_ects.groupby(['Jahr', 'Platz'])['ECTS'].count().reset_index(name='Anzahl')
    df_medium = pd.merge(df_sum, df_count, how='left', on=['Jahr', 'Platz'])
    df_medium['ECTS Mittelwert'] = df_medium['Summe']/df_medium['Anzahl']

    # Calculates the ECTS average value per year and person for all moduls.
    df_sum1 = df_all_moduls.groupby(['Nachname', 'Vorname', 'Jahr', 'Semester', 'Platz'])['ECTS'].sum().reset_index(name='Summe ETCS')
    df_count1 = df_all_moduls.groupby(['Nachname', 'Vorname', 'Jahr', 'Semester', 'Platz'])['Nachname'].count().reset_index(name='Anzahl Module')
    df_count1['ECTS'] = df_sum1['Summe ETCS'] / df_count1['Anzahl Module']

    # Calculates the ECTS average value of all persons per year for all moduls.
    df_sum2 = df_count1.groupby(['Jahr', 'Platz'])['ECTS'].sum().reset_index(name='Summe')
    df_count2 = df_count1.groupby(['Jahr', 'Platz'])['Anzahl Module'].count().reset_index(name='Anzahl')
    df_average = pd.merge(df_sum2, df_count2, how='left', on=['Jahr', 'Platz'])
    df_average['ECTS Mittelwert'] = df_average['Summe']/df_average['Anzahl']

    df_ects_all = pd.concat([df_medium, df_average], ignore_index=True)

    # Visualization of all average ects.
    fig = px.line(df_ects_all, x='Jahr', y='ECTS Mittelwert', color='Platz', title='Mittelwert der ECTS pro Jahr',
                  color_discrete_map={'1': 'blue', '2': 'red', '3': 'green', 'Durchschnitt aller Module': 'yellow'})
    return fig

def visualization_ects_scatterplot_winter(df_ects: pd.DataFrame):
    """
    This function visualizes all ects of lectures given by Best Profs in their winning winter semester with a scatterplot.
    :param df_ects: Data frame from all ects of lectures (get by create_ects_df()).
    """
    # Selected winter semester
    df_ects_winter = df_ects[df_ects['Semester'].str.contains('w')]

    # Visualizes data with a lineplot
    fig = px.scatter(df_ects_winter, x='Semester', y='ECTS', color="Platz", title='Verteilung der ECTS im Wintersemester',
                     category_orders={"Semester": ["2009w", "2010w", "2011w", "2012w", "2013w", "2014w", "2015w",
                                                   "2016w", "2017w", "2018w"]}, range_y=[0, 18])
    return fig

def visualization_ects_scatterplot_summer(df_ects: pd.DataFrame):
    """
    This function visualizes all ects of lectures given by Best Profs in their winning summer semester with a scatterplot.
    :param df_ects: Data frame from all ects of lectures (get by create_ects_df()).
    """
    # Selected summer semester
    df_ects_summer = df_ects[df_ects['Semester'].str.contains('s')]

    # Visualizes data with a lineplot
    fig = px.scatter(df_ects_summer, x='Semester', y='ECTS', color="Platz", title='Verteilung der ECTS im Sommersemester',
                     category_orders={"Semester": ["2010s", "2011s", "2012s", "2013s", "2014s", "2015s",
                                                   "2016s", "2017s", "2018s", "2019s"]}, range_y=[0, 18])
    return fig

def visualization_language_bar_plot(df_count_language: pd.DataFrame):
    """
    This function visualizes all englisch lectures given by Best Profs in their winning year with a barplot.
    :param df_count_language: A data frame that stores the number of english and german speaking moduls per year (get by count_lecture_language()).
    """
    fig = px.bar(df_count_language, x="Jahr", y="Anzahl", color='Sprache', title='Sprache der gehaltenen Module')
    return fig

def visualization_language_pie(df_count_language: pd.DataFrame):
    """
    This function visualizes the best Prof modul language in percent with a pie chart.
    :param df_count_language: A data frame that stores the number of english and german speaking moduls per year (get by count_lecture_language()).
    """
    df_language_all = df_count_language.groupby(['Sprache'])['Anzahl'].sum().reset_index(name='Anzahl')
    fig = px.pie(df_language_all, values='Anzahl', names='Sprache', title="Sprachverteilung Best Prof Module",
                 color_discrete_sequence=px.colors.sequential.Rainbow_r)
    return fig
def visualization_language_modul_db(df_modul_db: pd.DataFrame):
    """
    This function visualizes the best Prof modul language in percent with a pie chart.
    :param df_modul_db: A data frame that stores all data of modul db (get by create_df_modul_db()).
    """
    df_modul_db_language = df_modul_db.groupby(['lehrsprache'])['lehrsprache'].count().reset_index(name='Anzahl')
    # Visualization the language of modules
    fig = px.pie(df_modul_db_language, values='Anzahl', names='lehrsprache', title="Sprachverteilung sämtlicher Informatikmodule",
                 color_discrete_sequence=px.colors.sequential.Rainbow_r)
    return fig

def visualization_participant_lineplot(df_participants: pd.DataFrame, df_all_moduls: pd.DataFrame):
    """
    This function visualizes all expected number of participants for a module given by Best Profs in their winning year with a lineplot.
    :param df_all_moduls: Data frame with all computer science moduls data (get by create_df_all_moduls()).
    :param df_participants: A data frame that stores all expected number of participants (get by create_num_of_participants()).
    """
    # Calculates the participants per year and person for all moduls.
    df_sum1 = df_all_moduls.groupby(['Nachname', 'Vorname', 'Jahr', 'Platz'])['Teilnehmerzahl'].sum().reset_index(name='Summe Teilnehmer')
    df_count1 = df_all_moduls.groupby(['Nachname', 'Vorname', 'Jahr', 'Platz'])['Nachname'].count().reset_index(name='Anzahl Module')

    # Calculates the participants average value of all persons per year for all moduls.
    df_sum2 = df_sum1.groupby(['Jahr', 'Platz'])['Summe Teilnehmer'].sum().reset_index(name='Summe')

    df_count2 = df_count1.groupby(['Jahr', 'Platz'])['Anzahl Module'].count().reset_index(name='Anzahl')

    df_average = pd.merge(df_sum2, df_count2, how='left', on=['Jahr', 'Platz'])
    df_average['Teilnehmerzahl'] = df_average['Summe']/df_average['Anzahl']

    df_participants_all = pd.concat([df_participants, df_average], ignore_index=True)
    fig = px.line(df_participants_all, x="Jahr", y="Teilnehmerzahl", color="Platz", title='Anzahl der erwarteten Teilnehmer',
                  color_discrete_map={'1': 'blue', '2': 'red', '3': 'green', 'Durchschnitt aller Module': 'yellow'})
    return fig

def visualization_participant_average(df_participants: pd.DataFrame, df_count_lecture: pd.DataFrame):
    """
    This function visualizes the average of all expected number of participants per year or modul.
    :param df_participants: A data frame that stores all expected number of participants (get by create_num_of_participants()).
    :param df_count_lecture: Data Frame, which stores the year, place and the number of modules that
                        took place in the winning year (get by calculates_num_of_moduls())
    """
    df_sum_participants = df_participants.groupby(['Platz'])['Teilnehmerzahl'].sum().reset_index(name='Anzahl')
    df_sum_participants['Teilnehmerdurchschnitt pro Jahr'] = df_sum_participants['Anzahl']/10

    df_lecture_participants = df_count_lecture.groupby(['Platz'])['Modulanzahl'].sum().reset_index(name='Anzahl')
    df_lecture_participants['Teilnehmerdurchschnitt pro Modul'] = df_sum_participants['Anzahl']/df_lecture_participants['Anzahl']

    df_participants_average = pd.merge(df_sum_participants, df_lecture_participants, how='left', on=['Platz'])
    fig = px.bar(df_participants_average, x="Platz", y=["Teilnehmerdurchschnitt pro Modul", "Teilnehmerdurchschnitt pro Jahr"],
                 barmode="group", labels={"value": "Anzahl", "variable": "Durchschnitt"})
    return fig


def visualization_orgname_place(df_orgname: pd.DataFrame):
    """
    This function visualizes the associated orgname for a module given by Best Profs in their winning year with a bar plot grouped by place.
    :param df_orgname: A data frame that stores all expected number of participants (get by create_orgname()).
    """
    fig = px.bar(df_orgname, x="Organisation", y="Anzahl", color='Platz', title='Arbeitsgruppen der Awardmodule - Platzierungsübersicht',
                 animation_frame="Jahr")
    fig["layout"].pop("updatemenus")
    fig.update_layout(font=dict(size=10))
    return fig

def visualization_orgname_all(df_orgname: pd.DataFrame):
    """
    This function visualizes the associated orgname for a module given by Best Profs in their winning year with a bar plot.
    :param df_orgname: A data frame that stores all expected number of participants (get by create_orgname()).
    """
    fig = px.bar(df_orgname, x="Organisation", y="Anzahl", color='Jahr', title='Arbeitsgruppen der Awardmodule - Gesamtübersicht',
                 range_y=[0, 60], category_orders={"Organisation": ['Echtzeitsysteme / Eingebettete Systeme', 'Software Engineering',
                                                                'Diskrete Optimierung', 'Theoretische Informatik',
                                                                'Programmiersprachen & Übersetzerkonstruktion', 'Rechnergestützte Programmentwicklung',
                                                                'Verteilte Systeme', 'Scientific Computing',
                                                                'Algorithmische Optimale Steuerung',
                                                                'Institut für Experimentelle & Angewandte Physik',
                                                                'Integrated School of Ocean Sciences',
                                                                'Angewandte Informatik (Wirtschaftsinformatik)',
                                                                'Numerik und Optimierung', 'Informationssysteme',
                                                                'Algorithmen und Komplexität', 'Didaktik der Informatik']})
    return fig

def visualization_modul_time_days(df_modul_time: pd.DataFrame):
    """
    This function visualizes the favorite modul days animated per year.
    :param df_modul_time: Data Frame, which stores times of modules (get by create_modul_time()).
    """
    df_days = df_modul_time.groupby(['Jahr', 'Platz', 'Tag'])['Tag'].count().reset_index(name='Anzahl')

    # Visualization of the days of modules grouped by year.
    fig = px.bar(df_days, x='Tag', y='Anzahl', color='Platz',  title="Beliebte Vorlesungstage",
                 animation_frame="Jahr", barmode='group',
                 category_orders={"Tag": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]}, range_y=[0, 10])
    # Controls the speed of the animation.
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    return fig

def visualization_modul_time_days_pie(df_modul_time: pd.DataFrame):
    """
    This function visualizes the favorite modul days in percent with a pie chart.
    :param df_modul_time: Data Frame, which stores times of modules (get by create_modul_time()).
    """
    df_days = df_modul_time.groupby(['Jahr', 'Platz', 'Tag'])['Tag'].count().reset_index(name='Anzahl')

    # Visualization of the days of modules in %.
    fig = px.pie(df_days, values='Anzahl', names='Tag', title="Beliebteste Vorlesungstage Gesamtübersicht",
                 category_orders={"Tag": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]})
    return fig

def visualization_modul_time_hours(df_modul_time: pd.DataFrame):
    """
    This function visualizes the favorite modul hours animated per year.
    :param df_modul_time: Data Frame, which stores times of modules (get by create_modul_time()).
    """
    df_hours = df_modul_time.groupby(['Jahr', 'Platz', 'Startzeit'])['Startzeit'].count().reset_index(name='Anzahl')

    # Visualization of the days of modules grouped by year.
    fig = px.bar(df_hours, x='Startzeit', y='Anzahl', color='Platz',  title="Beliebte Vorlesungsstartzeiten",
                 animation_frame="Jahr", barmode='group',
                 category_orders={"Startzeit": ["8:00", "10:00", "12:00",
                                                "14:00", "16:00", "18:00"]})
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    return fig

def visualization_modul_time_hours_pie(df_modul_time: pd.DataFrame):
    """
    This function visualizes the favorite modul times in percent with a pie chart.
    :param df_modul_time: Data Frame, which stores times of modules (get by create_modul_time()).
    """
    df_hours = df_modul_time.groupby(['Jahr', 'Platz', 'Startzeit'])['Startzeit'].count().reset_index(name='Anzahl')

    # Visualization of the days of modules in %.
    fig = px.pie(df_hours, values='Anzahl', names='Startzeit', title="Beliebteste Vorlesungsstartzeiten Gesamtübersicht",
                 category_orders={"Startzeit": ["8:00", "10:00", "12:00",
                                                "14:00", "16:00", "18:00"]}, color_discrete_sequence=px.colors.sequential.Rainbow_r)
    return fig

def visualization_exam_date_no_period(df_exam: [pd.DataFrame]):
    """
    This function visualizes the exam dates outside the periods.
    :param df_exam: List of Data Frames, which stores distribution & count of exam dates (get by create_exam_date()).
    """
    df_no_period = df_exam[1].groupby(['Jahr', 'Platz'])['Anzahl außerhalb PZ'].count().reset_index(name='Anzahl')

    # Visualization of the days of modules grouped by place.
    fig = px.bar(df_no_period, x='Jahr', y='Anzahl', color='Platz', barmode="group", title="Prüfungen außerhalb der Prüfungszeiträume",
                 category_orders={"Platz": ["1", "2", "3"]})
    return fig

def visualization_exam_date_in_period(df_exam: [pd.DataFrame]):
    """
    This function visualizes the exam dates in the periods.
    :param df_exam: List of Data Frames, which stores distribution & count of exam dates (get by create_exam_date()).
    """
    df_sum = df_exam[0].groupby(['Jahr', 'Platz'])['Anzahl'].sum().reset_index(name='Summe')
    df_in_period = df_exam[0].groupby(['Jahr', 'Platz'])['Anzahl'].count().reset_index(name='verbleibende Tage')
    df_sum['verbleibende Tage'] = df_sum["Summe"]/df_in_period["verbleibende Tage"]

    # Visualization of the days of modules grouped by place.
    fig = px.scatter(df_sum, x='Jahr', y='verbleibende Tage', color='Platz', trendline='lowess', title="Prüfungen innerhalb der Prüfungszeiträume",
                     category_orders={"Platz": ["1", "2", "3"]})
    return fig

def visualization_required_modul(df_required_moduls: pd.DataFrame):
    """
    This function visualizes how many modules are mandatory modules
    :param df_required_moduls: A data frame with all required moduls per year (get by create_required_moduls()).
    """

    df_sum = df_required_moduls.groupby(['Jahr', 'Platz'])['Pflichtmodul'].sum().reset_index(name='Anzahl Pflichtmodule')
    df_count = df_required_moduls.groupby(['Jahr', 'Platz'])['Pflichtmodul'].count().reset_index(name='Anzahl sonstiger Module')
    df_count['Anzahl sonstiger Module'] = df_count['Anzahl sonstiger Module'] - df_sum['Anzahl Pflichtmodule']
    df_all = pd.merge(df_count, df_sum)

    fig = px.bar(df_all, x='Jahr', y=['Anzahl sonstiger Module', 'Anzahl Pflichtmodule'], barmode="group", title="Verteilung Wahl-/Pflichtmodule")
    return fig

def sql_prediction_best_prof_2022_lecture(year: list, starttime: list, days: list, ects: list, orgname: list, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that retrieves all lectures that fit the above categories.
    :param year: A list of semesters.
    :param starttime: A list of lecture start times.
    :param days: A list of days, format 'w1 1' = weekly, Monday.
    :param ects: A list of ects.
    :param orgname: A list of organisations.
    :param db A SQL database.
    :return: all found lectures.
    """
    result = db.execute(f''' SELECT L.name FROM Lecture L INNER JOIN dozs d ON L.semester = d.semester AND L.[@key] = d.[@key] 
                            INNER JOIN Person P ON d.doz = P.[@key] AND d.semester = P.semester 
                            INNER JOIN Event E ON L.[@key] = E.dbref AND L.semester = E.semester 
                            INNER JOIN terms t ON L.[@key] = t.[@key] AND L.semester = t.semester 
                            WHERE L.semester IN {str(tuple(year))} 
                            AND t.starttime IN {str(tuple(starttime))} 
                            AND t.repeat IN {str(tuple(days))} 
                            AND L.ects_cred IN {str(tuple(ects))} 
                            AND L.orgname IN {str(tuple(orgname))}; ''')

    return result

def sql_prediction_best_prof_2022_prof(year: list, lecture: list, db: sqlalchemy.engine.Engine) -> list:
    """
    SQL query that retrieves all professors who held the given lectures
    :param year: A list of semesters.
    :param lecture: A list of lecture names.
    :param db A SQL database.
    :return: all persons with lastname and firstname.
    """
    result = db.execute(f''' SELECT person.lastname, person.firstname
                            FROM Dozs INNER JOIN Person INNER JOIN Lecture 
                            ON dozs.doz = person.'@key' AND dozs.semester = lecture.semester AND dozs.semester = person.semester 
                            AND dozs.'@key' = lecture.'@key'
                            WHERE lecture.semester IN {str(tuple(year))} 
                            AND lecture.name IN {str(tuple(lecture))}; ''')
    return result

def prediction_best_prof_2022(db: sqlalchemy.engine.Engine) -> set:
    """
    This function creates a list of possible best profs based on several parameters
    :param db A SQL database.
    :return: A set of all possible best profs.
    """
    # Our parameters analyzed from the last years
    year = ['2021w', '2022s']
    ects = [8, 7, 5, 4]
    days = ['w1 2', 'w2 2', 'w1 3', 'w2 3', 'w1 4', 'w2 4']
    starttime = ['10:15', '10:00', '8:15', '8:00', '16:00', '16:15']
    orgname = ['Verteilte Systeme', 'Numerik und Optimierung', 'Didaktik der Informatik', 'Algorithmen und Komplexität',
               'Programmiersprachen & Übersetzerkonstruktion', 'Theoretische Informatik']

    # Retrieves all lectures that fit the above categories.
    result_lectures = sql_prediction_best_prof_2022_lecture(year, starttime, days, ects, orgname, db)

    # Saves the result of the SQL query to a list.
    lectures = [elem[0] for elem in result_lectures]

    # Filters all exercises
    filtered_lectures = []
    for ele in lectures:
        if "Übung" not in ele:
            if "übung" not in ele:
                if "Exercise" not in ele:
                    filtered_lectures.append(ele)

    result_prof = sql_prediction_best_prof_2022_prof(year, filtered_lectures, db)
    # Saves the result of the SQL query to a list.
    profs = [elem for elem in result_prof]

    prof_set = set(profs)

    # Prints the data frame and removes missing values.
    return prof_set
