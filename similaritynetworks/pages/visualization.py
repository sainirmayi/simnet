import os
import textwrap

import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import pymysql

pd.options.mode.chained_assignment = None


def getID_from_db(sequence):
    connection = database_connection()
    cur = connection.cursor()
    sql = f"SELECT Entry FROM protein_network.protein where Sequence = %s"
    cur.execute(sql, sequence)
    query = cur.fetchall()
    cur.close()
    connection.close()
    return query[0][0]


def getID_from_csv(sequence):
    uniprot_df = pd.DataFrame(pd.read_csv("../UniprotRetrieval/uniprot.csv"))
    df = uniprot_df.loc[uniprot_df['Sequence'] == sequence]
    query = df['Entry'].to_string(index=False)
    return query


def getProteinID(sequence):
    sequence = "".join(line.strip() for line in sequence.splitlines())
    return getID_from_db(sequence)
    # return getID_from_csv(sequence)


def database_connection():
    connection = pymysql.connect(user='root', password='proteinsim', host='localhost', port=3306)
    return connection


def similarity_data_from_csv(query, n_neighbors, algorithm):
    if algorithm == 'blast':
        df = pd.read_csv("../Blast/blast.csv")
    elif algorithm == 'fasta':
        df = pd.read_csv("../FASTA/fasta.csv")
    elif algorithm == 'ssearch':
        df = pd.read_csv("../FASTA/ssearch.csv")
    elif algorithm == 'hmmer':
        df = pd.read_csv("../HmmerWithSecondSearch.csv")
    else:
        df = pd.DataFrame()
    hits = pd.concat([df[df['Protein1'] == query], df[df['Protein2'] == query]], axis=0, ignore_index=True)
    hits.drop(hits[hits['Protein1'] == hits['Protein2']].index, inplace=True)
    hits.sort_values(by='Score', ascending=False, inplace=True)
    hits.reset_index(drop=True, inplace=True)
    results = hits[:n_neighbors]
    prot_list = list(pd.concat([results['Protein1'], results['Protein2']]).unique())
    prot_list.remove(query)
    for index, row in df.iterrows():
        if row['Protein1'] in prot_list and row['Protein2'] in prot_list:
            results = pd.concat([results, row.to_frame().T])
    results.drop_duplicates(inplace=True, ignore_index=True)
    return results


def similarity_data_from_db(query, n_neighbors, algorithm, cur):
    sql = """SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` 
        WHERE `TABLE_SCHEMA` = 'protein_network' AND `TABLE_NAME` = %s"""
    cur.execute(sql, (algorithm,))
    columns = [item[0] for item in cur.fetchall()]
    sql = f"""SELECT * FROM protein_network.{algorithm} WHERE (Protein1 = %s OR Protein2 = %s) AND Protein1 != Protein2 
        ORDER BY Score desc LIMIT %s"""
    cur.execute(sql, (query, query, n_neighbors))
    results = pd.DataFrame(cur.fetchall(), columns=columns)
    prot_list = list(pd.concat([results['Protein1'], results['Protein2']]).unique())
    print(prot_list)
    prot_list.remove(query)
    sql = f"""SELECT * FROM protein_network.{algorithm} 
        WHERE Protein1 in %s and Protein2 in %s"""
    cur.execute(sql, (tuple(prot_list), tuple(prot_list)))
    results = pd.concat([results, pd.DataFrame(cur.fetchall(), columns=columns)], axis=0)
    results.drop_duplicates(inplace=True, ignore_index=True)
    return results


def get_similarity_data(query, n_neighbors, algorithm, cur):
    # return similarity_data_from_csv(query, n_neighbors, algorithm)
    return similarity_data_from_db(query, n_neighbors, algorithm, cur)


def info_from_csv(similar_proteins):
    protein_list = list(pd.concat([similar_proteins['Protein1'], similar_proteins['Protein2']]).unique())
    df = pd.read_csv("UniprotRetrieval/uniprot.csv")
    df.rename(columns={'Entry Name':'Entry_Name', 'Gene Names (primary)':'Primary_Gene_Name', 'Gene Names':'Gene_Names',
                       'Organism (ID)':'OrganismID', 'Protein names':'Protein_names', 'Protein families':'Protein_families',
                       'Function [CC]':'Function', 'EC number':'EC_number', 'pH dependence':'pH_dependence',
                       'Temperature dependence':'Temperature_dependence'}, inplace=True)
    results = pd.DataFrame()
    for protein in protein_list:
        results = pd.concat([results, df[df['Entry'] == protein]], axis=0, ignore_index=True)
    results = results.fillna('')
    return results


def info_from_db(similar_proteins, cur):
    protein_list = list(pd.concat([similar_proteins['Protein1'], similar_proteins['Protein2']]).unique())
    sql = """SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` 
            WHERE `TABLE_SCHEMA` = 'protein_network' AND `TABLE_NAME` = 'protein'"""
    cur.execute(sql)
    columns = [item[0] for item in cur.fetchall()]
    results = pd.DataFrame()
    for protein in protein_list:
        sql = f"""SELECT * FROM protein_network.protein WHERE Entry = %s"""
        cur.execute(sql, (protein))
        results = pd.concat([results, pd.DataFrame(cur.fetchall(), columns=columns)], axis=0, ignore_index=True)
    print(len(results))
    return results


def get_protein_info(similar_proteins, cur):
    # return info_from_csv(similar_proteins)
    return info_from_db(similar_proteins, cur)


def create_network(query, similar_proteins, protein_info):
    """ Creating network diagram """
    # load pandas df as networkx graph
    if 'Identities' not in similar_proteins.columns:
        similar_proteins['Identities'] = ''
    graph = nx.from_pandas_edgelist(similar_proteins, 'Protein1', 'Protein2', edge_attr=['Score', 'E', 'Identities'])

    # Deciding on the layout of how the nodes will be lined up
    pos = nx.spring_layout(graph, k=0.5, iterations=50, seed=1, weight='Score')
    for n, p in pos.items():
        graph.nodes[n]['pos'] = p

    # Edges
    xtext = []
    ytext = []
    edge_trace = []
    edge_hovertemplate = []
    for edge in graph.edges():
        edge_x = []
        edge_y = []
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
        edge_hovertemplate.append(f"<b>Score:</b> {graph.edges()[edge]['Score']}" +
                                  f"<br><b>E-value:</b> {graph.edges()[edge]['E']}" +
                                  f"<br><b>Identity:</b> {graph.edges()[edge]['Identities']}"
                                  "<extra></extra>")

        # make an edge trace for each edge based on the edge weights (edge width is within in the range of 0.5 to 5.5)
        weight = (graph.edges()[edge]['Score']-similar_proteins['Score'].min())*4/(similar_proteins['Score'].max()-similar_proteins['Score'].min()) + 0.5
        visibility = (graph.edges()[edge]['Score']-similar_proteins['Score'].min())*0.7/(similar_proteins['Score'].max()-similar_proteins['Score'].min()) + 0.3
        edge_trace.append(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            opacity=visibility,
            line=dict(color='rgb(95,70,144)', width=weight)
            )
        )

    eweights_trace = go.Scatter(
        x=xtext, y=ytext,
        mode='text',
        marker=dict(size=0.5),
        textposition='top center')

    eweights_trace.hovertemplate = edge_hovertemplate

    # Nodes
    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition='middle right',
        textfont=dict(size=18, color='black'),
        marker=dict(
            showscale=True,
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

    # Colour node points by number of connections + text to node + text when you hover
    node_adjacency = []
    node_text = []
    node_hovertemplate = []

    pd.set_option('display.max_colwidth', None)   # to display the entire string
    for node, adjacencies in enumerate(graph.adjacency()):
        node_adjacency.append(len(adjacencies[1]))
        entry = adjacencies[0]

        df = protein_info[protein_info['Entry'] == entry]
        entry_name = df['Entry_Name'].to_string(index=False)
        primary_gene = df['Primary_Gene_Name'].to_string(index=False)
        gene_names = df['Gene_Names'].to_string(index=False)
        sequence = df['Sequence'].to_string(index=False)
        sequence = textwrap.fill(sequence).replace('\n', '<br>')
        organism = df['Organism'].to_string(index=False)
        organism_id = df['OrganismID'].to_string(index=False)
        protein_names = df['Protein_names'].to_string(index=False)
        ecnum = df['EC_number'].to_string(index=False)
        family = df['Protein_families'].to_string(index=False)
        pdb = df['PDB'].to_string(index=False)
        function = df['Function'].to_string(index=False).split(': ', 1)[1] if df['Function'].to_string(index=False) != '' else ''
        function = textwrap.fill(function, width=100).replace('\n', '<br>')
        pathway = df['Pathway'].to_string(index=False).split(': ', 1)[1] if df['Pathway'].to_string(index=False) != '' else ''

        node_text.append(entry_name)
        node_hovertemplate.append(f'<b>Entry:</b> {entry}'
                                  + f'<br><b>Entry name:</b> {entry_name}'
                                  + f'<br><b>Primary gene names:</b> {primary_gene}'
                                  + f'<br><b>Gene names:</b> {gene_names}'
                                  + f'<br><b>Organism:</b> {organism}'
                                  + f'<br><b>Organism ID:</b> {organism_id}'
                                  + f'<br><b>Protein names:</b> {protein_names}'
                                  + f'<br><b>EC Number:</b> {ecnum}'
                                  + f'<br><b>Protein families:</b> {family}'
                                  + f'<br><b>PDB:</b> {pdb}'
                                  + f'<br><b>Function:</b> <br>{function}'
                                  + f'<br><b>Pathway:</b> {pathway}'
                                  + f'<br><b>Sequence:</b> <br>{sequence}'
                                  + '<extra></extra>')
    node_trace.marker.color = node_adjacency
    node_trace.text = node_text
    node_trace.hovertemplate = node_hovertemplate

    # change color of query node to red
    for i in range(len(graph.nodes())):
        if node_trace.text[i] == protein_info[protein_info['Entry'] == query]['Entry_Name'].to_string(index=False):
            highlighted = list(node_trace.marker.color)
            highlighted[i] = 'darkred'
            node_trace.marker.color = tuple(highlighted)

    # Create Network Graph
    fig = go.Figure(layout=go.Layout(
        plot_bgcolor='white',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[dict(
            text=f"Query: {query}",
            font=dict(color="darkred"),
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002)],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )

    for trace in edge_trace:
        fig.add_trace(trace)
    fig.add_trace(node_trace)
    fig.add_trace(eweights_trace)
    return fig


def get_visualization(query, n_neighbors, algorithm, organism='All'):
    """ Call this function to get the similarity network for a query """
    # establish a database connection
    connection = database_connection()
    cur = connection.cursor()

    similar_proteins = get_similarity_data(query, n_neighbors, algorithm.lower(), cur)
    protein_info = get_protein_info(similar_proteins, cur)

    cur.close()
    connection.close()

    return create_network(query, similar_proteins, protein_info)


if __name__ == "__main__":
    #diatom_proteins = pd.read_csv("diatom_proteins/new_diatoms.csv")
    #print(diatom_proteins['Entry'].to_list())
    #query = input("Protein ID: ")
    #n_neighbors = int(input("Max. no. of hits: "))
    #algorithm = input("Similarity algorithm: ")
    #get_visualization(query, n_neighbors, algorithm).show()
    get_visualization('A0T0C2', 15, 'fasta').show()

