from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("page1", href="/page1")),
                dbc.NavItem(dbc.NavLink("page2", href="/page2")),
            ] ,
            brand="Name of Dash App",
            brand_href="/page1",
            color="dark",
            dark=True,
        ),
    ])

    return layout