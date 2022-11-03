from typing import Dict, Tuple, Optional, Union, List
import folium
import sqlalchemy
from folium import plugins
from jinja2 import Template
from folium.map import Layer
from python.faculty import Faculty, FACULTY_COLORS
from python.geomanager import GeoManager


def create_faculty_rooms_view(db: sqlalchemy.engine.Engine) -> None:
    """
    Creates a view that maps each the number of uses per semester for each room to the faculties.

    :param db: The database connection
    """
    faculties = str(tuple([str(x) for x in Faculty]))

    con = db.connect()
    con.execute(f'''
    CREATE VIEW IF NOT EXISTS faculty_rooms AS
    SELECT T.semester, orgunit AS 'faculty', new_address AS 'address', COUNT(*) AS 'count'
    FROM terms T
         NATURAL JOIN orgunits O
         LEFT JOIN Room R ON T.room = R.[@key] AND T.semester = R.semester
         LEFT JOIN new_addresses A ON R.address = A.old_address
    WHERE orgunit IN {faculties}
        GROUP BY T.semester, orgunit, new_address
        ORDER BY orgunit, T.semester;
    ''')


def create_map(db: sqlalchemy.engine.Engine, gm: GeoManager) -> folium.Map:
    """
    Creates a map of the room usage of faculties

    :param db: The database connection
    :param gm: The GeoManager
    :return:   The map as a string
    """
    create_faculty_rooms_view(db)

    con = db.connect()
    result = con.execute('SELECT * FROM faculty_rooms;')

    # Create the empty map
    m = folium.Map(location=[54.3384136, 10.1235659], zoom_start=14, tiles=None)
    # Add the OpenStreetMap tiles as background that you can not disable
    # (this is necessary, so the semester buttons can be radio buttons)
    base_map = folium.FeatureGroup(name='Basemap', overlay=True, control=False)
    base_map.add_child(folium.TileLayer(tiles='OpenStreetMap'))
    base_map.add_to(m)
    # Store the points of each semester in a feature group
    fgs = {}
    for semester, faculty, address, count in result:
        if semester not in fgs:
            fgs[semester] = folium.FeatureGroup(name=semester, overlay=False, control=True)
            fgs[semester].add_to(m)

        # Create a circle at the coordinates of the address
        coords = gm.get_coords(address)
        if coords is not None:
            fgs[semester].add_child(folium.Circle(location=coords, radius=count / 50, color=FACULTY_COLORS[faculty],
                                                  fill=True, fill_opacity=0.4, popup=f'{faculty} ({semester}: {count})',
                                                  tooltip=f'<b>{faculty}</b><br><i>{address}</i>'))
    m.add_child(folium.LayerControl())
    return m


def create_heatmap(db: sqlalchemy.engine.Engine,
                   gm: GeoManager
                   ) -> Dict[str, folium.Map]:
    """
    Creates a heatmap of the room usage of a faculty

    :param db:      The database connection
    :param gm:      The GeoManager
    :param faculty: The faculty to create the heatmap for
    :return:        The generated animated heatmaps
    """
    create_faculty_rooms_view(db)

    con = db.connect()
    result = con.execute(f'''
    SELECT semester, faculty, address, count, count * 1.0 / max AS 'ratio'
    FROM (
        SELECT semester, faculty, address, count
        FROM faculty_rooms
        WHERE address IS NOT NULL
        GROUP BY semester, faculty, address
    ) NATURAL JOIN (
        SELECT semester, faculty, MAX(count) AS 'max'
        FROM faculty_rooms
        WHERE address IS NOT NULL
        GROUP BY semester, faculty
    )
    GROUP BY faculty, semester, address;
    ''')

    # Create a dictionary for the maps and a dictionary for the data
    maps = {}
    data = {}

    # Initialize the map for all the faculties
    maps['all'] = folium.Map(location=[54.3384136, 10.1235659], zoom_start=14, tiles=None)
    maps['all'].add_child(folium.TileLayer(tiles='openstreetmap', name='OpenStreetMap'))
    maps['all'].add_child(folium.TileLayer(tiles='stamentoner', name='Stamen Toner'))
    maps['all'].add_child(folium.TileLayer(tiles='cartodbpositron', name='CartoDB Positron'))
    maps['all'].add_child(folium.TileLayer(tiles='cartodbdark_matter', name='CartoDB Dark Matter'))

    for semester, faculty, address, count, ratio in result:
        if faculty not in maps:
            # Initialize the map for the faculty
            maps[faculty] = folium.Map(location=[54.3384136, 10.1235659], zoom_start=14, tiles=None)
            maps[faculty].add_child(folium.TileLayer(tiles='openstreetmap', name='OpenStreetMap'))
            maps[faculty].add_child(folium.TileLayer(tiles='stamentoner', name='Stamen Toner'))
            maps[faculty].add_child(folium.TileLayer(tiles='cartodbpositron', name='CartoDB Positron'))
            maps[faculty].add_child(folium.TileLayer(tiles='cartodbdark_matter', name='CartoDB Dark Matter'))

        # Initialize the data for the faculty (and semester)
        if faculty not in data:
            data[faculty] = {}
        if semester not in data[faculty]:
            data[faculty][semester] = []

        # Get the coordinates of the address and add them to the data with the weight
        coords = gm.get_coords(address)
        if coords is None:
            continue
        lat, lon = coords
        data[faculty][semester] += [[lat, lon, ratio]]

    # Get the length of the biggest data set (time-wise) and create a list of all the semesters of the dataset
    max_len = 0
    index = []
    for faculty in data:
        if len(data[faculty]) > max_len:
            max_len = len(data[faculty])
            index = list(data[faculty].keys())

    # Create the heatmap for all the faculties
    # Because the 'all'-map needs only one 'HeatMapWithTime' layer, we need to handle the first faculty separately
    facs = list(data.keys())
    faculty = facs[0]

    # Combine the data of all the semesters of the faculty
    new_data = [data[faculty][semester] for semester in data[faculty]]
    # Create the heatmap and add it to the faculties map
    hm = plugins.HeatMapWithTime(new_data, index=list(data[faculty].keys()), use_local_extrema=True, max_opacity=0.9,
                                 radius=20, gradient={0: '#ffffff', 1: FACULTY_COLORS[faculty]}, name=faculty)
    maps[faculty].add_child(hm)
    maps[faculty].add_child(folium.LayerControl())

    # If the dataset is not complete, fill it with empty data
    if len(new_data) < max_len:
        new_data += [[[0, 0, 0]] * (max_len - len(new_data))]
    # Create the heatmap and add it to the 'all'-map
    hm2 = plugins.HeatMapWithTime(new_data, index=index, use_local_extrema=True, max_opacity=0.9, show=False,
                                  radius=20, gradient={0: '#ffffff', 1: FACULTY_COLORS[faculty]}, name=faculty)
    maps['all'].add_child(hm2)

    # Create the heatmaps for all the other faculties
    for faculty in facs[1:]:
        # Combine the data of all the semesters of the faculty
        new_data = [data[faculty][semester] for semester in data[faculty]]
        # Create the heatmap and add it to the faculties map
        hm = plugins.HeatMapWithTime(new_data, index=list(data[faculty].keys()), use_local_extrema=True, name=faculty,
                                     max_opacity=0.9, radius=20, gradient={0: '#ffffff', 1: FACULTY_COLORS[faculty]})
        maps[faculty].add_child(hm)
        maps[faculty].add_child(folium.LayerControl())

        # If the dataset is not complete, fill it with empty data
        if len(new_data) < max_len:
            new_data += [[[0, 0, 0]]] * (max_len - len(new_data))
        # Create the heatmap and add it to the 'all'-map
        hm2 = HeatMapWithTimeAdditional(new_data, use_local_extrema=True, max_opacity=0.9, radius=20,
                                        gradient={0: '#ffffff', 1: FACULTY_COLORS[faculty]}, name=faculty, show=False)
        maps['all'].add_child(hm2)
    maps['all'].add_child(folium.LayerControl())

    return maps


class HeatMapWithTimeAdditional(Layer):
    """
    An additional layer for foliums HeatMapWithTime.
    Code by GitHub User 'Conengmo' (https://github.com/python-visualization/folium/issues/1062#issuecomment-462075814)
    """
    _template = Template("""
        {% macro script(this, kwargs) %}
            var {{this.get_name()}} = new TDHeatmap({{ this.data }},
                {heatmapOptions: {
                    radius: {{this.radius}},
                    minOpacity: {{this.min_opacity}},
                    maxOpacity: {{this.max_opacity}},
                    scaleRadius: {{this.scale_radius}},
                    useLocalExtrema: {{this.use_local_extrema}},
                    defaultWeight: 1,
                    {% if this.gradient %}gradient: {{ this.gradient }}{% endif %}
                }
            }).addTo({{ this._parent.get_name() }});
        {% endmacro %}
    """)

    def __init__(self, data: Union[Tuple[float, float], Tuple[float, float, float], List[float]],
                 name: Optional[str] = None, radius: int = 15, min_opacity: int = 0, max_opacity: float = 0.6,
                 scale_radius: bool = False, gradient: Optional[Dict[Union[int, float], str]] = None,
                 use_local_extrema: bool = False, overlay: bool = True, control: bool = True, show: bool = True):
        """
        Initializes the HeatMapWithTimeAdditional layer.

        :param data:              The points you want to plot. The outer list corresponds to
                                   the various time steps in sequential order.
                                   (weight is in (0, 1] range and defaults to 1 if not specified for a point)
        :param name:              The name of the Layer, as it will appear in LayerControls.
        :param radius:            The radius used around points for the heatmap.
        :param min_opacity:       The minimum opacity for the heatmap.
        :param max_opacity:       The maximum opacity for the heatmap.
        :param scale_radius:      Scale the radius of the points based on the zoom level.
        :param gradient:          Match point density values to colors. Color can be a name (‘red’),
                                   RGB values (‘rgb(255,0,0)’) or a hex number (‘#FF0000’).
        :param use_local_extrema: Defines whether the heatmap uses a global extrema set found from the input data OR a
                                   local extrema (the maximum and minimum of the currently displayed view).
        :param overlay:           Adds the layer as an optional overlay (True) or the base layer (False).
        :param control:           Whether the Layer will be included in LayerControls.
        :param show:              Whether the layer will be shown on opening (only for overlays).
        """
        super(HeatMapWithTimeAdditional, self).__init__(
            name=name, overlay=overlay, control=control, show=show
        )
        self._name = 'HeatMap'
        self.data = data

        # Heatmap settings.
        self.radius = radius
        self.min_opacity = min_opacity
        self.max_opacity = max_opacity
        self.scale_radius = 'true' if scale_radius else 'false'
        self.use_local_extrema = 'true' if use_local_extrema else 'false'
        self.gradient = gradient
