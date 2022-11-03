# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import Dash, html, dcc
import dash_defer_js_import as dji
from dash.dependencies import Input, Output
import plotly.express as px
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager
from config import CACHE_PATH

cache = diskcache.Cache(CACHE_PATH + 'disccache\\')

external_js = [

]
external_css = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css'  # Font Awesome
]

app = Dash(__name__,
           update_title=None,
           use_pages=True,
           external_scripts=external_js,
           external_stylesheets=external_css,
           assets_ignore='sidebar.js',
           background_callback_manager=DiskcacheLongCallbackManager(cache)
           )

server = app.server

app.layout = html.Div(id='app', children=[
    html.Header(children=[
        html.A(id='toggle-sidebar', className='open-sidebar', children=html.I(className='fa-solid fa-bars'), href='#'),
        html.Img(id='tf-logo', src=app.get_asset_url('tf-logo.svg')),
    ]),
    html.Div(id='main', children=[
        html.Section(id='sidebar', children=[
            html.A(id='close-sidebar', children=html.I(className='fa-solid fa-xmark'), href='#'),
            html.H2(children='Navigation'),
            html.Nav(children=[
                html.Div(
                    dcc.Link([html.Span(page['name'], className='name'), ' - ',
                              html.Span(page['path'], className='path')], href=page['relative_path'])
                )
                if 'hidden' not in page else None for page in dash.page_registry.values()
            ]),
        ]),
        html.Main(children=[
            dash.page_container
        ]),
    ]),
    html.Footer(children=[
        html.Div(children='Data Science Projekt 2022')
    ]),
    dji.Import(src=app.get_asset_url('sidebar.js'))
])

if __name__ == '__main__':
    app.run_server(debug=True)
