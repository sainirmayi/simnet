import os
import dash
from dash import html
import dash_bio
from dash_bio_utils import PdbParser, create_mol3d_style

def getAlphaFoldStructure():
    print(os.getcwd())
    DNA_pdb_file = os.getcwd()+'/UniprotRetrieval/AF-A0T0A1-F1-model_v4.pdb'
    parser = PdbParser(DNA_pdb_file)

    data = parser.mol3d_data()
    styles = create_mol3d_style(
    data["atoms"], visualization_type="cartoon", color_element="residue"
    )
    return dash_bio.Molecule3dViewer(modelData=data, backgroundColor='#B2BFC4',
    backgroundOpacity=0.8,height = '350px',width = '335px' ,styles=styles)



