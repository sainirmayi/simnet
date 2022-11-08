import base64
import dash
import visualization
from dash import html, Input, Output,State, ctx
from dash import dcc
import dash_bootstrap_components as dbc
import re

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

    dbc.Row(dbc.Col(html.Div([
        dbc.Button('Accession search', id='accession', n_clicks=0, outline=True, color="info",className="me-1"),
        " or ",
        dbc.Button('Upload fasta', id='fasta', n_clicks=0, outline=True, color="success",className="me-1"),
    ]), width={"offset":2})

    ),

    dbc.Row(
            [
                dbc.Col(
                    dbc.Collapse(
                        dbc.Col("Protein ID",width={"offset": 4},),
                        id="accession_show1",
                        is_open=False,
                    )
                ),
            ],
            className="mt-3",),

    dbc.Row(
        [
            dbc.Col(
                dbc.Collapse(
                    dcc.Input(id='input'),
                    id="accession_show2",
                    is_open=False,
                ),
                width={"size": 3,"offset": 4},
            ),
        ],
        className="mt-3", ),

    dbc.Row(
        [
            dbc.Col(
                dbc.Collapse(
                    dcc.Upload(
                        id='upload_fasta',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                               ),
                    id="fasta_show",
                    is_open=False,
                ),
            ),
        ],
        className="mt-3", ),

        dbc.Row(
            html.Div(
                id='info_zone' ),),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Collapse(
                        html.Div(
                            id='plot_zone2' ),
                        id="fasta_show2",
                        is_open=True,
                    ),
                ),
            ],
            className="mt-3", ),

    html.Br(),
    dbc.Row(dbc.Col('Algorithm',width={"size": 3, "offset": 4},),),
    dbc.Row(
        dbc.Col(html.Div(
        dcc.Dropdown(id = 'Algorithm',
        options=[
        {'label': 'Blast', 'value': 'Blast'},
        {'label': 'Fasta', 'value': 'Fasta'},
         ],
         placeholder="Blast")),width={"size": 5,  "offset": 4},),),

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
                ),width={"size": 5,  "offset": 4},),)],)),
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
    Output('plot_zone2', 'children'),
    Input('search', 'n_clicks'), # dynamic input
    Input('upload_fasta', 'contents'),
    State('input', 'value'), # static input
    State('Algorithm', 'value'),
    State('n_neighbors', 'value')# static input
)

def showNetworkDiagram(n_clicks, content, proteinID, db,n_neighbors):
    if "search" == ctx.triggered_id and proteinID: #click or not
        visualization.get_visualization(proteinID, n_neighbors, db).show()
    elif content and "search" == ctx.triggered_id:
        fasta = base64.b64decode(content.split(',')[-1].encode('ascii')).decode()
        x = re.findall("^>.*", fasta)
        sequence = fasta.replace(f"{x[0]}", "")
        query = visualization.getProteinID(sequence)
        visualization.get_visualization(query, n_neighbors, db).show()

@homepage.callback(
    Output('accession_show1', "is_open"),
    Output('accession_show2', "is_open"),
    Output('fasta_show', "is_open"),
    Output('input', 'value'),
    Input("accession", "n_clicks"),
    Input("fasta", "n_clicks"),
    State('accession_show1', "is_open"),
    State('input', 'value'),
    State('accession_show2', "is_open"),
    State('fasta_show', "is_open"),
)



def show_accession(n_clicks1, n_clicks2, is_open1, value, is_open2, is_open3):
    if "accession" == ctx.triggered_id:
        if is_open1:
            return False, False, False, ''
        else:
            return True, True, False, value

    elif "fasta" == ctx.triggered_id:
        if is_open3:
            return False, False, False, ''
        else:
            return False, False, True, ''

    return is_open1, is_open2, is_open3, value

@homepage.callback(
    Output('info_zone', 'children'),
    Input('upload_fasta', 'contents'),
)

def file_upload_info(content):
    if content is not None:
        return "File uploaded successfully!"
    else:
        return "Please upload file!"


if __name__ == '__main__':
    homepage.run_server()