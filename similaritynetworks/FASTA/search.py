import os

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


def clientPoll(jobId):
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
    clientPoll(jobId)
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


def similarity_search(sequences, program, stype, alignments, db, outformat, baseUrl, email):
    for sequence in sequences:
        parameters = {
            'program': program,
            'stype': stype,
            'alignments': alignments,
            'sequence': f'>{sequence.id}\n{sequence.seq}',
            'database': db,
            'email': email
        }
        outfile = f"{program}_xml_out/{sequence.name.split('|')[1]}"
        if os.path.exists(f"{os.getcwd()}/{outfile}.{outformat}"):
            print(f"{outfile}.{outformat} already exists!")
        else:
            jobId = submit_job(parameters, baseUrl)
            print(f"Job: {jobId}")
            print(f"Getting results of {sequence.name.split('|')[1]}")
            get_result(jobId, outformat, outfile)


def parse_xml_files(program):
    df = pd.DataFrame()
    for file in os.listdir(f"{os.getcwd()}/{program}_xml_out/"):
        tree = ET.parse(f"{os.getcwd()}/{program}_xml_out/{file}")
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
            records.append(
                dict(Protein1=protein1, Protein2=protein2, DB=db, Organism=organism, Length=length, Score=score,
                     Identities=identity, Positives=positives, E=e))
        df = pd.concat([df, pd.DataFrame.from_records(records)], axis=0)
    df.to_csv(f'{program}.csv', index=False)


if __name__ == '__main__':
    baseUrl = 'https://www.ebi.ac.uk/Tools/services/rest/fasta'
    sequences = parse_fasta('../fastaSequence/Bacillariophyceae_reviewed.fasta')
    # program = 'fasta'
    program = 'ssearch'
    stype = 'protein'
    alignments = 20
    database = 'uniprotkb_swissprot'
    outformat = 'xml'
    email = 'ynirmayi@gmail.com'
    # make a new directory to put the separated hmmer result
    if not os.path.exists(f"{os.getcwd()}/{program}_xml_out/"):
        # Create a new directory because it does not exist
        os.makedirs(f"{os.getcwd()}/{program}_xml_out/")
        print("The new directory is created!")
    similarity_search(sequences, program, stype, alignments, database, outformat, baseUrl, email)
    parse_xml_files(program)
