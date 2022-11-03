import os
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from python.faculty import FACULTY_COLORS
import python.genderdata as genderdata
from dash.dependencies import Input, Output
from config import DB, CACHE_PATH

title = 'Geschlechterverteilung'
path = '/genders'

dash.register_page(__name__, name=title, path=path)

app = dash.get_app()

df_cache = {'True': {}, 'False': {}}
if not os.path.exists(CACHE_PATH + 'genders/'):
    os.makedirs(CACHE_PATH + 'genders/')
    for i in range(101):
        df_cache['True'][i] = genderdata.get_gender_data(DB, True, i, 0)
        df_cache['False'][i] = genderdata.get_gender_data(DB, False, i, 0)
        df_cache['True'][i].to_json(CACHE_PATH + 'genders/' + str(i) + '_True.json')
        df_cache['False'][i].to_json(CACHE_PATH + 'genders/' + str(i) + '_False.json')
else:
    for i in range(101):
        df_cache['True'][i] = pd.read_json(CACHE_PATH + 'genders/' + str(i) + '_True.json')
        df_cache['False'][i] = pd.read_json(CACHE_PATH + 'genders/' + str(i) + '_False.json')

print(f'{path} loaded')


# TODO: hinweis auf gender API

@app.callback(
    Output('gender-graph', 'figure'),
    Input('input-female', 'value'),
    Input('input-prob', 'value'),
    running=[
        (Output('input-prob', 'disabled'), True, False),
    ]
)
def update_graph(f, p):
    f = str(str(f) == 'True')
    p = int(p)
    df = df_cache[f][p]

    fig = px.line(df, x='Semester', y='Prozentualer Anteil', color='Fakultät', title='',
                  custom_data=['Anzahl', 'Gesamt'], color_discrete_map=FACULTY_COLORS)
    fig.update_traces(hovertemplate='<br>'.join([
        'Anteil: %{y:.2f}%',
        'Anzahl: %{customdata[0]}',
        'Gesamt: %{customdata[1]}'
    ]))

    return fig


@app.callback(
    Output('input-prob-value', 'children'),
    Input('input-prob', 'value'),
)
def update_graph(p):
    return f'{p}%'


layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H3(children='Wie hat sich der Anteil von Mitarbeitenden mit nicht-männlich erkannten Vornamen entwickelt?'),
    ]),
    html.Div(children=[
        dcc.Input(id='input-prob', type='range', min=0, max=100, step=1, value=75),
        html.Span(id='input-prob-value', children='75%'),
        dcc.RadioItems(id='input-female', value='False', options=[
            {
                "label": html.Div(id='fnm-nm', className='female-not-male', children=[
                        html.I(className='fa-solid fa-mars'),
                        html.I(className='fa-solid fa-ban'),
                    ]
                ),
                "value": 'False',
            },
            {
                "label": html.Div(id='fnm-f', className='female-not-male', children=[
                        html.I(className='fa-solid fa-venus'),
                    ]
                ),
                "value": 'True',
            },
        ]),
        dcc.Graph(
            id='gender-graph',
            config={
                'displaylogo': False
            }
        ),
        html.P('Die Theologische Fakultät hat sich am meisten entwickelt: Der Anteil von Mitarbeitenden mit '
               'nicht-männlich erkannten Vornamen startet im Sommersemester 2000 bei ca. 21% und '
               'liegt im Wintersemester 2022/23 bei ca. 54%.'),
        html.P('Die Medizinische Fakultät befindet sich seit dem Wintersemester 2006 immer über 50%. '
               'Die Technische Fakultät erreicht hingegen nicht einmal einen Wert von 30%.'),
        html.P('Die Anteile der anderen Fakultäten steigen stetig, aber bleiben relativ konstant. '
               'Dabei erreicht keine Fakultät die 60%-Marke.'),
        html.P('(Diese Auswertung bezieht sich auf eine Wahrscheinlichkeit einer richtigen Klassifizierung von 75%.)'),
        html.Span(['Die Namen wurden den Geschlechtern durch die API von ',
                   dcc.Link('genderapi.io', href='https://genderapi.io/'), ' zugeordnet.'], className='source'),
    ])
]
