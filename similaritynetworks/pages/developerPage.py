import dash
from dash import html, Input, Output, callback
from dash import dcc
import os
import pandas as pd
layout = html.Div(
    [
        html.H1(
            children="SimNet Help and Documentation",
            style={'font-weight': 'bold'}
        ),

        html.Br(),

        html.Div(
            [
                html.H3(
                    children="Introduction",
                    style={'font-weight':'bolder'}
                ),
                html.Br(),
                html.Div(
                    children="SimNet is a protein similarity network web application. It provides a method to search and visualize the protein sequence similarity data. SimNet implements four search tools (BLAST, FastA, HMMER and SSearch) and has its own database. Currently, SimNet allows querying with any reviewed diatom protein.",
                    style={'textAlign': "justify"}
                ),
                html.Br(),
                html.H6(
                    children="Download full diatom protein list",
                    style={'font-weight': 'bolder'}
                ),
                html.Button("Download", id="download-txt"),
                dcc.Download(id="download"),

            ]
        ),

        html.Br(),
        html.Br(),

        html.Div(
            [
                html.H3(
                    children="Getting started",
                    style={'font-weight':'bolder'}
                ),
                html.Br(),
                html.H5(
                    children="Step 1 - Enter query data",
                    style={'font-weight':'bolder'}
                ),
                html.Br(),
                html.H6(
                    children="Enter accession number",
                    style={'font-weight': 'bolder'}
                ),
                html.Div(
                    children="The uniprot accession ID of the query protein can be directly enter to this form. Only one accession ID is allowed for single search. Note that the accession ID is case sensitive. Any white space should be avoided. An example accession ID is A0T097."
                ),
                html.Br(),
                html.H6(
                    children="Upload fasta file",
                    style={'font-weight': 'bolder'}
                ),
                html.Div(
                    children="This is an alternative input option. A file containing a valid sequence in FASTA format can be used as input for the similarity search."
                    ,style={'textAlign': "justify"}
                ),
                html.Br(),
                html.H5(
                    children="Step 2 - Search options",
                    style={'font-weight': 'bolder'}
                ),
                html.Br(),
                html.H6(
                    children="Basic setting",
                    style={'font-weight': 'bolder'}
                ),
                html.Div(
                    children="The alignment drop-down table contains four values: blast, fasta, hmmer and ssearch. These matches with four protein sequence similarity search tools. SimNet retrieves similarity results searched with the user-specified tool. Another option is the number of hits displayed on the network diagram. The diagram can show at most 20 proteins per query."
                    ,style = {'textAlign': "justify"}

),
                html.Br(),
                html.H6(
                    children="Advanced setting",
                    style={'font-weight': 'bolder'}
                ),
                html.Div(
                    children="In the advanced setting, a filter on the target organism is provided. Either search by organism name or organism ID is allowed. This filter is optional, the default setting includes all organisms in the database.",
                    style={'textAlign': "justify"}

                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Div([
            html.H3(
                children="SimNet result",
                style={'font-weight': 'bolder'}
            ),
            html.Br(),
            html.Div(
                html.Img(
                    src=r'assets/diagram.png', alt='image',
                    style={'display': 'inline-block', 'height': "400px", 'width': '1000px', 'vertical-align': 'top',
                           'margin-left': '0vw', 'margin-right': '0vw', 'margin-top': '0vw'}),
            ),
            html.H5(
                children="Network diagram",
                style={'font-weight': 'bolder'}
            ),

            html.Br(),
            html.Div(
                children="The network diagram is composed of a collection of nodes and edges. Nodes are proteins and edges represent associations. The line thickness is determined by the similarity score between the connected protein nodes, with the width and gradient of edges reduced for less centralized connections. The protein nodes are colored by the number of connections, indicated by the scale bar. An information field will be shown when hovering around a protein node. Similarity score and E value will be shown when hovering around the middle of an edge.",
                style={'textAlign': "justify"}

            ),

            html.Br(),
            html.H5(
                children="Information table",
                style={'font-weight': 'bolder'}
            ),
            html.Br(),
            html.Div(
                children="Two data tables are provided containing fundamental information about query proteins and connection proteins (indexed by similarity score with query protein). Protein information includes protein ID, uniprot entry, protein name, organism and similarity score."
            ),

            html.Br(),
            html.H5(
                children="AlphaFold predicted structure",
                style={'font-weight': 'bolder'}
            ),
            html.Br(),
            html.Div(
                children="Predicted 3D structure of the query protein is provided. The data is retrieved from AlphaFold database."
            ),
            html.Div(
                html.Img(
                    src=r'assets/structure.png', alt='image',
                    style={'display': 'inline-block', 'height': "300px", 'width': '300px', 'vertical-align': 'top',
                           'margin-left': '0vw', 'margin-right': '0vw', 'margin-top': '1vw'}),
            ),
            html.Br(),
            html.Br(),
        ]
        )
    ]
)

@callback(
    Output("download", "data"),
    Input("download-txt", "n_clicks")
)
def download(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    else:
        dir = os.getcwd()
        ndir = dir.replace("\\", "/")
        relativePath = "/pages/diatom_proteins/diatoms.csv"
        filePath = ndir + relativePath
        print(filePath)
        return dcc.send_file(filePath)




if __name__ == "__main__":
    developerPage.run_server()
