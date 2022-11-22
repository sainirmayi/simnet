import os

from Bio.PDB import *
import pandas as pd

uniprot = pd.read_csv('uniprot.csv')
alphafold = uniprot['AlphaFoldDB'].dropna()
print(alphafold)

isexist = os.path.exists('../UniprotRetrieval/alphafold')
if not isexist:
    os.makedirs('../UniprotRetrieval/alphafold')

os.chdir('../UniprotRetrieval/alphafold')

process = 0

for id in alphafold:
    id = id.replace(';', '')
    print(id)
    process = process + 1
    print(process)
    alphafold_ID = 'AF-' + id + '-F1'
    database_version = 'v2'
    model_url = f'https://alphafold.ebi.ac.uk/files/{alphafold_ID}-model_{database_version}.pdb'
    #error_url = f'https://alphafold.ebi.ac.uk/files/AF-{alphafold_ID}-F1-predicted_aligned_error_{database_version}.json'
    os.system(f'curl {model_url} -o {alphafold_ID}.pdb')
    #os.system(f'curl {error_url} -o {alphafold_ID}.json')

#pdbl = PDBList()

#os.makedirs('../pdb')
#os.chdir("../pdb")
#for pdb_id in pdb:
#    pdbl.retrieve_pdb_file(pdb_id)