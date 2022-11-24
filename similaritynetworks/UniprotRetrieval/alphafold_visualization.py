import os
import dash
from dash import html
import dash_bio
from dash_bio_utils import PdbParser, create_mol3d_style

print(os.getcwd())
app = dash.Dash(__name__)
DNA_pdb_file = '../UniprotRetrieval/alphafold/AF-O93875-F1.pdb'
parser = PdbParser(DNA_pdb_file)

data = parser.mol3d_data()
styles = create_mol3d_style(
    data["atoms"], visualization_type="cartoon", color_element="residue"
)
app.layout = html.Div([dash_bio.Molecule3dViewer(modelData=data, styles=styles)])

if __name__ == '__main__':
    app.run_server()

