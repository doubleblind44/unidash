from typing import Optional
import folium
import pandas as pd


def inf_map(map_df: pd.DataFrame, sem: str, study_sem: Optional[str] = None) -> folium.Map:
    """
    Creates a map for a study programme semester of a specific semester showing the way a student of that
    study programme semester has to go in that semester

    :param map_df:    Dataframe containing the coordinates to a semester, study programme semester and day
    :param sem:       The semester we want to show
    :param study_sem: The study programme semester we want to show
    :return:          Map showing the way a student of every study programme semester has to go in a semester
    """
    # create a map
    m = folium.Map(location=[54.3384136, 10.1235659], zoom_start=16)
    # go through each day of work day of a week
    for day in [1, 2, 3, 4, 5]:
        # in the layer control show the work day
        match day:
            case 1:
                name = 'Montag'
            case 2:
                name = 'Dienstag'
            case 3:
                name = 'Mittwoch'
            case 4:
                name = 'Donnerstag'
            case 5:
                name = 'Freitag'
            case _:
                name = ''
        # create a layer for the current day to turn on and off in the layer control
        fg = folium.FeatureGroup(name=name + ' ' + sem)
        m.add_child(fg)
        # go through each work day of a week
        for index, row in map_df.iterrows():
            # if it's the wrong semester skip it
            if row['Semester'] != sem:
                continue
            # if it's the wrong day skip it
            day_row = int(row['Tag'])
            if day != day_row:
                continue
            # if it's the wrong study programme semester skip it
            study_sem_row = str(row['Fachsemester'])

            if study_sem is not None and study_sem_row != study_sem:
                continue
            # Each study programme semester should have its own color on the map
            match study_sem_row:
                case '1':
                    color = 'red'
                case '2':
                    color = 'blue'
                case '3':
                    color = 'orange'
                case '4':
                    color = 'cyan'
                case '5':
                    color = 'purple'
                case '6':
                    color = 'green'
                case _:
                    color = ''
            # for each route in the row draw a line on the map
            for r in row['Route']:
                if r:
                    fg.add_child(folium.PolyLine(r, color=color))

            # for each point add a marker on the map
            for p in row['Points']:
                if p:
                    fg.add_child(folium.CircleMarker(location=p, popup='Fachsemester: ' + study_sem_row, color=color,
                                                     fill_color=color))

    # add the layer control to the map
    folium.LayerControl().add_to(m)
    return m
