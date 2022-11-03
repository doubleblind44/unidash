import json
import re
from typing import Dict, List, Tuple

from python import osmroute
from python.geomanager import GeoManager
import pandas as pd


def inf_coords(dependencies: Dict[str, Dict[str, List[List[str]]]],
               gm: GeoManager
               ) -> Dict[str, Dict[str, Dict[str, List[Tuple[float, float]]]]]:
    """
    gets the coordinates for the addresses of rooms where lectures were hold which students of the courses of study
    computer science and business information technology have to visit at the same day

    :param dependencies: A dictionary containing the addresses of the rooms we want the coordinates for
    :param gm:           The GeoManager object
    :return:             A dictionary containing the coordinates of addresses of rooms that are visited by student of
                          the courses of study computer science and business information technology at the same day.
                          They represent the lectures from the same day, sorted by study programme semester and semester
                          example {"2016w": {"3": {"1": [(10.1236624, 54.3395847), (10.12160307769561, 54.33888365)]}}}
                          {semester: {study programme semester: {day of the week: [(longitude, latitude)]}}}
    """
    coor_dep = {}
    # iterate through the schedule
    for semester in dependencies:
        coor_dep[semester] = {}
        for study_sem in dependencies[semester]:
            coor_dep[semester][study_sem] = {}
            for day in dependencies[semester][study_sem]:
                if day not in coor_dep[semester][study_sem]:
                    coor_dep[semester][study_sem][day] = []
                # go through the addresses
                for addr in dependencies[semester][study_sem][day]:
                    # we only want the addresses with a house number
                    if addr and re.search(r'(?<!\d)\d{1,4}(?!\d)', addr) is not None:
                        # look up the coordinates
                        location = gm.get_coords(addr)
                        # add the longitude and latitude to the coordinates
                        if location:
                            coor_dep[semester][study_sem][day] += [location]
                        else:
                            coor_dep[semester][study_sem][day] += [None]
                    else:
                        coor_dep[semester][study_sem][day] += [None]
    return coor_dep


def routes_for_df(coor_dependencies: Dict[str, Dict[str, Dict[str, List[Tuple[float, float]]]]]
                  ) -> Dict[str, Dict[str, Dict[str, List[Tuple[float, float]]]]]:
    """
    Computes the coordinates of addresses of rooms where lectures were hold which students of the courses of study
    computer science and business information technology have to visit at the same day

    :param coor_dependencies: A dictionary containing the coordinates to compute the route from.
                               They represent the lectures from the same day, sorted by study programme semester and
                               semester. Example:
                               {"2016w": {"3": {"1": [(10.1236624, 54.3395847), (10.12160307769561, 54.33888365)]}}}
                               {semester: {study programme semester: {day of the week: [(longitude, latitude)]}}}
    :return:                  A dictionary containing the distances between the addresses and the routes to get from one
                               address to the other, sorted by day of the week, study programme semester and semester
                               Example: {'2016w': {'3': {'1': {'distances': [965.8], 'route':
                               [[10.1236624, 54.3395847, 10.123722, 54.339707, 10.12160307769561, 54.33888365]]}}}}
    """
    routes = {}
    cache = {}
    # iterate through the semesters
    for semester in coor_dependencies:
        routes[semester] = []
        # iterate through the study programme semesters
        for study_sem in coor_dependencies[semester]:
            # iterate through the days
            for day in coor_dependencies[semester][study_sem]:
                coors = coor_dependencies[semester][study_sem][day]
                # if there is only one coordinate, there is no route to compute
                if len(coors) == 1:
                    routes[semester] += \
                        [{'Fachsemester': study_sem, 'Tag': day, 'Route': [], 'Points': coors}]
                    continue
                entry = {'Fachsemester': study_sem, 'Tag': day, 'Route': [], 'Points': []}
                # iterate through the coordinates
                for i in range(len(coors)):

                    # if there is no coordinate available we can't compute a route
                    if coors[i] is None:
                        entry['Points'] += [None]
                        continue
                    # if we reached the last address we can't compute a route
                    if i == len(coors) - 1:
                        entry['Points'] += [coors[i]]
                        continue
                    # If the next coordinate is None, we can't compute a route to that address
                    if coors[i + 1] is None:
                        entry['Points'] += [coors[i]]
                        continue
                    # if we already computed that route, just get it from the cache and save it to the dictionary
                    if str(coors[i] + coors[i + 1]) in cache:
                        entry['Route'] += [cache[str(coors[i] + coors[i+1])]]
                        entry['Points'] += [coors[i]]
                        continue
                    # get the route
                    route = osmroute.pyroutedistance(float(coors[i][1]), float(coors[i][0]), float(coors[i + 1][1]), float(coors[i + 1][0]))
                    # save the route and distance in the dictionary
                    entry['Route'] += [route]
                    entry['Points'] += [coors[i]]
                    # save that route in the cache, so we don't dDoS the API
                    cache[str(coors[i] + coors[i+1])] = route

                routes[semester] += [entry]
    return routes


def get_dataframe(routes):
    """
    Changes the dict to a dataframe, so the semesters, study programme semesters, days, routes and waypoints are all in different columns

    :param routes: Dictionary containing the routes to visualize
    """
    df = pd.DataFrame().from_dict(routes, orient='index')
    all_dfs = []
    # Convert each column into one dataframe with the keys of the dictionaries as columns
    for column in df:
        new_df = df[column].apply(pd.Series, dtype = "object")
        all_dfs += [new_df]
     # Connect the new dataframes
    df_ready = pd.DataFrame()
    for i in range(len(all_dfs)):
        df_ready = pd.concat([df_ready, all_dfs[i]], axis=0)
    # drop the rows only containing None
    df_ready = df_ready.dropna(how='all')
    # In the index are the Semester, but we need them in a separate column
    df_ready = df_ready.reset_index(level=0)
    df_ready = df_ready.rename(columns={'index': 'Semester'}, errors='raise')
    # sort the dataframe by semester, study programme semester and day
    df_ready = df_ready.sort_values(by=["Semester", "Fachsemester", 'Tag'])

    return df_ready
