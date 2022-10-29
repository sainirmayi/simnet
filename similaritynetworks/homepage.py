
#from dash import html
#from dash import dcc
import dash

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pip
homepage = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
homepage.layout = html.Div(
    [
    dbc.Row(dbc.Col('Name',width={"size": 3, "offset": 0},),),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
        dbc.Container(
    [
    dbc.Row(style={'height': '30px'}),
    dbc.Row(
                dbc.Col('Protein ID',width={"offset": 4},),),
    dbc.Row(dbc.Col(dcc.Input(id = "ProteinID"),width={"size": 3,  "offset": 4},)),

    html.Br(),
    dbc.Row(dbc.Col('Algorithm',width={"size": 3, "offset": 4},),),
    dbc.Row(
        dbc.Col(html.Div(
        dcc.Dropdown(
        options=[
        {'label': 'Blast', 'value': 'Blast'},
        {'label': 'SSearch', 'value': 'SSearch'}
         ],
         placeholder="Blast",
         multi=True)),width={"size": 5,  "offset": 4},),),

    html.Br(),
    dbc.Row(
         dbc.Col(html.Label("Target Organism:"), width={"size": 5, "offset": 4},)),

    dbc.Row(        dbc.Col(html.Div(
                dcc.Dropdown(
                    options=[
                        {'label': 'Bacillariophyceae', 'value': 'diatom'},
                        {'label': 'Homo sapiens', 'value': 'human'}
                    ],
                    placeholder="Original Organism",
                    multi=True
                )), width={"size": 5, "offset": 4},),
        ),
    html.Br(),
    dbc.Row(
        html.Details(
        contextMenu = "s",
            children = [
            html.Summary(
                children="Advanced Settings" #set the name of the detail label
            ),
            dbc.Row(dbc.Col(
            html.Div(
            dcc.Dropdown(
            options=[
                {'label': '1', 'value': 'diatom'},
                {'label': '2', 'human': 'human'},
                ],
                placeholder="Select threshold score",
        )),width={"size": 5,  "offset": 4},),),
            html.Br(),
            dbc.Row(dbc.Col(
            dcc.Dropdown(
            options=[
                {'label': '1', 'value': 'diatom'},
                {'label': '2', 'human': 'human'},
                ],
                placeholder="Size cutoff",
                ),width={"size": 5,  "offset": 4},),  )],)),
    html.Br(),
    dbc.Row(
        dbc.Col(
            dbc.Button('SEARCH', style={'border-radius': '18px'}),
            width={'size': 10, 'offset': 2},
            style={'text-align': 'center'})),

        ], style={
                'background-color': '#ededef',
                'max-width': '480px',
                'border-radius': '12px'
            })

    ])

if __name__ == '__main__':
    homepage.run_server()