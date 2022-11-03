from pyroutelib3 import Router


def pyroutedistance(lon0, lat0, lon3, lat3):
    """
    gets the route between to points
    :param lon0: longitude of the first point
    :param lat0: latitude of the first point
    :param lon3: longitude of the second point
    :param lat3: latitude of the second point
    :return: route between two points
    """
    # Initialise router and set the transport mode for pedestrians
    router = Router("foot")
    # Find start and end nodes
    start = router.findNode(lat0, lon0)
    end = router.findNode(lat3, lon3)

    # Find the route - a list of OSM nodes
    status, route = router.doRoute(start, end)

    if status == "success":
        start_point = (lat0, lon0)
        # Get actual route coordinates
        route_lat_lons = list(map(router.nodeLatLon, route))
        end_point = (lat3, lon3)
        res = [start_point] + route_lat_lons + [end_point]
        return res

    else:
        return None




