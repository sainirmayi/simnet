import os
from os import path
from Bio.PDB import *
import pandas as pd

uniprot = pd.read_csv('uniprot.csv')
alphafold = uniprot['AlphaFoldDB']
print(alphafold)

isexist = os.path.exists('../UniprotRetrieval/alphafold')
if not isexist:
    os.makedirs('../UniprotRetrieval/alphafold')

#os.chdir('../UniprotRetrieval/alphafold')

alphafold_path = []
for id in alphafold:
    id = str(id).replace(';', '')
    if id == 'nan':
        alphafold_path.append('')
    else:
        alphafold_ID = 'AF-' + id + '-F1'
        if path.exists(f"../UniprotRetrieval/alphafold/{alphafold_ID}.pdb"):
                alphafold_path.append(f"../UniprotRetrieval/alphafold/{alphafold_ID}.pdb")
        else:
            database_version = 'v2'
            model_url = f'https://alphafold.ebi.ac.uk/files/{alphafold_ID}-model_{database_version}.pdb'
            os.chdir('../UniprotRetrieval/alphafold')
            os.system(f'curl {model_url} -o {alphafold_ID}.pdb')
            os.chdir('..')
            alphafold_path.append(f"../UniprotRetrieval/alphafold/{alphafold_ID}.pdb")

print(alphafold_path)

uniprot['alphafold_path'] = alphafold_path
uniprot.to_csv('uniprot_alphafold.csv', index=False)