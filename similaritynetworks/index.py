from importlib import import_module

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from pages import homepage
from app import app

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Search", href="/", active="exact"),
                dbc.NavLink("Developer", href="/Developer", active="exact"),
                dbc.NavLink("page 2", href="/page2", active="exact"),
            ],

            brand="Name of app",
            color="primary",
            dark=True,
        ),
        dbc.Container(id="page-content", className="pt-4"),
    ]
)




@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return homepage.layout
    elif pathname == "/Developer":
        return html.P("deve")
    elif pathname == "/page2":
        return html.P("Oh cool, this is page 2!")
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