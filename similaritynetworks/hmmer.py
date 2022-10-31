import os
import urllib
import urllib.request as urllib2
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
    isexist = os.path.exists(os.getcwd() + "/hmmer_xml_output")
    if not isexist:
        # Create a new directory because it does not exist
        os.makedirs(os.getcwd() + "/hmmer_xml_output")
        print("The new directory is created!")
    if isexist:
        print("The folder already exist!")

    for sequence in sequences:

        name =  sequence.name.split('|')
        isexist = os.path.exists(os.getcwd() + f"/hmmer_xml_output/{name[1]}_hmmer.xml")
        if isexist:
            print(f"{name[1]}_exist")
        if not isexist:
            print(f"{name[1]}_notexist")
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

            # Write the output to a file
            with open(f"hmmer_xml_output/{name[1]}_hmmer.xml", 'w') as save_file:
                save_file.write(string)
            print(f"The result for {name[1]} has been saved.")

def parse_xml():
    # to be added...
    return 0

sequences = parse_fasta("Bacillariophyceae_reviewed.fasta")
hmmer_search(sequences, 'uniprotkb')
# The second argument is the database you want to search against, can be pdb, uniprotkb, swissprot...