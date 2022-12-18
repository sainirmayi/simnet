import pandas as pd
import pymysql


def getInfoForSingleProtein(UniprotID):
    connection = pymysql.connect(user='root', password='proteinsim',db='protein_network',
                                host='localhost',
                                port=3306)

    cur = connection.cursor()
    sql = f"""SELECT Entry, Entry_Name, Primary_Gene_Name, Protein_names, Organism 
            FROM protein_network.protein WHERE Entry = '{UniprotID}'"""

    cur.execute(sql)
    dt = cur.fetchall()
    info = pd.DataFrame(dt, columns=['Protein ID', 'UniProt Entry', 'Gene Name', 'Protein Name', 'Organism'])

    cur.close()
    connection.close()
    return info


def getInfoForConnectedProteins(UniprotID,Algorithm,n_neighbors, Scope):
    connection = pymysql.connect(user='root', password='proteinsim', db='protein_network',
                                 host='localhost',
                                 port=3306)
    cur = connection.cursor()
    sql = f"""SELECT distinct P.Entry, P.Entry_Name, P.Protein_names, P.Organism,  S.Score
            FROM protein_network.protein P, protein_network.{Algorithm.lower()} S 
            WHERE (S.Protein1 = '{UniprotID}' or S.Protein2 = '{UniprotID}') and (P.Entry = S.Protein1 or P.Entry = S.Protein2) and (P.Entry != '{UniprotID}')
            ORDER BY S.Score DESC LIMIT {n_neighbors}"""
    cur.execute(sql)
    df = cur.fetchall()
    df = pd.DataFrame(df, columns=['Protein ID', 'UniProt Entry', 'Protein Name', 'Organism', 'Score'])

    #print(df)
    #diatoms = pd.read_csv(
     #   "/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/pages/diatom_proteins/diatoms.csv")

    #print(set(diatoms.iloc[:, 0]))
    #deletion = 0
    #for index, row in df.iterrows():
     #   if not (row['Protein ID'] in set(diatoms.iloc[:, 0])):
      #      #print(row['Protein ID'])
       #     df = df.drop(index)
        #    deletion = deletion +1
            #print(deletion)
    diatoms = ['Skeletonema costatum', 'Phaeodactylum tricornutum', 'Cylindrotheca fusiformis',
               'Cylindrotheca sp. (strain N1)', 'Nitzschia alba', 'Cyclotella meneghiniana', 'Thalassiosira pseudonana',
               'Pseudo-nitzschia multiseries', 'Detonula confervacea', 'Thalassiosira nordenskioeldii',
               'Thalassiosira oceanica', 'Phaeodactylum tricornutum (strain CCAP 1055/1)', 'Trieres chinensis',
               'Thalassiosira weissflogii']
    if Scope == 'Diatoms':
       d = df['Organism'].copy(deep=True)
       d = d.str.extract(r"([^(]*)")[0]
       d = d.str.strip()
       df = df[d.isin(diatoms)]




    # print(n_neighbors)
    info = pd.DataFrame(df, columns=['Protein ID', 'UniProt Entry', 'Protein Name', 'Organism', 'Score'])
    # print(info)
    cur.close()
    connection.close()
    return info


if __name__ == '__main__':
    # print(getInfoForSingleProtein("Q6B8P5"))
    print(getInfoForConnectedProteins("A0T097", "fasta", 20, 'all'))
    #diatoms = pd.read_csv("/Users/jiyue/PycharmProjects/similarity-networks/similaritynetworks/pages/diatom_proteins/diatoms.csv")

    #print(set(diatoms.iloc[:,0]))
