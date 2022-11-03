import os
import dash
from dash import html, dcc
import pandas as pd
from config import DB, CACHE_PATH
from python import capacity

title = 'Raumauslastungen'
path = '/capacity'

dash.register_page(__name__, name=title, path=path)

if not os.path.exists(CACHE_PATH + 'capacity\\'):
    os.makedirs(CACHE_PATH + 'capacity\\')
    l, m, s, avl, avm, avs = capacity.capacity(DB)
    cl, cm, cs = capacity.capacity_corona(DB)
    df_l = capacity.get_dataframe(l)
    df_m = capacity.get_dataframe(m)
    df_s = capacity.get_dataframe(s)
    df_means = capacity.get_dataframe_for_mean(avl, avm, avs)
    df_cl = capacity.get_dataframe(cl)
    df_cm = capacity.get_dataframe(cm)
    df_cs = capacity.get_dataframe(cs)
    df_l.to_json(CACHE_PATH + 'capacity/large.json')
    df_m.to_json(CACHE_PATH + 'capacity/medium.json')
    df_s.to_json(CACHE_PATH + 'capacity/small.json')
    df_means.to_json(CACHE_PATH + 'capacity/means.json')
    df_cl.to_json(CACHE_PATH + 'capacity/cov-large.json')
    df_cm.to_json(CACHE_PATH + 'capacity/cov-medium.json')
    df_cs.to_json(CACHE_PATH + 'capacity/cov-small.json')
else:
    df_l = pd.read_json(CACHE_PATH + 'capacity/large.json')
    df_m = pd.read_json(CACHE_PATH + 'capacity/medium.json')
    df_s = pd.read_json(CACHE_PATH + 'capacity/small.json')
    df_means = pd.read_json(CACHE_PATH + 'capacity/means.json')
    df_cl = pd.read_json(CACHE_PATH + 'capacity/cov-large.json')
    df_cm = pd.read_json(CACHE_PATH + 'capacity/cov-medium.json')
    df_cs = pd.read_json(CACHE_PATH + 'capacity/cov-small.json')

print(f'{path} loaded')

fig_means, fig_l, fig_m, fig_s_a, fig_s_b = capacity.visualize_capacity(df_l, df_m, df_s, df_means)

fig_cl_a, fig_cm_a, fig_cs_a, fig_cl_b, fig_cm_b, fig_cs_b = capacity.visualize_corona(df_cl, df_cm, df_cs)

layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H2('Raumauslastungen insgesamt'),
        html.H3('In welchem Maße wurde die Raumkapazität genutzt?'),
    ]),
    html.Div(children=[
        dcc.Graph(
            id='cap-means-graph',
            figure=fig_means,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-l-graph',
            figure=fig_l,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-m-graph',
            figure=fig_m,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-s-a-graph',
            figure=fig_s_a,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-s-b-graph',
            figure=fig_s_b,
            config={
                'displaylogo': False
            }
        ),
        html.P('In dem Plot für die Räume mit einer Kapazität von mindestens 100 Personen ist zu erkennen, '
               'dass im Sommersemester 2021 die Raumauslastung aller Räume auf einmal konsequent sinkt. '
               'Dies scheint mit Corona zusammenzuhängen. Sonst ist auffällig, dass die Raumauslastung meistens '
               'unter 100% bleibt.'),
        html.P('Auffällig ist, dass einige mittlere Räumen seit einigen Jahren im Wintersemester '
               'stark überbelegt wurden.'),
        html.P('Bei den kleinen Räumen sind Häufungen z.B. bei einer Raumauslastung von 50% sichtbar. Unter 50% sind '
               'im Vergleich eher weniger Räume belegt. Dies erweckt den Eindruck, dass darauf geachtet wird, die '
               'kleinen Räume mit mindestens 50% zu belegen.'),
        html.P('Wenn man sich die Mittelwerte anschaut, fällt auf, dass die größeren Räume die geringste und die '
               'kleineren Räume die höchste Raumauslastung aufweisen. Dabei bewegt sich die durchschnittliche '
               'Raumauslastung der mittleren und größeren Räume immer unter 100%, was darauf schließen lässt, '
               'dass diese Räume ihre Kapazitäten im Durchschnitt nicht vollständig ausschöpfen. Weiter ist erkennbar, '
               'dass die kleineren Räume im Vergleich zu den anderen Räumen stark bis überbelegt werden.')
    ]),
    html.Div(children=[
        html.H2('Raumauslastungen während Corona'),
        html.H3('Wie sehr wurde die Raumkapazität während Corona verringert?'),
        dcc.Graph(
            id='cap-cl-a-graph',
            figure=fig_cl_a,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-cm-a-graph',
            figure=fig_cm_a,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-cs-a-graph',
            figure=fig_cs_a,
            config={
                'displaylogo': False
            }
        ),
        html.P('Im Zuge der Pandemie wurde die Kapazität der großen Räume in der Regel auf ca. 10% bis 18% der '
               'ursprünglichen Kapazität reduziert. Bei den mittleren Räumen wurde die Kapazität nicht ganz so stark '
               'verringert, aber befindet sich immer noch im Bereich von unter 50%. Die Kapazität der kleinen Räume '
               'wurde auf ca. 14% bis 70% reduziert, was deutlich über den Anteil der anderen Raumgrößen liegt.'),
        html.H3('In welchem Maße wurde die reduzierte Raumkapazität während Corona genutzt?'),
        dcc.Graph(
            id='cap-cl-b-graph',
            figure=fig_cl_b,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-cm-b-graph',
            figure=fig_cm_b,
            config={
                'displaylogo': False
            }
        ),
        dcc.Graph(
            id='cap-cs-b-graph',
            figure=fig_cs_b,
            config={
                'displaylogo': False
            }
        ),
        html.P('Es fällt auf, dass bei den größeren Räumen im Sommersemester 2020 stark darauf geachtet wurde, '
               'die Räume mit weniger Personen zu belegen. Aber in den folgenden Semestern ist die Raumauslastung '
               'je nach Raum sehr unterschiedlich und wieder stark angestiegen. Die mittleren Räume wurden während '
               'Corona allgemein nicht stark belastet und die kleineren Räume wurden wieder teilweise überbelegt.')
    ])
]
