import os
import dash
from dash import html, dcc
import pandas as pd
from config import DB, CACHE_PATH
from python import bestProf as bp

title = 'Best Prof'
path = '/best-prof'

dash.register_page(__name__, name=title, path=path)

if not os.path.exists(CACHE_PATH + 'bestprof/'):
    os.makedirs(CACHE_PATH + 'bestprof/')

    df_lecture = bp.create_lecture_df(DB)
    df_all_moduls = bp.create_df_all_moduls(DB)
    df_ects = bp.create_ects_df(df_lecture, DB)
    df_orgname = bp.create_orgname(df_lecture, DB)
    df_modul_time = bp.create_modul_time(df_lecture, DB)

    df_lecture = df_lecture.reset_index()
    df_all_moduls = df_all_moduls.reset_index()
    df_ects = df_ects.reset_index()
    df_orgname = df_orgname.reset_index()
    df_modul_time = df_modul_time.reset_index()

    df_lecture.to_json(CACHE_PATH + 'bestprof/lecture.json')
    df_all_moduls.to_json(CACHE_PATH + 'bestprof/all_moduls.json')
    df_ects.to_json(CACHE_PATH + 'bestprof/ects.json')
    df_orgname.to_json(CACHE_PATH + 'bestprof/orgname.json')
    df_modul_time.to_json(CACHE_PATH + 'bestprof/modul_time.json')
else:
    df_lecture = pd.read_json(CACHE_PATH + 'bestprof/lecture.json')
    df_all_moduls = pd.read_json(CACHE_PATH + 'bestprof/all_moduls.json')
    df_ects = pd.read_json(CACHE_PATH + 'bestprof/ects.json')
    df_orgname = pd.read_json(CACHE_PATH + 'bestprof/orgname.json')
    df_modul_time = pd.read_json(CACHE_PATH + 'bestprof/modul_time.json')

fig_lec = bp.visualization_lecture(df_lecture)
fig_ects = bp.visualization_ects_lineplot_year(df_ects, df_all_moduls)
fig_orgs = bp.visualization_orgname_all(df_orgname)
fig_t_a = bp.visualization_modul_time_days_pie(df_modul_time)
fig_t_b = bp.visualization_modul_time_hours_pie(df_modul_time)

print(f'{path} loaded')


layout = [
    html.Div(children=[
        html.H1(id='title', children=title),

        html.H2('Können durch die Auswertung der Daten aus dem UnivIS die Platzierungen des '
                '"Best Prof Awards Informatik 2022" richtig vorhergesagt werden?'),
        html.P(['Wir haben die Platzierungen für den Zeitraum 2010 – 2019. Der Award wird immer im Sommer vergeben. ',
                'Zu einem "Awardjahr" gehören also Module des aktuellen Sommersemesters sowie des im vorherigen Jahr ',
                'beginnenden Wintersemesters.', html.Br(),
                'Wir stellen hier einige von uns durchgeführte Analysen als Beispiel vor.'])
    ]),
    html.Div(children=[
        html.H3('Häufige Module:'),
        html.P(['Welche Module aus der Awardmodulliste sind die häufigsten? ',
                'Ist ein Sieg durch ein bestimmtes Modul garantiert?']),
        dcc.Graph(
            id='best-prof-lec-graph',
            figure=fig_lec,
            config={
                'displaylogo': False
            }
        ),
        html.P(['Auffallend ist das \'Hardwarepraktikum\' mit einer Häufigkeit von 8 als Spitzenreiter. '
                'Da es jedes Semester (bis SS18) angeboten wird, war es also 4 Jahre unter den Top 3.', html.Br(),
                'Laut ModulDB finden von allen genannten Modulen nur noch \'Computersysteme\', '
                '\'Logik in der Informatik\' und das \'Masterseminar - Programmiersprachen und Programmiersysteme\' '
                'statt.']),
    ]),
    html.Div(children=[
        html.H3('Anzahl ECTS:'),
        html.P(['Werden Lehrpersonen gewählt, die im Schnitt eher zeitaufwändige Module mit vielen ECTS anbieten?']),
        dcc.Graph(
            id='best-prof-ects-graph',
            figure=fig_ects,
            config={
                'displaylogo': False
            }
        ),
        html.P(['Die ECTS-Gesamtanzahl der Awardmodule hat je nach Platzierung Ausreißer in unterschiedlichen Jahren, '
                'sinkt aber im Jahresverlauf.', html.Br(),
                'Erkennbar ist, dass der Durchschnitt aller Module im Vergleich zu den Best Prof Modulen weniger stark '
                'schwankt und sich durchgehend im Bereich 5,8 bis 6,9 ECTS pro Modul befindet.']),
    ]),
    html.Div(children=[
        html.H3('Verteilung der Institutionen/Arbeitsgruppen:'),
        html.P('Wird der Best Prof wegen der Arbeitsgruppe gewählt oder besteht eine breite Verteilung durch alle '
               'Arbeitsgruppen des Instituts?'),
        dcc.Graph(
            id='best-prof-orgs-graph',
            figure=fig_orgs,
            config={
                'displaylogo': False
            }
        ),
        html.P(['Bis zum 01.10.2018 gab es die Arbeitsgruppe "Technische Informatik". Seit dem 01.10.2018 wurde daraus '
                'die Arbeitsgruppe "Verteilte Systeme".', html.Br(),
                'Somit haben wir zur besseren Übersicht & Auswertung alle Module der "Technischen Informatik" der AG '
                '"Verteilte Systeme" zugeordnet und stellen diese AG also schon dar, bevor es sie gab.']),
        html.P(['Die Gesamtübersicht zeigt, dass sich “Echtzeitsysteme / Eingebettete Systeme”, “Programmiersprachen '
                'und Übersetzerkonstruktion”, “Theoretische Informatik” und “Verteilte Systeme” klar absetzten mit '
                'einer Häufigkeit im Bereich 34 - 63. Alle anderen Arbeitsgruppen bleiben unter 15 zugehörigen '
                'Modulen.', html.Br(),
                'Es fällt auf, dass die eben 4 genannten Module Phasen hatten, bei denen sie mehrere Jahre (3- 4) '
                'hintereinander in die Top 3 gekommen sind.']),
    ]),
    html.Div(children=[
        html.H3('Beliebte Vorlesungszeiten:'),
        html.P(['Können wir einen Trend bei den Vorlesungszeiten finden? Sind Profs von montags 8 Uhr Vorlesungen '
                'benachteiligt?']),
        dcc.Graph(
            id='best-prof-t-a-graph',
            figure=fig_t_a,
            config={
                'displaylogo': False
            }
        ),
        html.P(['Der häufigste Vorlesungstag, der vorkommt, ist mit 26,4 % Mittwoch, dicht gefolgt von Dienstag und '
                'Donnerstag.', html.Br(),
                'Montag, Freitag und Samstag schneiden nicht so gut ab.']),
        dcc.Graph(
            id='best-prof-t-b-graph',
            figure=fig_t_b,
            config={
                'displaylogo': False
            }
        ),
        html.P(['Die häufigste Startzeit ist 10:00 Uhr mit 17,9 %. '
                'Erstaunlich für alle "Langschläfer" ist, dass 08:00 Uhr mit 11,7 % an zweiter Stelle ist.'])
    ]),
    html.Div(children=[
        html.H3('Wer wurde nach unserer Auswertung Best Prof 2022?'),
        html.P(['Wir haben Prof. Dr. Olaf Landsiedel, Dr. Barbara Langfeld und Prof. Dr. Andreas Mühling als '
                'Best Profs 2022 bestimmt.', html.Br(),
                'Eine genaue Platzierung ist mit unseren Analyseergebnissen nicht möglich.']),
    ]),
    html.Div(children=[
        html.H3('Wer wurde wirklich Best Prof 2022?'),
        html.P(['Platz 1: Dr. Barbara Langfeld', html.Br(),
                'Platz 2: Prof. Dr. Olaf Landsiedel', html.Br(),
                'Platz 3: Prof. Dr. Thomas Wilke.', html.Br(),
                'Mit unserer Auswertung haben wir somit zwei von drei Best Profs des Jahres 2022 richtig '
                'vorhersagen können.']),
    ])
]