import sqlalchemy
from python.geomanager import GeoManager

# TODO: Please configure the website here
CACHE_PATH = '/path/to/webcache/'         # The Path where the website should cache data in json format (should end with '/')
DB_PATH = r'sqlite:////path/to/univis.db' # The path of the database
GM_MAIL = 'mail@example.com'             # See also: https://operations.osmfoundation.org/policies/nominatim/


# The instances used by the website
DB = sqlalchemy.create_engine(DB_PATH)
GM = GeoManager(GM_MAIL)
