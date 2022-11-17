import pandas as pd
import pymysql

from similaritynetworks.visualization import get_similarity_data


def getInfoForSingleProtein(UniprotID):
    connection = pymysql.connect(user='root', password='proteinsim',db='newschema',
                                host='localhost',
                                port=3306)

    cur = connection.cursor()
    sql = f"select Entry, Protein2, Score from newschema.protein where Entry = '{UniprotID}'"

    cur.execute(sql)
    dt = cur.fetchall()
    info = pd.DataFrame(dt, columns=['Protein1', 'Protein2', 'Score'])
                                 # results2.reset_index(drop=True, inplace=True)
    #df = pd.DataFrame(pd.read_csv("../../UniprotRetrival/uniprot.csv"))
    #info = df[df['Entry'] == UniprotID]
    #info = info[["Entry","Protein names"]]
    #info = info.astype(str)
    return info

def getInfoForConnectedProteins(UniprotID,Algorithm,n_neighbors,targetOrganisms):
    info = get_similarity_data(UniprotID, n_neighbors, Algorithm)
    info = pd.DataFrame(info)
    return info

if __name__ == '__main__':
    print(getInfoForConnectedProteins("A0T0A2","kk",15,"dd"))