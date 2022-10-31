import dash
import visualization
from dash import html, Input, Output,State
from dash import dcc
import dash_bootstrap_components as dbc

# library used need to be specified here
homepage = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#wehpage design
homepage.layout = html.Div(
    [
    dbc.Row(dbc.Col('Name',width={"size": 3, "offset": 0},),),
    html.Br(),#blank
    html.Hr(),#line
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
    dbc.Row(dbc.Col(dcc.Input(id = 'input'),width={"size": 3,  "offset": 4},)),

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

    dbc.Row(dbc.Col(html.Div(
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
                placeholder="Default score cut-off",
        )),width={"size": 5,  "offset": 4},),),
            html.Br(),
            dbc.Row(dbc.Col(
            dcc.Dropdown(id = 'n_neighbors',
            options=[
                {'label': 'No more than 5 interactors', 'value': 5},#font needs to be adjusted
                {'label': 'No more than 10 interactors', 'value': 10},
                {'label': 'No more than 15 interactors', 'value': 15},
                {'label': 'No more than 20 interactors', 'value': 20},
                ],
                placeholder="no more than 15 interactors",
                ),width={"size": 5,  "offset": 4},),  )],)),
    html.Br(),
    dbc.Row(
        dbc.Col(
            dbc.Button('SEARCH', id= 'search',style={'border-radius': '18px'},n_clicks=0),
            width={'size': 10, 'offset': 2},
            style={'text-align': 'center'})),

        ], style={
                'background-color': '#ededef',
                'max-width': '480px',
                'border-radius': '12px'
            }),# specify the search block style
    dbc.Row(
        html.Div(
            id='plot_zone' ),) # empty block that ready to receive the diagram
    ])


@homepage.callback(
    Output('plot_zone', 'children'),
    Input('search', 'n_clicks'), # dynamic input
    State('input', 'value'), # static input
    State('n_neighbors', 'value')# static input
)
def showNetworkDiagram(n_clicks,proteinID,n_neighors):
    if n_clicks: #click or not
        return html.Div( # return a whole block containing network digram
           dcc.Graph(
                id='network',figure = visualization.get_visualization(proteinID,n_neighors)))

if __name__ == '__main__':
    homepage.run_server()