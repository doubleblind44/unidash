import os
import dash
from dash import html, dcc
import pandas as pd
from config import DB, CACHE_PATH
from python import english

title = 'Englisch'
path = '/english'

dash.register_page(__name__, name=title, path=path)

if not os.path.exists(CACHE_PATH + 'englisch\\'):
    os.makedirs(CACHE_PATH + 'englisch\\')
    df_tmp = english.englishs(DB)
    df = english.add_missing_semester(df_tmp)
    df = df.reset_index()
    df.to_json(CACHE_PATH + 'englisch/englishs.json')
else:
    df = pd.read_json(CACHE_PATH + 'englisch/englishs.json')

print(f'{path} loaded')

fig_a, fig_b = english.visualize(df)  # TODO: Add titles

layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H3(children='In welcher Fakultät finden die meisten Veranstaltungen auf Englisch statt?'),
    ]),
    html.Div(children=[
        dcc.Graph(
            id='english-a-graph',
            figure=fig_a,
            config={
                'displaylogo': False
            }
        )
    ]),
    html.Div(children=[
        dcc.Graph(
            id='english-rl-graph',
            figure=fig_b,
            config={
                'displaylogo': False
            }
        )
    ]),
    html.Div(children=[
        html.P('Insgesamt ist zu sehen, dass die absolute Anzahl an englischen Modulen bei allen Fakultäten steigt. '
               'Eine Ausnahme bildet die Philosophische Fakultät.'),
        html.P('Weiter ist auffällig, dass die Technische Fakultät seit 2009 im Wintersemester mehr englische Module '
               'anbietet als im Sommersemester. Im Wintersemester 2019 ist außerdem ein plötzlicher Anstieg zu sehen, '
               'der möglicherweise mit der Einführung der neuen Fachprüfungsordnung der Informatik zusammenhängen '
               'könnte.'),
        html.P('Die Darstellung des Anteils der englischsprachigen Veranstaltungen bestätigt die vorherige Auswertung. '
               'Ansonsten ist zu erkennen, dass der Anteil sich bei den meisten Fakultäten auf unter 25% beschränkt, '
               'lediglich die Technische Fakultät nähert sich stetig den 50% an.'),
        html.P('Anscheinend bieten die Medizinische und Theologische Fakultät keine englischen Module oder pflegen '
               'den entsprechenden Eintrag im UnivIS für die Modulsprache nicht.'),
    ])
]