from typing import Tuple, Dict, Union, Any, List

import pandas as pd
import plotly.express
import pandas
import sqlalchemy
from plotly.graph_objs import Figure


def capacity(db: sqlalchemy.engine.base.Engine
             ) -> Tuple[Dict[str, List[Dict[str, Union[int, str, float]]]],
                        Dict[str, List[Dict[str, Union[int, str, float]]]],
                        Dict[str, List[Dict[str, Union[int, str, float]]]],
                        Dict[str, List[float]], Dict[str, List[float]], Dict[str, List[float]]]:
    """
    Get the average degree of capacity utilization per room for every semester
    and the average degree of capacity utilization per room size for every semester (the mean for every room size)

    :param db: Sql database
    :return:   Dictionaries containing the information about the degree of capacity utilization, name, size and
                number of uses of a room sorted by semester.
                Also dictionaries containing the mean of every room size sorted by semester
    """
    con = db.connect()
    # collect the degree of capacity utilization for every semester, separated by room size
    capacity_room_from_100 = {}
    capacity_room_til_100 = {}
    capacity_room_til_50 = {}
    # adds up the degrees of capacity utilization to compute a mean for every semester, separated by room size
    average_f100 = {}
    average_t100 = {}
    average_t50 = {}
    # count the number of rooms to compute a mean for every semester, separated by room size
    counter_f100 = {}
    counter_t100 = {}
    counter_t50 = {}
    # dictionaries to see if a room was already added to our dictionaries
    added_rooms_f_100 = set()
    added_rooms_t_100 = set()
    added_rooms_t_50 = set()
    # get the average degree of capacity utilization of every room per semester
    query = "SELECT [@key], name, short, AVG(ratio), semester, size, number, teilnehmer " \
            "FROM " \
            "(SELECT R.[@key], R.name, R.short, OT.semester, ROUND(turnout * 100.0 / size, 2) AS ratio, " \
            "room, SUM(turnout) AS teilnehmer, size, COUNT(*) AS number " \
            "FROM (terms NATURAL JOIN orgunits) OT " \
            "LEFt JOIN Lecture L on OT.[@key] = L.[@key] AND L.semester = OT.semester " \
            "LEFT JOIN Room R ON OT.room = R.[@key] AND R.semester = OT.semester " \
            "WHERE turnout NOT NULL " \
            "AND SUBSTR(orgunit, -8, 8) = 'Fakultät' " \
            "AND size NOT NULL " \
            "GROUP BY OT.semester, room) " \
            "GROUP BY room, semester"
    info = con.execute(query)
    # save the information in the dictionary
    for key, name, short, average, semester, size, number, teilnehmer in info:
        if int(size) >= 100:
            name = short if name is None else name
            if name not in added_rooms_f_100:
                capacity_room_from_100[name] = []
            capacity_room_from_100[name] += [
                {"Semester": semester, "Short": short, "Durchschnittliche Raumauslastung": average, "Größe": size,
                 "Teilnehmer": teilnehmer, "#uses": number}]
            # add the room to the cache
            added_rooms_f_100.add(name)
            # collect the degrees of capacity utilization
            if semester not in average_f100:
                average_f100[semester] = 0
            average_f100[semester] += average
            # count the rooms
            if semester not in counter_f100:
                counter_f100[semester] = 0
            counter_f100[semester] += 1

        if 50 <= int(size) < 100:
            name = short if name is None else name
            if name not in added_rooms_t_100:
                capacity_room_til_100[name] = []
            capacity_room_til_100[name] += [
                {"Semester": semester, "Short": short, "Durchschnittliche Raumauslastung": average, "Größe": size,
                 "Teilnehmer": teilnehmer, "#uses": number}]
            # add the room to the cache
            added_rooms_t_100.add(name)
            # collect the degrees of capacity utilization
            if semester not in average_t100:
                average_t100[semester] = 0
            average_t100[semester] += average
            # count the rooms
            if semester not in counter_t100:
                counter_t100[semester] = 0
            counter_t100[semester] += 1

        if int(size) < 50:
            name = short if name is None else name
            if name not in added_rooms_t_50:
                capacity_room_til_50[name] = []

            capacity_room_til_50[name] += [
                {"Semester": semester, "Short": short, "Durchschnittliche Raumauslastung": average, "Größe": size,
                 "Teilnehmer": teilnehmer, "#uses": number}]
            # add the room to the cache
            added_rooms_t_50.add(name)
            # collect the degrees of capacity utilization
            if semester not in average_t50:
                average_t50[semester] = 0
            average_t50[semester] += average
            # count the rooms
            if semester not in counter_t50:
                counter_t50[semester] = 0
            counter_t50[semester] += 1
    # compute the mean for every semester and room size
    for sem in average_f100:
        average_f100[sem] = [round(average_f100[sem] / counter_f100[sem], 2)]
    for sem in average_t100:
        average_t100[sem] = [round(average_t100[sem] / counter_t100[sem], 2)]
    for sem in average_t50:
        average_t50[sem] = [round(average_t50[sem] / counter_t50[sem], 2)]

    return capacity_room_from_100, capacity_room_til_100, capacity_room_til_50, average_f100, average_t100, average_t50


def capacity_corona(db: sqlalchemy.engine.base.Engine):
    """
    get the average degree of capacity utilization
    and ratio between the normal size and the reduced size while covid of every room per semester

    :param db: sql database
    :return: dictionary containing the information about the
    degree of capacity utilization, name, size and number of uses of a room sorted by semester
    """
    con = db.connect()
    # collect the degree of capacity utilization and ratio for every semester, separated by room size
    capacity_room_from_100 = {}
    capacity_room_til_100 = {}
    capacity_room_til_50 = {}
    # dictionaries to see if a room was already added to our dictionaries
    added_rooms_f_100 = set({})
    added_rooms_t_100 = set({})
    added_rooms_t_50 = set({})
    # get the average degree of capacity utilization of every room per semester while corona
    query = "Select [@key], semester, name, short, size, reducedsize, AVG(ratio), teilnehmer, AVG(capacity), number " \
            "FROM " \
            "(Select R.[@key], R.name, reducedsize, R.short, OT.semester, " \
            "ROUND(reducedsize * 100.0 / size, 2) AS ratio, room, SUM(turnout) AS teilnehmer, " \
            "size, COUNT(*) AS number, " \
            "ROUND(reducedsize * 100.0 / turnout, 2) AS capacity " \
            "FROM (terms NATURAL JOIN orgunits) OT " \
            "LEft JOIN Lecture L on OT.[@key] = L.[@key] " \
            "AND L.semester = OT.semester LEFT JOIN Room R ON OT.room = R.[@key] " \
            "AND R.semester = OT.semester WHERE turnout NOT NULL " \
            "AND reducedsize NOT NULL " \
            "AND OT.semester IN ('2020s', '2020w', '2021s', '2021w') " \
            "AND size NOT NULL " \
            "GROUP BY OT.semester, room) " \
            "GROUP BY room, semester " \
            "ORDER BY semester;"
    info = con.execute(query)
    # save the information in the dictionary
    for key, semester, name, short, size, reduced_size, ratio, teilnehmer, capacity_utilization, number in info:
        if int(size) >= 100:
            name = short if name is None else name
            if name not in added_rooms_f_100:
                capacity_room_from_100[name] = []
            capacity_room_from_100[name] += [
                {"Semester": semester, "Short": short, "Prozentualer Anteil": ratio, "Teilnehmer": teilnehmer,
                 "Durchschnittliche Raumauslastung": capacity_utilization, "Größe": size,
                 "Corona-Größe": reduced_size, "#uses": number}]
            # add the room to the cache
            added_rooms_f_100.add(name)
        if 50 <= int(size) < 100:
            name = short if name is None else name
            if name not in added_rooms_t_100:
                capacity_room_til_100[name] = []
            capacity_room_til_100[name] += [
                {"Semester": semester, "Short": short, "Prozentualer Anteil": ratio, "Teilnehmer": teilnehmer,
                 "Durchschnittliche Raumauslastung": capacity_utilization, "Größe": size,
                 "Corona-Größe": reduced_size, "#uses": number}]
            # add the room to the cache
            added_rooms_t_100.add(name)
        if int(size) < 50:
            name = short if name is None else name
            if name not in added_rooms_t_50:
                capacity_room_til_50[name] = []
            capacity_room_til_50[name] += [
                {"Semester": semester, "Short": short, "Prozentualer Anteil": ratio, "Teilnehmer": teilnehmer,
                 "Durchschnittliche Raumauslastung": capacity_utilization, "Größe": size,
                 "Corona-Größe": reduced_size, "#uses": number}]
            # add the room to the cache
            added_rooms_t_50.add(name)

    return capacity_room_from_100, capacity_room_til_100, capacity_room_til_50


def visualize_capacity(df_rooms_f100: pd.DataFrame, df_rooms_t100: pd.DataFrame, df_rooms_t50: pd.DataFrame,
                       df_means: pd.DataFrame) -> Tuple[Figure, Figure, Figure, Figure, Figure]:
    """
    Creates plots to visualize the degree of utilization of the different room sizes

    :param df_rooms_f100: Dataframe containing information about rooms with a capacity of at least 100 person
    :param df_rooms_t100: Dataframe containing information about rooms with a capacity of at most 100 person
    :param df_rooms_t50:  Dataframe containing information about rooms with a capacity of at most 50 person
    :param df_means:      Dataframe containing the information about the means of every room type for every semester
    :return:              Plots visualizing the degree of utilization
    """
    # plot for the means
    fig_means = plotly.express.line(df_means, x="Semester", y="Mittelwert in Prozent", color="Raumgröße in Personen",
                                    hover_name="Mittelwert in Prozent",
                                    hover_data={"Semester": True, "Raumgröße in Personen": False, "Mittelwert in Prozent": False},
                                    title="Durchschnittliche Raumauslastung pro Raumgröße")

    # plots for degree of utilization
    # capacity of at least 100 people
    fig_f100 = plotly.express.scatter(data_frame=df_rooms_f100, x="Durchschnittliche Raumauslastung", y="Raum",
                                      animation_frame="Semester", color="Semester", range_x=[0, 260], hover_name="Raum",
                                      hover_data={'Raum': False, 'Semester': False, 'Größe': True, '#uses': True},
                                      title="Raumauslastung der Räume mit einer Kapazität von mind. 100 Personen")
    fig_f100.update_layout(showlegend=False)
    # capacity of at most 100 people
    fig_t100 = plotly.express.scatter(data_frame=df_rooms_t100, x="Durchschnittliche Raumauslastung", y="Raum",
                                      animation_frame="Semester", color="Semester", range_x=[0, 460], hover_name="Raum",
                                      hover_data={'Raum': False, 'Semester': True, 'Größe': True, '#uses': True},
                                      title="Raumauslastung der Räume mit einer Kapazität von 50 bis 100 Personen")
    fig_t100.update_layout(showlegend=False)
    # capacity of at most 50 people
    fig_t50 = plotly.express.scatter(data_frame=df_rooms_t50, x="Durchschnittliche Raumauslastung", y="Raum",
                                     color="Semester", hover_name="Raum",
                                     hover_data={'Raum': False, 'Semester': True, 'Größe': True, '#uses': True},
                                     title="Raumauslastung der Räume mit einer Kapazität von max. 50 Personen")
    fig_t50_part = plotly.express.scatter(data_frame=df_rooms_t50, x="Durchschnittliche Raumauslastung", y="Raum",
                                          color="Semester", range_x=[0, 100], hover_name="Raum",
                                          hover_data={'Raum': False, 'Semester': True, 'Größe': True, '#uses': True},
                                          title="Raumauslastungen zwischen 0% und 100% der kleinen Räume ")

    return fig_means, fig_f100, fig_t100, fig_t50, fig_t50_part


def visualize_corona(df_corona_f100, df_corona_t100, df_corona_t50):
    """
    creates plots to visualize the difference between the reduced size while corona and the normal size
    :param df_corona_f100: dataframe containing information about rooms with a capacity of at least 100 person
    :param df_corona_t100: dataframe containing information about rooms with a capacity of at most 100 person
    :param df_corona_t50: dataframe containing information about rooms with a capacity of at most 50 person
    :return: plots visualizing the difference between the reduced size while corona and the normal size
    """

    # plots for capacity difference
    # at least 100
    fig_cap_f100 = plotly.express.scatter(data_frame=df_corona_f100, x="Prozentualer Anteil",
                                          y="Raum", color="Semester", hover_name="Raum",
                                          hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                      "Größe": True, "Corona-Größe": True},
                                          title="Reduzierte Kapazität für Räume mit einer "
                                                "Kapazität von mind. 100 Personen")
    # at most 100
    fig_cap_t100 = plotly.express.scatter(data_frame=df_corona_t100, x="Prozentualer Anteil", y="Raum",
                                          color="Semester", range_x=[0, 100], hover_name="Raum",
                                          hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                      "Größe": True, "Corona-Größe": True},
                                          title="Reduzierte Kapazität für Räume mit einer "
                                                "Kapazität von 50 bis 100 Personen")
    # at most 50
    fig_cap_t50 = plotly.express.scatter(data_frame=df_corona_t50, x="Prozentualer Anteil", y="Raum", color="Semester",
                                         range_x=[0, 100], hover_name="Raum",
                                         hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                     "Größe": True, "Corona-Größe": True},
                                         title="Reduzierte Kapazität für Räume mit einer "
                                               "Kapazität von max. 50 Personen")

    # plots for degree of utilization
    # at least 100
    fig_deg_f100 = plotly.express.scatter(data_frame=df_corona_f100, x="Durchschnittliche Raumauslastung", y="Raum",
                                          color="Semester", hover_name="Raum",
                                          hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                      "Größe": True, "Corona-Größe": True},
                                          title="Raumauslastung der Räume mit einer Kapazität "
                                                "von mind. 100 Personen während Corona")
    # at most 100
    fig_deg_t100 = plotly.express.scatter(data_frame=df_corona_t100, x="Durchschnittliche Raumauslastung", y="Raum",
                                          color="Semester", hover_name="Raum",
                                          hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                      "Größe": True, "Corona-Größe": True},
                                          title="Raumauslastung der Räume mit einer Kapazität "
                                                "von 50 bis 100 Personen während Corona")
    # at most 50
    fig_deg_t50 = plotly.express.scatter(data_frame=df_corona_t50, x="Durchschnittliche Raumauslastung", y="Raum",
                                         color="Semester", hover_name="Raum",
                                         hover_data={"Semester": False, "Raum": False, "Prozentualer Anteil": True,
                                                     "Größe": True, "Corona-Größe": True},
                                         title="Raumauslastung der Räume mit einer Kapazität "
                                               "von max. 50 Personen während Corona")

    return fig_cap_f100, fig_cap_t100, fig_cap_t50, fig_deg_f100, fig_deg_t100, fig_deg_t50


def get_dataframe(rooms):
    """
     changes the dict to a dataframe and changes the dataframe
     so the keys of the dictionary are the names of the columns,
     to show the degree of utilization per room size (not for the mean)

    :param rooms:
    :return:
    """
    df = pandas.DataFrame().from_dict(rooms, orient='index')
    all_dfs = []
    # The dataframe has a column for each index of the lists of the different rooms
    # In each cell of the column is a dictionary or None.
    # So convert each column into one dataframe with the keys of the dictionaries as columns
    for column in df:
        new_df = df[column].apply(pandas.Series, dtype="object")
        all_dfs += [new_df]
    # Connect the new dataframes
    df_ready = pandas.DataFrame()
    for i in range(len(all_dfs)):
        df_ready = pandas.concat([df_ready, all_dfs[i]], axis=0)
    # drop the rows only containing None
    df_ready = df_ready.dropna(how='all')
    # In the index are the rooms, but we need the faculties in a separate column
    df_ready = df_ready.reset_index(level=0)
    df_ready = df_ready.rename(columns={'index': 'Raum'}, errors='raise')
    # sort the dataframe by semester
    df_ready = df_ready.sort_values(by=["Semester"])

    return df_ready


def get_dataframe_for_mean(mean_f100, mean_t100, mean_t50):
    """
    get a dataframe combining all the means of different room sizes

    :param mean_f100: Dictionary containing the means per semester for rooms with a capacity of at least 100 people
    :param mean_t100: Dictionary containing the means per semester for rooms with a capacity of at most 99 people
    :param mean_t50: Dictionary containing the means per semester for rooms with a capacity of at most 49 people
    :return: dataframe combining all the means of different room sizes
    """
    # creates dataframes from the dictionaries
    df_mean_f100 = pandas.DataFrame().from_records(mean_f100)
    df_mean_t100 = pandas.DataFrame().from_records(mean_t100)
    df_mean_t50 = pandas.DataFrame().from_records(mean_t50)
    # change rows and columns
    df_mean_f100 = df_mean_f100.T
    df_mean_t100 = df_mean_t100.T
    df_mean_t50 = df_mean_t50.T
    # add a column for the type of room size
    df_mean_f100["Raumgröße in Personen"] = ">= 100"
    df_mean_t100["Raumgröße in Personen"] = "50 - 99"
    df_mean_t50["Raumgröße in Personen"] = "< 50"

    # change the name of the columns containing the mean and create a column for the semester
    df_ready_f100 = df_mean_f100.rename(columns={0: 'Mittelwert in Prozent'}, errors='raise')
    df_ready_f100 = df_ready_f100.reset_index(level=0)
    df_ready_f100 = df_ready_f100.rename(columns={'index': 'Semester'}, errors='raise')

    df_ready_t100 = df_mean_t100.rename(columns={0: 'Mittelwert in Prozent'}, errors='raise')
    df_ready_t100 = df_ready_t100.reset_index(level=0)
    df_ready_t100 = df_ready_t100.rename(columns={'index': 'Semester'}, errors='raise')

    df_ready_t50 = df_mean_t50.rename(columns={0: 'Mittelwert in Prozent'}, errors='raise')
    df_ready_t50 = df_ready_t50.reset_index(level=0)
    df_ready_t50 = df_ready_t50.rename(columns={'index': 'Semester'}, errors='raise')

    # put the dataframes together
    res = pandas.concat([df_ready_f100, df_ready_t100, df_ready_t50], ignore_index=True)

    return res
