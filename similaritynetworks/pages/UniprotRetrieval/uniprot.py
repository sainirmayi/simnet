import os
import pandas as pd
import requests
import io


def uniprot_retrieval(query_id):
    base = "https://rest.uniprot.org/uniprotkb/"
    query = "search?query="
    format = "&format=tsv"
    columns = "&fields=accession,id,gene_primary,gene_names,sequence,organism_name,organism_id,protein_name,protein_families,xref_alphafolddb, xref_pdb, cc_function,ec,cc_pathway,ph_dependence,temp_dependence"
    result = requests.get(base + query + query_id + format + columns)
    df = pd.read_csv(io.StringIO(result.text), sep='\t')
    return df


if __name__ == '__main__':
    blast_dataframe = pd.read_csv('../Blast/blast.csv')
    blast_proteins = blast_dataframe['Protein1'].append(blast_dataframe['Protein2']).drop_duplicates()
    print(len(blast_proteins))

    ssearch_dataframe = pd.read_csv('../FASTA/ssearch.csv')
    ssearch_proteins = ssearch_dataframe['Protein1'].append(ssearch_dataframe['Protein2']).drop_duplicates()
    print(len(ssearch_proteins))

    fasta_dataframe = pd.read_csv('../FASTA/fasta.csv')
    fasta_proteins = fasta_dataframe['Protein1'].append(fasta_dataframe['Protein2']).drop_duplicates()
    print(len(fasta_proteins))

    hmmer_dataframe = pd.read_csv('../Hmmer/HmmerWithSecondSearch.csv')
    hmmer_proteins = hmmer_dataframe['Protein1'].append(hmmer_dataframe['Protein2']).drop_duplicates()
    print(len(hmmer_proteins))


    proteins = blast_proteins.append(ssearch_proteins).append(hmmer_proteins).append(fasta_proteins).drop_duplicates()
    print(proteins)

    df = pd.DataFrame()
    process = 0
    for protein in proteins:
        process = process + 1
        print(process)
        df = pd.concat([df, uniprot_retrieval(protein)], axis=0)

    df.to_csv('uniprot.csv', index=False)