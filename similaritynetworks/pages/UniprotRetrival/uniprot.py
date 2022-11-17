import os
import pandas as pd
import requests
import io

def uniprot_retrieval(query_id):
    base = "https://rest.uniprot.org/uniprotkb/"
    query = "search?query="
    format = "&format=tsv"
    columns = "&fields=accession,id,gene_names,sequence,organism_name,organism_id,protein_name"
    result = requests.get(base + query + query_id + format + columns)
    df = pd.read_csv(io.StringIO(result.text), sep='\t')
    return df


blast_dataframe = pd.read_csv('../../Blast/blast.csv')
proteins = blast_dataframe['Protein1'].append(blast_dataframe['Protein2']).drop_duplicates()

df = pd.DataFrame()
process = 0
for protein in proteins:
    process = process + 1
    print(process)
    df = pd.concat([df, uniprot_retrieval(protein)], axis=0)

df.to_csv('uniprot.csv', index=False)