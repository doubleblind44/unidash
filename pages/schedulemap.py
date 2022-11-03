import os
import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
from config import DB, GM, CACHE_PATH
from python import schedulemap as sm, lecturesperfaculty as lpf, lectureinf as li, geo
from distutils.dir_util import copy_tree
from python.faculty import Faculty

title = 'Wege von Informatikstudierenden'
path = '/routing-map'

dash.register_page(__name__, name=title, path=path)

app = dash.get_app()

if not os.path.exists(CACHE_PATH + 'schedulemap/'):
    os.makedirs(CACHE_PATH + 'schedulemap/maps/')

if not os.path.exists(CACHE_PATH + 'schedulemap/' + 'route_winf.json'):
    modules = lpf.get_lectures(DB)

    mods_techn = modules[str(Faculty.TECHN)]
    mods_mathe = modules[str(Faculty.MATHE)]
    mods_wirtsc = modules[str(Faculty.WIRTSC)]
    mods_rechts = modules[str(Faculty.RECHTS)]

    mods_inf = {}
    mods_winf = {}
    for sem in mods_techn:
        mods_inf[sem] = mods_techn[sem] + mods_mathe[sem]
        mods_winf[sem] = mods_techn[sem] + mods_mathe[sem] + mods_wirtsc[sem] + mods_rechts[sem]

    sched_inf = li.get_dependencies(DB, li.add_exercises_inf(li.build_schedule(DB, mods_inf), DB))
    sched_winf = li.get_dependencies(DB, li.add_exercises_winf(li.build_schedule(DB, mods_winf, True), DB))

    route_inf = geo.get_dataframe(geo.routes_for_df(geo.inf_coords(sched_inf, GM)))
    route_winf = geo.get_dataframe(geo.routes_for_df(geo.inf_coords(sched_winf, GM)))

    route_inf.to_json(CACHE_PATH + 'schedulemap/route_inf.json')
    route_winf.to_json(CACHE_PATH + 'schedulemap/route_winf.json')
    with open(CACHE_PATH + 'schedulemap/geomanager.json', 'w') as f:
        f.write(GM.to_json())
else:
    route_inf = pd.read_json(CACHE_PATH + 'schedulemap/route_inf.json')
    route_winf = pd.read_json(CACHE_PATH + 'schedulemap/route_winf.json')
    with open(CACHE_PATH + 'schedulemap/geomanager.json', 'r') as f:
        GM.read_json(f.read())

if not os.path.exists(CACHE_PATH + 'schedulemap/maps/empty.html'):
    for sem in route_inf['Semester'].unique():
        sm.inf_map(route_inf, sem).save(CACHE_PATH + 'schedulemap/maps/inf_' + sem + '_0.html')
        sm.inf_map(route_winf, sem).save(CACHE_PATH + 'schedulemap/maps/winf_' + sem + '_0.html')
        for i in range(1, 3 + 1):
            k = str(i * 2) if sem.endswith('s') else str(i * 2 - 1)
            sm.inf_map(route_inf, sem, k).save(CACHE_PATH + 'schedulemap/maps/inf_' + sem + '_' + k + '.html')
            sm.inf_map(route_winf, sem, k).save(CACHE_PATH + 'schedulemap/maps/winf_' + sem + '_' + k + '.html')
    sm.inf_map(pd.DataFrame(), '').save(CACHE_PATH + 'schedulemap/maps/empty.html')
semesters = route_inf['Semester'].unique()
copy_tree(CACHE_PATH + 'schedulemap/maps/', '/var/www/datascienceproject/assets/maps/')

print(f'{path} loaded')


@app.callback(
    Output('lmap', 'src'),
    Input('lcon-w', 'value'),
    Input('lcon-s', 'value'),
    Input('lcon-fs', 'value')
)
def update_left(winf, semester, fs):
    if fs == 'all':
        fs = '0'

    if winf not in ['inf', 'winf'] \
            or semester not in semesters \
            or semester[-1] == 'w' and fs not in ['0', '1', '3', '5'] \
            or semester[-1] == 's' and fs not in ['0', '2', '4', '6']:
        return dash.get_asset_url(f'maps/empty.html')
    return dash.get_asset_url(f'maps/{winf}_{semester}_{fs}.html')


@app.callback(
    Output('rmap', 'src'),
    Input('rcon-w', 'value'),
    Input('rcon-s', 'value'),
    Input('rcon-fs', 'value')
)
def update_right(winf, semester, fs):
    if fs == 'all':
        fs = '0'

    if winf not in ['inf', 'winf'] \
            or semester not in semesters \
            or semester[-1] == 'w' and fs not in ['0', '1', '3', '5'] \
            or semester[-1] == 's' and fs not in ['0', '2', '4', '6']:
        return dash.get_asset_url(f'maps/empty.html')
    return dash.get_asset_url(f'maps/{winf}_{semester}_{fs}.html')


layout = [
    html.Div(children=[
        html.H1(id='title', children=title),
        html.H3(children='Welche Wege müssen Studierende der Informatik bzw. Wirtschaftsinformatik in einem Semester '
                         'zurücklegen?'),
    ]),
    html.Div(children=[
        html.Div(className='map', children=[
            html.Div(className='left', children=[
                html.Div(className='mapcontrols', id='lcon', children=[
                    dcc.Dropdown(id='lcon-w', options=['inf', 'winf'], value='inf'),
                    dcc.Dropdown(id='lcon-s', options=semesters, value='2022w'),
                    dcc.Dropdown(id='lcon-fs', options=['all', '1', '2', '3', '4', '5', '6'], value='all')
                ]),
                html.Iframe(id='lmap', src=dash.get_asset_url('maps/inf_2015w_0.html'), width='100%', height='100%'),
            ]),
            html.Div(className='right', children=[
                html.Div(className='mapcontrols', id='rcon', children=[
                    dcc.Dropdown(id='rcon-w', options=['inf', 'winf'], value='winf'),
                    dcc.Dropdown(id='rcon-s', options=semesters, value='2022w'),
                    dcc.Dropdown(id='rcon-fs', options=['all', '1', '2', '3', '4', '5', '6'], value='all')
                ]),
                html.Iframe(id='rmap', src=dash.get_asset_url('maps/winf_2015w_0.html'), width='100%', height='100%')
            ])
        ]),
    ]),
    html.Div(children=[
        html.P('Aus diesen Karten konnten wir erkennen, dass die meisten Veranstaltungen in dem Bereich um der '
               'Ludewig-Meyn-Straße und dem Christian-Albrechts-Platz stattfinden und die Studenten eher kurze Wege '
               'beschreiten müssen. Hauptsächlich die Studierenden aus den ersten drei Fachsemestern müssen Richtung '
               'Leibnizstraße gehen.'),
        html.P('Im Gegensatz zu Informatikern haben die Wirtschaftsinformaitker auch im sechsten Fachsemester '
               'Pflichtmodule.')
    ])
]