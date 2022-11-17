import pandas as pd

from similaritynetworks.visualization import get_similarity_data


def getInfoForSingleProtein(UniprotID):
    df = pd.DataFrame(pd.read_csv("UniprotRetrival/uniprot.csv"))
    info = df[df['Entry'] == UniprotID]
    info = info[["Entry","Protein names"]]
    info = info.astype(str)
    return info

def getInfoForConnectedProteins(UniprotID,Algorithm,n_neighbors,targetOrganisms):
    info = get_similarity_data(UniprotID, n_neighbors, Algorithm)
    info = pd.DataFrame(info)
    return info

if __name__ == '__main__':
    print(getInfoForConnectedProteins("A0T0A2","kk",15,"dd"))