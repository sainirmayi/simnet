import pandas as pd
import dash_bio
from dash_bio_utils import PdbParser, create_mol3d_style
from pages.visualization import database_connection
import plotly.graph_objects as go


def getAlphaFoldStructure(proteinID):

    connection = database_connection()
    cur = connection.cursor()

    sql = """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
              WHERE TABLE_SCHEMA = 'protein_network' AND TABLE_NAME = 'protein'"""
    cur.execute(sql)
    columns = [item[0] for item in cur.fetchall()]

    results = pd.DataFrame()
    sql = f"""SELECT * FROM protein_network.protein WHERE Entry = %s"""
    cur.execute(sql, proteinID)
    results = pd.concat([results, pd.DataFrame(cur.fetchall(), columns=columns)], axis=0, ignore_index=True)

    cur.close()
    connection.close()

    id = results['AlphaFoldDB'].to_string(index=False)
    if id != '':
        alphafoldID = str(id).replace(';', '')
        DNA_pdb_file = "pages/UniprotRetrieval/alphafold/AF-"+alphafoldID+"-F1.pdb"
        # DNA_pdb_file = results['Alphafold_path'].to_string(index=False)
        parser = PdbParser(DNA_pdb_file)
        data = parser.mol3d_data()
        styles = create_mol3d_style(data["atoms"], visualization_type="cartoon", color_element="residue")
        return dash_bio.Molecule3dViewer(modelData=data, backgroundColor='#B2BFC4',
                                         backgroundOpacity=0.8,height = '350px',width = '335px' ,styles=styles)
