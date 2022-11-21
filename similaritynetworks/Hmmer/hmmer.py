import os
from os import path
import urllib
import pandas as pd
import urllib.request as urllib2
import xml.etree.ElementTree as ET

'''For who wants to do second search:
 1.first search, get parsed results df1(as csv), and get unique list of 2 protein columns(name list_scope) (do yourselves)
 2.second search , feed the folder with xml output into function parsingAndConcatIntoDf(folderName), get df2
 3.feed the df1 and df2 to dataTrimming(df1,df2), get df
 4.feed list_scope and df to dropOutOfScopeProtein(list,df)(!Dont forget to write to csv in main)
 Note:paths defintely needs to be modified...'''
main_path = os.getcwd()
def parseXML(file,folder):
    '''(DEPRECATED)'''
    tree = ET.parse(main_path + "/Hmmer/" + folder+'/'+file)
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

def parsingAndConcatIntoDf(folderName):
    '''parse a list of xml files in a folder and concatate them into df'''
    df = pd.DataFrame()
    for file in os.listdir(main_path +"/" + folderName):
        if file.endswith(".xml"):
            tree = ET.parse(main_path +"/" + folderName+"/" + file)
            root = tree.getroot()
            Protein2 = []
            E = []
            Score = []
            Organism = []

            for node in root.iter('hits'):
                Protein2.append(node.attrib.get("acc2"))
                E.append(node.attrib.get("evalue"))
                Score.append(node.attrib.get("score"))
                Organism.append(node.attrib.get("species"))
            Protein1 = [file.split("_")[0]] * len(Protein2)
            hit = list(range(1, len(Protein1) + 1))
            df_tmp = {'Hit': hit, 'Protein1': Protein1,
                      'Protein2': Protein2, 'E': E, 'Score': Score,
                      'Organism': Organism}
            df_tmp = pd.DataFrame(df_tmp)
            df = pd.concat(([df, df_tmp]), axis=0)
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
    '''Searching script'''
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

def concatIntoCSV(folderName):
    '''(DEPRECATED)parse a list of xml files in a folder and concatate them into df'''
    df = pd.DataFrame()
    for file in os.listdir(main_path + "/Hmmer/" + folderName):
        if file.endswith(".xml"):
            if path.exists(f"{file}_hmmer.xml"):
                print(f"{file}_hmmer.txt already exists")
            else:
              df = pd.concat([df, parseXML(file,folderName)], axis=0)
    return df

def dataTrimming(df1,df2):
    '''concanate two df(1st search and 2nd search) and trim repeated protein pairs'''
    deletion = 0
    df = pd.concat([df1, df2], axis=0)
    df["concat1"]  = df["Protein1"] + df["Protein2"]
    df["concat2"] = df["Protein2"] + df["Protein1"]
    df["Hit"] = range(len(df["concat2"] ))
    df.set_index([pd.Index(range(len(df["concat2"])))],inplace=True, drop=True)
    for index, row in df.iterrows():
        if row["concat2"] in set(df['concat1']):
            df = df.drop(index)
            deletion = deletion +1
            print(deletion)
    df = df.drop_duplicates(subset=['concat1'])#remove identical rows
    df = pd.DataFrame(df)
    return df
    #12643
    #547
#sequences = parse_fasta("/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/diatom_proteins/Bacillariophyceae_reviewed.fasta")
#hmmer_search(sequences, 'swissprot')
#main_path = os.getcwd()

def dropOutOfScopeProtein(list,df):
    '''Drop protein pairs in (df) that are not entirely within (list) user provide
    (list of protein of first search results needs to be provided!)'''
    deletion = 0
    for index, row in df.iterrows():
        if not(row["Protein1"] in list and row["Protein2"] in list):
            df = df.drop(index)
            deletion = deletion +1
            print(deletion)
    return df


#d = {'Protein1': ["1", "2","1","3","5"], 'Protein2': ["2", "1","2","4","6"]}
#df1 = pd.read_csv('/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/Hmmer/testnew.csv')
#df1 = pd.DataFrame(data=d)
#df2 = pd.DataFrame()
#df = dataTrimming(df1,df2)
#print(df)
#df.to_csv(main_path + "/prey",index=False)
#hit = list(range(1,len(df["Protein1"])+1))
#df["Hit"] = hit
#df.reset_index(drop=True, inplace=True)
#print(df)
#df = df.drop(['concat1', 'concat2'], axis=1)
#df = df.drop_duplicates(subset=['concat1'])
#df.to_csv(main_path + "/HmmerWithSecondSearch.csv",index=False)
#my_file = open("/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/Hmmer/a_file.txt", "r")
#data = my_file.read()
#newdf = dropOutOfScopeProtein(data,df)
#print(newdf)
#newdf.to_csv(main_path + "/newoutputTrimmed.csv",index=False)
#df1 = concatIntoCSV("hmmer_xml_output1")
#dataTrimming(df1,df2)
#df2 = concatIntoCSV("hmmer_xml_output2")
#df3=concatIntoCSVnew("hmmer_xml_output2")
#df3.to_csv(main_path + "/testnew.csv",index=False)
#list = pd.unique(df["Protein2"])
#print(len(list))
#textfile = open("a_file.txt", "w")
#for element in list:
    #textfile.write(element + "\n")
#textfile.close()

# The second argument is the database you want to search against, can be pdb, uniprotkb, swissprot...