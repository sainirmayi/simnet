import os
from os import path
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
import pandas as pd


def split_fasta(fname):
    # make a new directory to put the separated fasta sequences
    isexist = os.path.exists(os.getcwd() + "/separated_sequences")
    if not isexist:
        # Create a new directory because it does not exist
        os.makedirs(os.getcwd() + "/separated_sequences")
        print("The new directory is created!")

    f = open(fname, "r")
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


def blast_search(directory):
    for file in os.listdir(directory):
        if file.endswith(".fasta"):
            if path.exists(f"{file}_blast.xml"):
                print(f"{file}_blast.txt already exists")
            else:
                sequence_data = open(file).read()
                result_handle = NCBIWWW.qblast("blastp", "swissprot", sequence_data, format_type="XML", hitlist_size=20)
                with open(f"{file}_blast.xml", 'w') as save_file:
                    blast_results = result_handle.read()
                    save_file.write(blast_results)


def parse_blast(directory):
    blast_records = []

    for file in os.listdir(directory):
        if file.endswith(".xml"):
            result = open(file, "r")
            records = NCBIXML.parse(result)
            item = next(records)

            for alignment in item.alignments:
                for hsp in alignment.hsps:
                    protein = file.split('.')[0]
                    sequence = alignment.title
                    length = alignment.length
                    evalue = hsp.expect
                    score = hsp.score
                    gaps = hsp.gaps

                    blast_records.append(
                        dict(protein=protein, sequence=sequence, length=length, evalue=evalue, score=score, gaps=gaps))

    blast_dataframe = pd.DataFrame.from_records(blast_records)
    blast_dataframe.to_csv('blast.csv')


split_fasta(sequences.fasta)
blast_search(os.getcwd())
parse_blast(os.getcwd())
