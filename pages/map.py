import os
import dash
from dash import html
from config import DB, GM, CACHE_PATH
from python import facultymap as fm
from distutils.dir_util import copy_tree

title = 'Raumverteilung'
path = '/room-map'

dash.register_page(__name__, name=title, path=path)

if os.path.exists(CACHE_PATH + 'map/geomanager.json'):
    with open(CACHE_PATH + 'map/geomanager.json', 'r') as f:
        GM.read_json(f.read())
if not os.path.exists(CACHE_PATH + 'map/maps/'):
    os.makedirs(CACHE_PATH + 'map/maps/')
    fm.create_map(DB, GM).save(CACHE_PATH + 'map/maps/map.html')
    for fac, m in fm.create_heatmap(DB, GM).items():
        m.save(CACHE_PATH + f'map/maps/heatmap_{fac}.html')
    with open(CACHE_PATH + 'map/geomanager.json', 'w') as f:
        f.write(GM.to_json())

copy_tree(CACHE_PATH + 'map/maps/', '/var/www/datascienceproject/assets/maps/')

print(f'{path} loaded')

layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H3(children='Wie hat sich die Raumverteilung der Fakultäten im Laufe der Zeit verändert?'),
    ]),
    html.Div(children=[
        html.Iframe(className='map', src=dash.get_asset_url('maps/map.html'), width='100%', height='100%')
    ]),
    html.Div(children=[
        html.Iframe(className='map', src=dash.get_asset_url('maps/heatmap_all.html'), width='100%', height='100%')
    ]),
    html.Div(children=[
        html.P('Die meisten Veranstaltungen finden in Kiel und Umgebung statt, jedoch gibt es auch Ausnahmen, wie zum '
               'Beispiel im Jahr 2008 die Agrar- und Ernährungswissenschaftliche Fakultät, die jährlich eine '
               'Veranstaltung in Gartersleben (Sachsen-Anhalt) angeboten hat.'),
        html.P('Die Module der Philosophischen und Rechtswissenschaftlichen Fakultäten finden auf dem gesamten Campus '
               'statt. Die Theologen hingegen sind sehr sesshaft in der Leibnizstraße 4.'),
        html.P('An beiden Darstellungen erkennt man gut, wenn neue Gebäude eröffnet wurden. Zum Beispiel finden seit '
               'dem Wintersemester 2021 vermehrt Veranstaltungen der Rechtswissenschaftlichen Fakultät '
               'im Juridicum statt.')
    ])
]