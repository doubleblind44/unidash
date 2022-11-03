import json
from typing import Union, Tuple

import geopy
from geopy.geocoders import Nominatim
import time


class GeoManager:
    """
    A class to manage addresses and coordinates
    """
    def __init__(self, email: str):
        """
        Initialize the GeoManager

        :param email: The email address to use for the geopy geolocator (required by the Nominatim API)
        """
        self.addr_to_coords = {}
        self.geolocator = Nominatim(user_agent=email)

    def get_coords(self, addr: str) -> Union[Tuple[float, float], None]:
        """
        Get the coordinates for the given address

        :param addr: An address as string
        :return:     The coordinates as tuple (lat, lon) or None if the address could not be found
        """
        # Checks if the address is already in the cache
        if addr not in self.addr_to_coords:
            # If not, try to get the coordinates from the geolocator (and cache them)
            time.sleep(1)
            location = self.geolocator.geocode(addr)
            self.addr_to_coords[addr] = location
        # Return the coordinates from the cache
        loc = self.addr_to_coords[addr]
        if loc:
            return loc.latitude, loc.longitude
        return None

    def to_json(self) -> str:
        """
        Get a JSON representation of the cache

        :return: A JSON string representing the cache
        """
        json_dict = {
            addr: None if loc is None else [loc.address, loc.latitude, loc.longitude, loc.altitude, loc.raw]
            for addr, loc in self.addr_to_coords.items()}
        return json.dumps(json_dict)

    def read_json(self, json_str: str):
        """
        Read a JSON string into the cache

        :param json_str: A JSON string representing the cache
        """
        cached = json.loads(json_str)
        self.addr_to_coords = {
            addr: None if loc is None else geopy.location.Location(loc[0], (loc[1], loc[2], loc[3]), loc[4])
            for addr, loc in cached.items()}