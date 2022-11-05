import os
from os import path
import urllib
import pandas as pd
import urllib.request as urllib2
import xml.etree.ElementTree as ET


main_path = os.getcwd()
def parseXML(file):
    tree = ET.parse(main_path + "/Hmmer/hmmer_xml_output1/"+file)
    root = tree.getroot()

    Protein1 = []
    Protein2 = []
    E = []
    Score = []
    Organism = []

    for node in root.iter('hits'):
        Protein2.append(node.attrib.get("acc2"))
        E.append(node.attrib.get("evalue"))
        Score.append(node.attrib.get("score"))
        Organism.append(node.attrib.get("species"))
    Protein1 = [file.split("_")[0]]* len(Protein2)
    hit = list(range(1,len(Protein1)+1))
    df = {'Hit':hit,'Protein1':Protein1,'Protein2':Protein2,'E':E,'Score':Score,'Organism':Organism}
    df = pd.DataFrame(df)
    return df


from multidimensional_urlencode import urlencode
try:
    from urllib.parse import unquote
except:
    from urllib import unquote
from Bio import SeqIO

# Parse the fasta file
def parse_fasta(filename):
    sequences=[i for i in SeqIO.parse(filename,'fasta')]
    return sequences

def hmmer_search(sequences, DB):
    class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
        # install a custom handler to prevent following of redirects automatically.
        def http_error_302(self, req, fp, code, msg, headers):
            return headers
    opener = urllib2.build_opener(SmartRedirectHandler())
    urllib2.install_opener(opener);

    # make a new directory to put the separated hmmer result
    isexist = os.path.exists(os.getcwd() + "/Hmmer/hmmer_xml_output1")
    if not isexist:
        # Create a new directory because it does not exist
        os.makedirs(os.getcwd() + "/Hmmer/hmmer_xml_output1")
        print("The new directory is created!")

    for sequence in sequences:
        parameters = {
            'seqdb': f'{DB}',
            'seq': '>Seq\n'+sequence.seq
        }
        data = urllib.parse.urlencode(parameters).encode("utf-8")

        # post the search request to the server
        req = urllib.request.Request('https://www.ebi.ac.uk/Tools/hmmer/search/phmmer', data)

        # get the url where the results can be fetched from
        results_url = urllib2.urlopen(req).get('location')

        # modify the range, format and presence of alignments in your results here
        res_params = {
            'output': 'xml',
            'range': '1,20'
        }

        # add the parameters to your request for the results
        enc_res_params = urlencode(res_params)
        modified_res_url = results_url + '?' + enc_res_params

        # send a GET request to the server
        results_request = urllib2.Request(modified_res_url)
        data = urllib2.urlopen(results_request)
        string = data.read().decode('utf-8')

        name =  sequence.name.split('|')

        # Write the output to a file
        with open(f"Hmmer/hmmer_xml_output1/{name[1]}_hmmer.xml", 'w') as save_file:
            save_file.write(string)
        print(f"The result for {name[1]} has been saved.")



#sequences = parse_fasta("/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/Hmmer/hmmer-second_search.fasta")
#hmmer_search(sequences, 'swissprot')
#main_path = os.getcwd()

def concatIntoCSV(folderName):
    deletion = 0
    df = pd.DataFrame()
    for file in os.listdir(main_path + "/Hmmer/" + folderName):
        if file.endswith(".xml"):
            if path.exists(f"{file}_hmmer.xml"):
                print(f"{file}_hmmer.txt already exists")
            else:
              df = pd.concat([df, parseXML(file)], axis=0)
    df["concat1"]  = df["Protein1"]+df["Protein2"]
    df["concat2"] = df["Protein2"] + df["Protein1"]
    df["Hit"] = range(len(df["concat2"] ))
    df.set_index([pd.Index(range(len(df["concat2"])))],inplace=True, drop=True)
    for index, row in df.iterrows():
        if row["concat2"] in set(df['concat1']):
            df = df.drop(index)
            deletion = deletion +1
            print(deletion)
    df.to_csv(main_path + "/Hmmer/" + folderName+"/outputTrimmed.csv",index=False)
    #12643
#sequences = parse_fasta("/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/Hmmer/hmmer-second_search.fasta")
#hmmer_search(sequences, 'swissprot')
#main_path = os.getcwd()
concatIntoCSV("hmmer_xml_output1")
#list = pd.unique(df["Protein2"])
#print(len(list))
#textfile = open("a_file.txt", "w")
#for element in list:
    #textfile.write(element + "\n")
#textfile.close()

# The second argument is the database you want to search against, can be pdb, uniprotkb, swissprot...