import os

import numpy as np
import pandas as pd
from Bio import SeqIO
import time
import requests
from xmltramp2 import xmltramp
import urllib
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import xml.etree.ElementTree as ET
import sys
sys.path.insert(0,r"C:\Users\Tutuy\PycharmProjects\similarity-networks\similaritynetworks\UniprotRetrieval")
import uniprot


def parse_fasta(filename):
    sequences = [i for i in SeqIO.parse(filename, 'fasta')]
    return sequences

# Wrapper for a REST (HTTP GET) request
def rest_request(url):
    try:
        req = Request(url)
        reqH = urlopen(req)
        resp = reqH.read()
        contenttype = reqH.info()
        if (len(resp) > 0 and contenttype != "image/png;charset=UTF-8"
                and contenttype != "image/jpeg;charset=UTF-8"
                and contenttype != "application/gzip;charset=UTF-8"):
            try:
                result = resp.decode('utf-8')
            except UnicodeDecodeError:
                result = resp
        else:
            result = resp
        reqH.close()
    # Errors are indicated by HTTP status codes.
    except HTTPError as ex:
        result = requests.get(baseUrl).content
    return result


def submit_job(parameters, baseUrl):
    requestUrl = baseUrl + '/run/'
    try:
        req = Request(requestUrl)
        # Make the submission (HTTP POST).
        reqH = urlopen(req, urllib.parse.urlencode(parameters).encode("utf-8"))
        jobId = reqH.read().decode('utf-8')
        reqH.close()
    except HTTPError as ex:
        print(xmltramp.parse(ex.read().decode('utf-8'))[0][0])
        quit()
    return jobId


# Get job status
def get_status(jobId):
    requestUrl = baseUrl + '/status/' + jobId
    status = rest_request(requestUrl)
    return status


def client_poll(jobId):
    result = 'PENDING'
    while result == 'RUNNING' or result == 'PENDING':
        result = get_status(jobId)
        if result == 'RUNNING' or result == 'PENDING':
            time.sleep(5)


# Get available result types for job
def get_result_types(jobId):
    requestUrl = baseUrl + '/resulttypes/' + jobId
    xmlDoc = rest_request(requestUrl)
    doc = xmltramp.parse(xmlDoc)
    return doc['type':]


def get_result(jobId, outformat, outfile):
    # Check status and wait if necessary
    client_poll(jobId)
    # Get available result types
    resultTypes = get_result_types(jobId)
    # Derive the filename for the result
    filename = f"{outfile}.{outformat}"
    # Write a result file
    # Get the result
    requestUrl = baseUrl + '/result/' + jobId + '/' + outformat
    result = rest_request(requestUrl)
    fh = open(filename, 'w')
    fh.write(result)
    fh.close()


def similarity_search(sequence, program, stype, alignments, db, outformat, baseUrl, email, outfile):
    parameters = {
        'program': program,
        'stype': stype,
        'alignments': alignments,
        'sequence': sequence,
        'database': db,
        'email': email
    }
    if os.path.exists(f"{os.getcwd()}/{outfile}.{outformat}"):
        print(f"{outfile}.{outformat} already exists!")
    else:
        jobId = submit_job(parameters, baseUrl)
        print(f"Job: {jobId}")
        print(f"Getting results of {sequence.splitlines()[0]}")
        get_result(jobId, outformat, outfile)


def parse_xml_files(folder):
    df = pd.DataFrame()
    for file in os.listdir(folder):
        tree = ET.parse(f"{folder}/{file}")
        root = tree.getroot()
        records = []
        ns = {'name': 'http://www.ebi.ac.uk/schema'}
        for item in root.findall("name:SequenceSimilaritySearchResult/name:hits/name:hit", ns):
            protein1 = file.split('.')[0]
            protein2 = item.attrib.get('ac')
            db = item.attrib.get('database')
            organism = item.attrib.get('description').split('OS=')[1].split('OX=')[0]
            length = item.attrib.get('length')
            score = item.find('name:alignments/name:alignment/name:score', ns).text
            identity = item.find('name:alignments/name:alignment/name:identity', ns).text
            positives = item.find('name:alignments/name:alignment/name:positives', ns).text
            e = item.find('name:alignments/name:alignment/name:expectation', ns).text
            match_seq = item.find('name:alignments/name:alignment/name:matchSeq', ns).text
            records.append(
                dict(Protein1=protein1, Protein2=protein2, DB=db, Organism=organism, Length=length, Score=score,
                     Identities=identity, Positives=positives, E=e, MatchSequence=match_seq))
        df = pd.concat([df, pd.DataFrame.from_records(records)], axis=0)
    return df


def retrieve_protein_info(similarity_search_results):
    # Retrieving protein information from uniprot
    uniprot_df = pd.read_csv("../UniprotRetrieval/updated_uniprot.csv")
    proteins = pd.concat([similarity_search_results['Protein1'], similarity_search_results['Protein2']], axis=0).drop_duplicates()
    protein_info = pd.DataFrame()
    for protein in proteins:
        if protein not in uniprot_df:
            protein_info = pd.concat([protein_info, uniprot.uniprot_retrieval(protein)], axis=0)
    pd.concat([uniprot_df, protein_info], axis=0).drop_duplicates().to_csv('../UniprotRetrieval/updated_uniprot.csv')


if __name__ == '__main__':
    baseUrl = 'https://www.ebi.ac.uk/Tools/services/rest/fasta'
    sequences = parse_fasta('../fastaSequence/Bacillariophyceae_reviewed.fasta')
    program = 'fasta'
    # program = 'ssearch'
    stype = 'protein'
    alignments = 20
    database = 'uniprotkb_swissprot'
    outformat = 'xml'
    email = 'ynirmayi@gmail.com'

    # make a new directory for the first search results
    if not os.path.exists(f"{os.getcwd()}/{program}_xml_out/"):
        # Create a new directory because it does not exist
        os.makedirs(f"{os.getcwd()}/{program}_xml_out/")
        print("The new directory is created!")

    # first similarity search
    for record in sequences:
        sequence = f">{record.id}\n{record.seq}"
        similarity_search(sequence, program, stype, alignments, database, outformat, baseUrl, email, f"{program}_xml_out/{sequence.split('|')[1]}")

    # Parsing search results in xml folder
    first_search_results = parse_xml_files(f"{os.getcwd()}/{program}_xml_out/")
    print(first_search_results)
    print("start retrieval")
    # updating uniprot protein information file
    # retrieve_protein_info(first_search_results)

    print("information retrieved")
    # make a new directory for the search results
    if not os.path.exists(f"{os.getcwd()}/{program}_second_search_xml_out/"):
        # Create a new directory because it does not exist
        os.makedirs(f"{os.getcwd()}/{program}_second_search_xml_out/")
        print("The new directory is created!")

    # Finding similarities between hits for each queried protein
    for query in first_search_results['Protein1'].unique():
        hits = first_search_results[first_search_results['Protein1'] == query]
        for index, hit in hits.iterrows():
            if hit['Protein2'] != query and hit['Protein2'] not in hits['Protein1'].unique():
                seq = f">{hit['Protein2']}\n{hit['MatchSequence'].replace('-', '')}"
                similarity_search(seq, program, stype, alignments, database, outformat, baseUrl, email, f"{program}_second_search_xml_out/{hit['Protein2']}")

    second_search_results = parse_xml_files(f"{os.getcwd()}/{program}_second_search_xml_out/")
    print(second_search_results)

    final_df = pd.concat([second_search_results, first_search_results], axis=0).drop_duplicates().drop(columns='MatchSequence')
    final_df.reset_index(drop=True, inplace=True)
    print(len(final_df))
    # removing duplicate protein pairs
    duplicates = final_df.index[pd.DataFrame(np.sort(final_df[['Protein1', 'Protein2']].values)).duplicated()].to_list()
    print(len(duplicates),duplicates)
    final_df.drop(duplicates, axis=0, inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    # removing similarities between protein pairs if either of the proteins are not in the first search
    proteins_list = first_search_results['Protein2'].unique()
    print(proteins_list)
    for index, row in final_df.iterrows():
        if not(row["Protein1"] in proteins_list and row["Protein2"] in proteins_list):
            final_df.drop(index, inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    print(final_df)

    final_df.to_csv(f"{program}.csv", index=False)
