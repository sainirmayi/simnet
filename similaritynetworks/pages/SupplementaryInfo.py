import pandas as pd
import pymysql


def getInfoForSingleProtein(UniprotID):
    connection = pymysql.connect(user='root', password='proteinsim',db='protein_network',
                                host='localhost',
                                port=3306)

    cur = connection.cursor()
    sql = f"select Entry, Protein_names from protein_network.protein where Entry = '{UniprotID}'"

    cur.execute(sql)
    dt = cur.fetchall()
    info = pd.DataFrame(dt, columns=['Entry', 'Protein_names'])
    cur.close()
    connection.close()
    return info


def getInfoForConnectedProteins(UniprotID,Algorithm,n_neighbors,targetOrganisms):
    data = pd.DataFrame()
    connection = pymysql.connect(user='root', password='proteinsim', db='protein_network',
                                 host='localhost',
                                 port=3306)
    cur = connection.cursor()
    sql = f"select Protein1, Protein2, Score from protein_network.hmmer where Protein1 = '{UniprotID}' OR Protein1 = '{UniprotID}'" \
          f"order by Score desc LIMIT {n_neighbors}"
    cur.execute(sql)
    dt = cur.fetchall()
    info = pd.DataFrame(dt, columns=['Protein1', 'Protein2','Score'])
    for index, row in info.iterrows():
        # info.loc[info.index[index], 'Links'] = '[Google]' + f"https://www.uniprot.org/uniprotkb/{UniprotID}/entry"
        if row['Protein1'] == UniprotID:
            info.loc[info.index[index], 'Protein1']  = row['Protein2']
    # info = info.drop(info['Protein2'])
    info['Protein2'] = info['Protein1']
    plist = info['Protein1'].unique().tolist()
    for i in plist:
        data_tmp = getInfoForSingleProtein(i)
        data = pd.concat([data_tmp,data])

    data = data.reindex()
    info = pd.concat([info.set_index('Protein2'),data.set_index('Entry')],axis = 1, join='inner')
    cur.close()
    connection.close()
    return info

if __name__ == '__main__':
    # print(getInfoForSingleProtein("Q6B8P5"))
    print(getInfoForConnectedProteins("A0T0A2","kk",15,"dd"))