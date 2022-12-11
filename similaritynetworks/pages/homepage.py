# import homepage as homepage
from dash import dash_table
from dash import html, Input, Output, State, ctx, callback
from dash import dcc
import dash_bootstrap_components as dbc

import pages.visualization
import UniprotRetrieval.alphafold_visualization
from pages.SupplementaryInfo import getInfoForSingleProtein, getInfoForConnectedProteins

# library used need to be specified here
# import app

# homepage = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
# components

# webpage design
from UniprotRetrieval.alphafold_visualization import getAlphaFoldStructure

layout = html.Div([html.Div([html.Div(
    [
        html.Br(),
        html.Br(),
        #html.Div([html.P("SEARCH")], style={'margin-left': '1vw','color': '#142d4c','font-size': '30px'}),
        dbc.Container(
            [
                dbc.Row(style={'height': '20px'}),

                dbc.Row(dbc.Col(html.Div([
                    dbc.Button('Accession search', id='accession', n_clicks=0, outline=True, color="info",
                               className="me-1"),
                    " OR ",
                    dbc.Button('Upload fasta', id='fasta', n_clicks=0, outline=True, color="success", className="me-1"),
                ]), )

                ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Collapse(
                                dbc.Col("Protein ID", ),
                                id="accession_show1",
                                is_open=False,
                            )
                        ),
                    ],
                    className="mt-3", ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Collapse(
                                dcc.Input(id='input'),
                                id="accession_show2",
                                is_open=False,
                            ),
                            width={"size": 3},
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
                        id='info_zone'), ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Collapse(
                                html.Div(
                                    id='plot_zone2'),
                                id="fasta_show2",
                                is_open=True,
                            ),
                        ),
                    ],
                    className="mt-3", ),

                dbc.Row(dbc.Col('Algorithm', width={"size": 3}, ), ),
                dbc.Row(
                    dbc.Col(html.Div(
                        dcc.Dropdown(id='Algorithm',
                                     options=[
                                         {'label': 'Blast', 'value': 'Blast'},
                                         {'label': 'Fasta', 'value': 'Fasta'},
                                         {'label': 'hmmer', 'value': 'hmmer'},
                                         {'label': 'ssearch', 'value': 'ssearch'},
                                     ],
                                     placeholder="Blast")), width={"size": 5}, ), ),
                html.Br(),

                dbc.Row(
                    dbc.Col(html.Label("Hit"), width={"size": 5}, )),
                dbc.Row(dbc.Col(
                    dcc.Dropdown(id='n_neighbors',
                                 options=[
                                     {'label': '5', 'value': 5},  # font needs to be adjusted
                                     {'label': '10', 'value': 10},
                                     {'label': '15', 'value': 15},
                                     {'label': '20', 'value': 20},
                                 ],
                                 placeholder="15",
                                 ), width={"size": 5}, ), ),

                html.Br(),
                dbc.Row(
                    html.Details(
                        contextMenu="s",
                        children=[
                            html.Summary(
                                children="Advanced Settings"  # set the name of the detail label
                            ),
                            #     dbc.Row(dbc.Col(
                            #     html.Div(
                            #     dcc.Dropdown(
                            #     options=[
                            #         {'label': '1', 'value': 'diatom'},
                            #         {'label': '2', 'value': 'human'},
                            #         ],
                            #         placeholder="Default score cut-off",
                            # )),width={"size": 5,  "offset": 4},),),

                            html.Br(),
                            dbc.Row(dbc.Col(html.Label("Target Organism:"), width={"size": 5}, )),
                            dbc.Row(dbc.Col(html.Div(
                                dcc.Dropdown(
                                    options=[
                                        {'label': "All", 'value': 0},
                                        {'label': "Acaryochloris marina [329726]", 'value': 329726},
                                        {'label': "Angiopteris evecta [13825]", 'value': 13825},
                                        {'label': "Aspergillus clavatus [344612]", 'value': 344612},
                                        {'label': "Aspergillus niger [425011]", 'value': 425011},
                                        {'label': "Bacillus anthracis [592021]", 'value': 592021},
                                        {'label': "Bacillus pumilus [315750]", 'value': 315750},
                                        {'label': "Bos taurus [9913]", 'value': 9913},
                                        {'label': "Branchiostoma floridae [7739]", 'value': 7739},
                                        {'label': "Chloroflexus aurantiacus [324602]", 'value': 324602},
                                        {'label': "Chlorokybus atmophyticus [3144]", 'value': 3144},
                                        {'label': "Cicer arietinum [3827]", 'value': 3827},
                                        {'label': "Coffea arabica [13443]", 'value': 13443},
                                        {'label': "Coprinopsis cinerea [240176]", 'value': 240176},
                                        {'label': "Crocosphaera subtropica [43989]", 'value': 43989},
                                        {'label': "Cyanothece sp. [395961]", 'value': 395961},
                                        {'label': "Desulfitobacterium hafniense [272564]", 'value': 272564},
                                    ],
                                    placeholder="All",
                                    multi=True
                                )), width={"size": 9}, ), ), ], )),
                html.Br(),
                dbc.Row(
                    dbc.Col(
                        dbc.Button('SEARCH', id='search',  className="me-1",n_clicks=0, style={'font-size': '20px','height':'50px','width':'120px','border': '0px','border-radius': '18px',}),
                        style={'text-align': 'center','font-size': '30px'})),
                html.Br(),

            ], ),  # style={
        #     'background-color': '#ededef',
        #    'max-width': '480px',
        # 'border-radius': '12px'

        #  }, ),# specify the search block style
        html.Br(),
    ], style={'color': '#142d4c','display': 'inline-block', 'vertical-align': 'top', 'margin-left': '-2vw', 'margin-right': '1vw',
              'margin-top': '0vw', 'height': '580px','width': '335px','backgroundColor': '#ececec','border-radius': '8px'}
),
html.Div(id='alphafold_zone',style={'margin-top': '1vw','margin-left': '-8vw','margin-right': '-3vw','width': '335px',
          'border-radius': '8px'}
    #[
     #   html.Br(),
      #  html.Div(html.Img(src=r'assets/logo.png', alt='image',style={'margin-left': '0.7vw','height':'50%', 'width':'50%'})),
       # html.Div([html.P(["M.Sc.Bioinfomatics", html.Br(), "Integrated Bioinformatics Project"])], style={'margin-left': '0.7vw','font-size': '18px'}),
        #html.Hr(),
        #html.Div([html.P(["Kato Milis, Sai Nirmayi Yasa",html.Br(),"Shuhua Liu, Wenjia Yu"])], style={"background-color":"#eaeaea",'width':'230px','margin-left': '0.7vw','font-size': '16px','border-radius': '8px'}),

        #html.Br()],
)],style={'display': 'inline-block'}),
        html.Div([
        html.Div(
            html.Div(html.Img(src=r'assets/intro.jpg', alt='image',
                              style={'margin-left': '0vw', 'height': '210%', 'width': '130%'})),id='intro_zone',
            style={'vertical-align': 'top', 'margin-left': '0vw', 'margin-right': '1vw', 'font-size': '100px','margin-top': '0vw'}),

        html.Div(
            id='plot_zone')],
            style={'display': 'inline-block', 'height':"600px",'width': '800px','vertical-align': 'top', 'margin-left': '0vw', 'margin-right': '-3vw','margin-top': '0vw'}),
        # html.Div(html.P("Input Protein"), style={'display': 'block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-top': '0vw','font-size': '12px'},),
        # html.Div(html.P("Sequence Similarity Partners"), style={'display': 'block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-top': '0vw','font-size': '12px'},)

])


@callback(
    Output('alphafold_zone', 'children'),
    Output('intro_zone', 'children'),
    Output('plot_zone', 'children'),
    Input('search', 'n_clicks'),
    State('input', 'value'),
    State('Algorithm', 'value'),
    State('n_neighbors', 'value')
)
def showNetworkDiagram(n_clicks, proteinID, Algorithm,n_neighbors):
    if n_neighbors is None:
        n_neighbors = 10
    if n_clicks:
        print('yes')
        return \
            html.Div([html.Label("AlphaFold Predicted Structure",style = {'margin-left':'6vw'}),getAlphaFoldStructure()]), '', \
            html.Div(dbc.Col([html.Div(dcc.Graph(
                id='network', figure=pages.visualization.get_visualization(proteinID, n_neighbors, Algorithm),
                style={'width': '130vh', 'height': '600px'}),style={'margin-top': '0vw','width': '130vh', 'height': '600px'}),
                html.Div([html.Div(html.P("Your Input"),
                         style={'font-size': '12px', "font-weight": "bold"}),
                html.Div(dash_table.DataTable(getInfoForSingleProtein(proteinID).to_dict('records'),
                                     [{"name": i, "id": i} for i in getInfoForSingleProtein(proteinID).columns],
                                     style_data={'whiteSpace': 'normal','height': 'auto',},style_cell={'textAlign': 'left'}, fill_width=False),style={'width': '130vh','margin-right': '3vw','margin-top': '-1vw',}),
                          html.Br(),
                html.Div([html.P("Sequence Similarity Partners")], style={'font-size': '12px', "font-weight": "bold"}),
                html.Div(dash_table.DataTable(
                    getInfoForConnectedProteins(proteinID, Algorithm, n_neighbors, 'tmp').to_dict('records'),
                    [{"name": i, "id": i} for i in
                     getInfoForConnectedProteins(proteinID, Algorithm, n_neighbors, 'tmp').columns],
                    style_data={'whiteSpace': 'normal','height': 'auto',},
                    style_cell={'textAlign': 'left'}),style={'margin-top': '-1vw',}),],style={'width': '130vh',"background-color":"#e7eaf6"})
                # dash_table.DataTable(
                # data=getInfoForConnectedProteins(proteinID,'tmp',n_neighors,'tmp').to_dict('records'),
                # columns = [{ 'name': x, 'id': x, 'type':'text', 'presentation': 'markdown'} if x == 'Links' else { 'name': x,'id': x}
                #           for x in getInfoForConnectedProteins(proteinID,'tmp',n_neighors,'tmp').columns],
                #         style_table = {'position': 'relative', 'top': '5vh', 'left': '5vw', 'width': '60vw'}
            ], style={'width': '100vh',"background-color":"#e7eaf6"}
            )
            )


@callback(
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


@callback(
    Output('info_zone', 'children'),
    Input('upload_fasta', 'contents'),
)
def file_upload_info(content):
    if content is not None:
        return "File uploaded successfully!"
    # else:
    #   return "Please upload file or provide a uniprot accession number!"


if __name__ == '__main__':
    homepage.run_server()
