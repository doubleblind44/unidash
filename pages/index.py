import dash
from dash import html

title = 'Home'
path = '/'

dash.register_page(__name__, name='Home', path=path)

layout = [
    html.Div(children=[
        html.H1(id='title', children=title),
        html.P('Auf dieser Seite befinden sich die Ergebnisse unserer UnivIS-Analyse.'),
    ]),
    html.Div(children=[

    ])
]