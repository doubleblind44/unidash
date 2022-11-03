import os
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import python.rolli as rolli
from config import DB, CACHE_PATH
from python.faculty import FACULTY_COLORS

title = 'Rollstuhlgerechte Räume'
path = '/wheelchair'

dash.register_page(__name__, name=title, path=path)


if not os.path.exists(CACHE_PATH + 'rolli/'):
    os.makedirs(CACHE_PATH + 'rolli/')
    rolli_data = rolli.rollis(DB)
    df = pd.DataFrame().from_dict(rolli_data)
    df = df.reset_index(level=0)
    df = df.applymap(lambda x: x[2] if type(x) is tuple and len(x) >= 3 else x)
    df = pd.melt(df, id_vars=['index'])
    df = df.rename(columns={'index': 'Fakultät', 'variable': 'Semester', 'value': 'Prozentualer Anteil'})
    df.to_json(CACHE_PATH + 'rolli/rollis.json')
else:
    df = pd.read_json(CACHE_PATH + 'rolli/rollis.json')

print(f'{path} loaded')

fig = px.line(df, x='Semester', y='Prozentualer Anteil', color='Fakultät',
              color_discrete_map=FACULTY_COLORS)
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode='x')

layout = [
    html.Div(children=[
        html.H1(id='title', children=title),
        html.H3('Wie barrierefrei sind die Veranstalung der verschiedenen Fakultäten für Rollstuhlfahrende?'),
    ]),
    html.Div(children=[
        dcc.Graph(
            id='rolli-graph',
            figure=fig,
            config={
                'displaylogo': False
            }
        ),
        html.P('Es ist auffällig, dass der Anteil an Räumen, die mit einem Rollstuhl zugänglich sind, bei der '
               'Theologischen Fakultäten ab dem Sommersemester 2005 stetig gestiegen und im Wintersemester 2016 '
               'plötzlich gesunken ist. Weiter ist aufgefallen, dass der Anteil bei der Rechtswissenschaftlichen '
               'Fakultät im Sommersemester 2022 stark angestiegen ist. Dies lässt sich dadurch erklären, dass zu '
               'dieser Zeit das Juridicum fertiggestellt und eröffnet wurde. Zu der Medizinischen Fakultät lässt sich '
               'sagen, dass der Anteil im Wintersemester 2008 plötzlich angestiegen ist. Diese haben auch erst vier '
               'Jahre nach den anderen Fakultäten angefangen, den entsprechenden Eintrag im UnivIS zu pflegen. Als '
               'allgemeiner Trend ist zu beobachten, dass zu Beginn der Anteil steigt, bis ein Wert von ca. 50 % '
               'erreicht ist, dann bis Corona gleichbleibend ist und nach den Coronasemestern wieder auf ca. 50% '
               'ansteigt.')
    ])
]