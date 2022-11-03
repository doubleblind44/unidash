import sqlalchemy
from python.faculty import Faculty, FACULTY_COLORS
import pandas
import plotly.express


def englishs(db: sqlalchemy.engine.Engine) -> pandas.DataFrame():
    """
    gets the ratio of the english lectures for every faculty
    :param db: the sql database
    :return: dictionary that contains the ratio of the english lectures for every semester and the absolute numbers,
    sorted by faculty
    """
    faculties = str(tuple([str(x) for x in Faculty]))
    # get the ratio of the english lectures for every faculty
    sql = f'''
    SELECT OT.semester AS Semester, orgunit AS Fakultät, SUM(englisch) AS Englisch, COUNT(*) AS "Anzahl Lectures", 
        ROUND(SUM(englisch) * 100.0 / COUNT(*), 2) AS "Prozentualer Anteil" 
    FROM Lecture NATURAL JOIN orgunits OT 
    WHERE type NOT IN ('AG', 'FPUE', 'KL', 'KO', 'UAK', 'KU', 'SPUE', 'P', 'P-SEM', 'PRUE', 'TU', 'broken') 
        AND orgunit IN {faculties} 
    GROUP BY OT.semester, orgunit 
    '''
    # get the dataframe and sort it by faculty and semester
    df_eng = pandas.read_sql(sql, db)
    df_eng = df_eng.sort_values(by=['Fakultät', 'Semester'])

    return df_eng


def add_missing_semester(df_eng: pandas.DataFrame()) -> pandas.DataFrame():
    """
    if a semester is missing add a row to the dataframe containing the semester and faculty,
    fill the other columns with null
    :param df_eng: the dataframe to check for missing semester
    :return: a dataframe without missing semesters
    """
    # get the semesters
    semesters = list(df_eng['Semester'].unique())
    # a dataframe to collect the missing rows
    missing_sems = pandas.DataFrame(columns=['Semester', 'Fakultät', 'Englisch',
                                             'Anzahl Lectures', 'Prozentualer Anteil'])
    i = 0
    # got through the data
    for index, row in df_eng.iterrows():
        # get the expected semester
        sem = semesters[i]
        # get the current semester
        sem_row = row['Semester']
        # if the current and expected semester don't match, the semester is missing. So add it to the new dataframe
        if sem_row != sem:
            missing_sems.loc[len(missing_sems.index)] = [sem, row['Fakultät'], None, 0, None]
        # if we reached the end and it's not the last semesters in UnivIS, that semester is missing
        if index == df_eng.index[-1] and sem != semesters[-1]:
            missing_sems.loc[len(missing_sems.index)] = ['2023s', row['Fakultät'], None, 0, None]
        # look at the next semester
        i += 1
        # if we reached the last semester, start at the beginning because there aren't more rows for the current faculty
        if sem == semesters[-1]:
            i = 0

    return pandas.concat([df_eng, missing_sems])


def visualize(df: pandas.DataFrame):
    # plot for ratio
    fig_r = plotly.express.bar(df, x="Prozentualer Anteil", y="Fakultät", color="Fakultät",
                               animation_frame="Semester", range_x=[0, 100], color_discrete_map=FACULTY_COLORS,
                               hover_name="Prozentualer Anteil",
                               hover_data={"Semester": False, "Englisch": True, "Anzahl Lectures": True,
                                           "Fakultät": False, "Prozentualer Anteil": False},
                               title="Anteil der englischsprachigen Veranstaltungen pro Fakultät")

    # plot for absolute number of english lectures
    fig_a = plotly.express.bar(df, x="Englisch", y="Fakultät", color="Fakultät",
                               animation_frame="Semester", range_x=[0, 130], color_discrete_map=FACULTY_COLORS,
                               hover_name="Englisch",
                               hover_data={"Semester": False, "Prozentualer Anteil": True, "Anzahl Lectures": True,
                                           "Fakultät": False, "Englisch": False},
                               title="Anzahl der englischsprachigen Veranstaltungen pro Fakultät")

    return fig_a, fig_r



