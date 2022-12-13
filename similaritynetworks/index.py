from importlib import import_module

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from pages import homepage, developerPage
from app import app

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.Navbar(
            children=[html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Div(html.Img(src=r'assets/SimNet.png', height = '60',width = '150',alt='image'),style={'display': 'inline-block','margin-left': '2vw', 'margin-right': '10vw', })),
                        dbc.Col(html.Div(dbc.NavLink("Single Search", href="/", active="exact",style={'color': '#fff'}),style={'margin-left': '60vw','color': '#fff'})),
                        dbc.Col(dbc.NavLink("Multi-Search", href="/Developer", active="exact",style={'color': '#fff'})),
                        dbc.Col(html.Div(dbc.NavLink("Help", href="/page2", active="exact",style={'color': '#fff'}))),
                        #html.Div(dbc.Col(html.Img(src=r'assets/SimNet.png', height = '50',width = '130',alt='image')),
                        #style={'display': 'inline-block','margin-left': '2vw', 'margin-right': '1vw', }),
                        #html.Div(dbc.Col(dbc.NavLink("Single Search", href="/", active="exact")),style={'display': 'inline-block'}),
                        #html.Div(dbc.Col(dbc.NavLink("Multi-Search", href="/Developer", active="exact")),style={'display': 'inline-block'}),
                        #html.Div(dbc.Col(dbc.NavLink("page 2", href="/page2", active="exact")),style={'display': 'inline-block'}),


                    ],
                    align="center",
                    className="g-0",
                ),
            style={"color": "white"}),
            ],

            #brand="Name of app",
            color="#385170",
            #dark=True,
        ),
        dbc.Container(id="page-content", className="pt-4"),
    ]
)




@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        # return html.P("Test")
        return homepage.layout
    elif pathname == "/Developer":
        return html.P("deve")
    elif pathname == "/page2":
        return developerPage.layout
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":
    app.run_server()