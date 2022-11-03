import os
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import python.workload as workload
from python.faculty import FACULTY_COLORS
from config import DB, CACHE_PATH

title = 'Vorlesungen pro Person'
path = '/workload'

dash.register_page(__name__, name=title, path=path)

app = dash.get_app()


if not os.path.exists(CACHE_PATH + 'workload/'):
    os.makedirs(CACHE_PATH + 'workload/')
    df = workload.workloads(DB)
    df.to_json(CACHE_PATH + 'workload/workload.json')
else:
    df = pd.read_json(CACHE_PATH + 'workload/workload.json')

print(f'{path} loaded')


fig = px.line(df, x="Semester", y="Arbeitsbelastung", color="Fakultät", title='', color_discrete_map=FACULTY_COLORS)
fig.update_traces(hovertemplate='<br>'.join([
    'Arbeitsbelastung: %{y:.2f} Durchschnittliche Vorlesungen pro Lehrperson'
]))
fig.update_layout(hovermode='x')


layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H3(children='Wie hat sich die Arbeitsbelastung einer Lehrperson bezüglich Lehrveranstaltungen entwickelt?'),
    ]),
    html.Div(children=[
        dcc.Graph(
            id='workload-graph',
            figure=fig,
            config={
                'displaylogo': False
            }
        ),
        html.P('Die Arbeitsbelastung einer Lehrperson der medizinischen Fakultät ist von 4,56 durchschnittlichen '
               'Veranstaltungen pro Lehrperson auf 1,8 stark gesunken. Wenn sich die Arbeitsbelastung einer Fakultät '
               'erhöht hat, dann lediglich um höchstens eine Veranstaltung im untersuchten Zeitraum. Sonst ist '
               'aufgefallen, dass die Arbeitsbelastung bei manchen Fakultäten davon abhängig ist, ob gerade Sommer- '
               'oder Wintersemester ist. Zum Beispiel bei der Technischen Fakultät war ab dem Sommersemester 2013 die '
               'Arbeitsbelastung im Winter höher als im Sommer. Dies kehrte sich im Wintersemester 2021 um, was unter '
               'anderem auf die neue Fachprüfungsordnung der Informatik zurückzuführen sein könnte.')
    ])
]
