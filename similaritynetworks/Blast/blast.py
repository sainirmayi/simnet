import os
import shutil
import xml.etree.ElementTree as ET
from os import path

import numpy as np
import pandas as pd
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML


#function to split the fasta sequences in the fasta file into different files
def split_fasta(fastafile):
    f = open(fastafile, "r")
    os.chdir(os.getcwd() + "/separated_sequences")
    outfile = []
    for line in f:
        if line.startswith(">"):
            if outfile != []:
                outfile.close()
            genename = line.strip().split('|')[1]
            filename = genename + ".fasta"
            outfile = open(filename, 'w')
            outfile.write(line)
        else:
            outfile.write(line)
    outfile.close()
    return outfile

#function to do a blast search for a certain protein, input has to be a fastafile
def blast_search(fastafile):
    sequence_data = open(file).read()
    result_handle = NCBIWWW.qblast("blastp", "swissprot", sequence_data, format_type="XML", alignments=1, hitlist_size=20)
    with open(f"{file}_blast.xml", 'w') as save_file:
        blast_results = result_handle.read()
        save_file.write(blast_results)

def blast_search_ID(proteinID):
    result_handle = NCBIWWW.qblast("blastp", "swissprot", proteinID, format_type="XML", alignments=1,
                                   hitlist_size=20)
    with open(f"{proteinID}_blast.xml", 'w') as save_file:
        blast_results = result_handle.read()
        save_file.write(blast_results)

#function to parse the blast output, input has to be a xml file
def parse_blast(xmlfile):
    blast_records = []

    result = open(xmlfile, "r")
    records = NCBIXML.parse(result)
    item = next(records)

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for app in root.findall('BlastOutput_db'):
        DB = ("%s" % (app.text));

    i=0
    for alignment in item.alignments:
        hsp = alignment.hsps[0]
        hit = i+1
        i = i+1
        queried_protein = xmlfile.split('.')[0]
        hit_protein = alignment.title.split('|')[1].split('.')[0]
        sequence = alignment.title
        length = alignment.length
        evalue = hsp.expect
        score = hsp.score
        gaps = hsp.gaps
        organism = sequence[sequence.find("[") + 1:sequence.find("]")]
        identities = hsp.identities
        pidentities = "%0.2f" % (100 * float(identities) / float(length))
        positives = hsp.positives
        ppositives = "%0.2f" % (100 * float(positives) / float(length))

        blast_records.append(
                dict(Hit=hit, DB=DB, Protein1=queried_protein, Protein2=hit_protein, Organism=organism, Length=length, Score=score, Identities=pidentities, Positives=ppositives, E=evalue))

    blast_dataframe = pd.DataFrame.from_records(blast_records)
    return blast_dataframe


if __name__ == "__main__":
    main_path = 'C:/Users/Kato Milis/PycharmProjects/similarity-networks/similaritynetworks'
    blast_path = main_path + '/Blast'
    fasta_path = main_path + '/fastaSequence'

    isexist = os.path.exists(blast_path + "/separated_sequences")
    if not isexist:
        # Create a new directory because it does not exist
        os.makedirs(blast_path + "/separated_sequences")
        print("The new directory is created!")

    split_fasta(fasta_path + "/Bacillariophyceae_reviewed.fasta")

    for file in os.listdir(blast_path + "/separated_sequences"):
        if file.endswith(".fasta"):
            if path.exists(f"{file}_blast.xml"):
                print(f"{file}_blast.txt already exists")
            else:
                blast_search(file)

    df = pd.DataFrame()
    for file in os.listdir(blast_path + "/separated_sequences"):
        if file.endswith(".fasta_blast.xml"):
            df = pd.concat([df, parse_blast(file)], axis=0)

    #second search
    proteins2 = df['Protein2']
    proteins2 = proteins2.drop_duplicates()
    print(proteins2)
    process = 0
    for file in os.listdir(blast_path + "/separated_sequences"):
        for protein in proteins2:
            print(protein)
            process = process +1
            print(process)
            if path.exists(f"{protein}.fasta_blast.xml"):
                print(f"{protein}.fasta_blast.txt already exists")
            elif path.exists(f"{protein}_blast.xml"):
                print(f"{protein}_blast.txt already exists")
            else:
                blast_search_ID(protein)

    #all in one dataframe
    #not yet efficient
    df = pd.DataFrame()
    for file in os.listdir(blast_path + "/separated_sequences"):
        if file.endswith(".xml"):
            df = pd.concat([df, parse_blast(file)], axis=0)

    df = df.drop_duplicates()

    # removing duplicate protein pairs
    duplicates = df.index[pd.DataFrame(np.sort(df[['Protein1', 'Protein2']].values)).duplicated()].to_list()
    print(len(duplicates), duplicates)
    df.drop(duplicates, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # removing similarities between protein pairs if either of the proteins are not in the first search
    print(proteins2)
    for index, row in df.iterrows():
        if not (row["Protein1"] in proteins2 and row["Protein2"] in proteins2):
            df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df)

    df.to_csv('blast.csv', index=False)
    shutil.move(blast_path + "/separated_sequences/blast.csv", blast_path + "/blast.csv")