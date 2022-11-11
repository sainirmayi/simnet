import os

import plotly.graph_objects as go
import networkx as nx
import pandas as pd
pd.options.mode.chained_assignment = None
import pymysql
import plotly.express as px

# def create_sample_db():
#     """ Sample dataframes to represent the databases """
#     main_dataframe = pd.DataFrame(pd.read_csv("sample_data.csv"))
#     protein_info = main_dataframe.drop(['Hit', 'Score(Bits)', 'Identities(%)', 'Positives(%)', 'E()'],
#                                        axis=1).drop_duplicates()
#     protein_info.reset_index(drop=True, inplace=True)
#     similarity_db = main_dataframe.drop(['DB', 'Description', 'Organism', 'Length'], axis=1)
#     similarity_db.reset_index(drop=True, inplace=True)
#     similarity_db['Protein1'] = None
#     for i in range(similarity_db.shape[0]):
#         if similarity_db["Hit"][i] == 1:
#             qp = similarity_db.loc[i, 'Accession']
#         similarity_db['Protein1'][i] = qp
#     similarity_db.rename(columns={'Accession': 'Protein2', 'Score(Bits)': 'Score',
#                                   'Identities(%)': 'Identities', 'Positives(%)': 'Positives', 'E()': 'E'},
#                          inplace=True)
#     similarity_db.reset_index(drop=True, inplace=True)
#     return similarity_db


def getProteinID(sequence):
    #-----------------------------------------------------------------------
    """Database"""
    # connection = pymysql.connect(user='root', password='123456',
    #                              host='localhost',
    #                              port=3306)
    # sequence = "".join(line.strip() for line in sequence.splitlines())
    # cur = connection.cursor()
    # sql = f"select ID from protein_network.protein where Sequence = '{sequence}'"
    #
    # cur.execute(sql)
    # query = cur.fetchall()
    #
    # cur.close()
    # # close the connection
    # connection.close()
    #------------------------------------------------------------------------

    #------------------------------------------------------------------------
    """csv file"""
    uniprot_df = pd.DataFrame(pd.read_csv("UniprotRetrival/uniprot.csv"))
    sequence = "".join(line.strip() for line in sequence.splitlines())
    df = uniprot_df.loc[uniprot_df['Sequence'] == sequence]

    #print(df)
    query = df['Entry'].to_string(index=False)
    #print(query)
    #---------------------------------------------------------------------------
    # return query[0][0] for database option
    return query


def get_similarity_data(query,n_neighbors, DB):
    """ Creating dataframe of similar proteins.
     To be replaced with a function to query the database
     and maybe obtain a result dataframe with the 20 most similar proteins. """
    similarity_db = pd.DataFrame(pd.read_csv(os.getcwd() +"/HmmerWithSecondSearch.csv"))
    similarity_db = similarity_db.drop(['Hit', 'Organism',  'E'], axis=1)
    results = pd.DataFrame()
    queryInfo = similarity_db[(similarity_db['Protein1'] == query) ]
                              #| (similarity_db['Protein2'] == query)]
    queryInfo.sort_values(by= 'Score', ascending=False, inplace=True)
    queryInfo.reset_index(drop=True, inplace=True)
    #print(queryInfo)
    #similar = list(similarity_db['Protein2'][similarity_db['Protein1'] == query])
   # similar.remove(query)
    topN = queryInfo[:n_neighbors]
    direct_connection = pd.concat([topN['Protein1'][topN['Protein2'] ==
                            query],topN['Protein2'][topN['Protein1'] == query]])

    direct_connection = direct_connection.tolist()
    #print(direct_connection)
    for index, row in similarity_db.iterrows():
        if row["Protein1"] in direct_connection and row['Protein2'] in direct_connection :
            results = results.append(row)
    results = pd.concat([results, topN], axis=0)
    #print(topN)

    #for i in range(results.shape[0]):
     #   if results['Protein1'][i] != query:
      #      if results['Protein1'][i] not in data or \
       #              (results['Protein1'][i] in data and results['Protein2'][i] not in data):
        #              results.drop(labels=i, inplace=True, axis=0)
         #   else:
          #      if results["Protein1"][i] == results["Protein2"][i] or results['Protein2'][i] not in data:
           #      results.drop(labels=i, inplace=True, axis=0)

    results.reset_index(drop=True, inplace=True)

    #print(results)
    return results
    #------------------------------------------------------------------------------------------------------------------

    #"""Use the following code if you can connect to the database"""
    # Retrieve information from database.
    #connection = pymysql.connect(user='root', password='123456',
                                 #host='localhost',
                                 #port=3306)
    #cur = connection.cursor()
    #if DB == 'Blast':
    #    sql = f"select Protein1, Protein2, Score from protein_network.blast where Protein1 = '{query}' and Protein2 != '{query}' order by Score desc LIMIT {n_neighbors}"
    #elif DB == 'Fasta':
    #    sql = f"select Protein1, Protein2, Score from protein_network.fasta where Protein1 = '{query}' and Protein2 != '{query}' order by Score desc LIMIT {n_neighbors}"
    #else:
        #a default sql query
    #    sql = f"select Protein1, Protein2, Score from protein_network.blast where Protein1 = '{query}' and Protein2 != '{query}' order by Score desc LIMIT {n_neighbors}"


    #cur.execute(sql)
    #dt = cur.fetchall()
    #results2 = pd.DataFrame(dt, columns=['Protein1', 'Protein2', 'Score'])

    #cur.close()
    # close the connection
    #connection.close()
    #------------------------------------------------------------------------------------------------------------------

    # 'return results2' if you want to retrieve data from the database.
    return results2


def create_network(similar_proteins):
    """ Creating network diagram """
    # load pandas df as networkx graph
    graph = nx.from_pandas_edgelist(similar_proteins, 'Protein1', 'Protein2', edge_attr='Score')

    # Deciding on the layout of how the nodes will be lined up
    pos = nx.spring_layout(graph, k=0.5, iterations=50, weight='Score')
    for n, p in pos.items():
        graph.nodes[n]['pos'] = p
    # Create edges
    edge_x = []
    edge_y = []
    xtext = []
    ytext = []
    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['pos']
        x1, y1 = graph.nodes[edge[1]]['pos']
        xtext.append((x0 + x1) / 2)
        ytext.append((y0 + y1) / 2)
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(
            #showscale=True,
            #colorscale='YlGnBu',
            #reversescale=True,
            #color=[],
            width=1)
    )

    edge_hovertemplate = []
    edge_colors = []

    for edge in graph.edges():
        protein1 = edge[0]
        protein2 = edge[1]
        df = similar_proteins[((similar_proteins['Protein1'] == protein1) & (similar_proteins['Protein2']== protein2))
                               | ((similar_proteins['Protein2'] == protein1) & (similar_proteins['Protein1'] == protein2))]



        score = df['Score'].to_string(index=False)
        print(score)
        edge_colors.append(score)
        edge_hovertemplate.append(f'Score: {score} <extra></extra>')

    #print(edge_colors)
    #edge_trace.line.color = edge_colors

    eweights_trace = go.Scatter(x=xtext, y=ytext, mode='text',
                                marker_size=0.5,
                                textposition='top center')
    eweights_trace.hovertemplate = edge_hovertemplate

    #Nodes:
    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    uniprot_df = pd.DataFrame(pd.read_csv("UniprotRetrival/uniprot.csv"))

    # Try hovertemplate instead of hoverinfo to display more information
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition='middle right',
        textfont=dict(size=10, color='black'),
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=30,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    #Colour node points by number of connections + text to node + text when you hover
    node_adjacency = []
    node_text = []
    node_hovertemplate = []

    for node, adjacencies in enumerate(graph.adjacency()):
        node_adjacency.append(len(adjacencies[1]))
        node_text.append(adjacencies[0])
        entry = adjacencies[0]
        df = uniprot_df.loc[uniprot_df['Entry'] == entry]
        entry_name = df['Entry Name'].to_string(index=False)
        gene_names = df['Gene Names'].to_string(index=False)
        sequence = df['Sequence'].to_string(index=False)
        organism = df['Organism'].to_string(index=False)

        organism_id = df['Organism (ID)'].to_string(index=False)
        protein_names = df['Protein names'].to_string(index=False)

        node_hovertemplate.append(f'Entry: {entry}'
                                  + f'<br>Entry name: {entry_name}'
                                  + f'<br>Gene names: {gene_names}'
                                  + f'<br>Sequence: {sequence}'
                                  + f'<br>Organism: {organism}'
                                  + f'<br>Organism id: {organism_id}'
                                  + f'<br>Protein names: {protein_names}'
                                  + '<extra></extra>')

    #-------------------------------------------------------------------------
    """Database option"""
    #
    #connection = pymysql.connect(user='root', password='123456',
    #                             host='localhost',
    #                             port=3306)
    #cur = connection.cursor()
    #for node, adjacencies in enumerate(graph.adjacency()):
    #    node_adjacency.append(len(adjacencies[1]))
    #    node_text.append(adjacencies[0])
    #    entry = adjacencies[0]
    #    sql = f"select Entry Name, Gene Names, Sequence, Organism, Organism (ID), Protein Names from protein_network.protein where ID = '{entry}'"
    #    cur.execute(sql)
    #    data = cur.fetchall()
    #    entry_name = data[0][0]
    #    gene_names = data[0][1]
    #    sequence = data[0][2]
    #    organism = data[0][3]
    #    organism_id = data[0][4]
    #    protein_names = data[0][5]
    #    node_hovertemplate.append(f'Entry: {entry}'
    #                              + f'<br>Entry name: {entry_name}'
    #                              + f'<br>Gene names: {gene_names}'
    #                              + f'<br>Sequence: {sequence}'
    #                              + f'<br>Organism: {organism}'
    #                              + f'<br>Organism id: {organism_id}'
    #                              + f'<br>Protein names: {protein_names}')
    #cur.close()
     # close the connection
    #connection.close()
    #-------------------------------------------------------------------------

    node_trace.marker.color = node_adjacency
    node_trace.text = node_text
    node_trace.hovertemplate = node_hovertemplate

    # Create Network Graph
    fig = go.Figure(data=[edge_trace, node_trace, eweights_trace],
                    layout=go.Layout(
                        title='<br>Protein similarity network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="Protein similarities",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig


def get_visualization(query,n_neighbors,DB):
    """ Call this function to get the similarity network for a query """
    similar_proteins = get_similarity_data(query,n_neighbors,DB)

    return create_network(similar_proteins)


if __name__ == "__main__":

    get_visualization("A0T0A3", 5, "Blast").show()
