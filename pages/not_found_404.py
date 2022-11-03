import dash
from dash import html

dash.register_page(__name__, hidden=True)

layout = [
    html.Div(children=[
        html.Div(id='error404', children=[
            html.H1('404'),
            html.P('Die angeforderte Seite konnte nicht gefunden werden.')
        ])
    ])
]