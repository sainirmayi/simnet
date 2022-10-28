import plotly.graph_objects as go
import networkx as nx
import pandas as pd


def create_sample_db():
    """ Sample dataframes to represent the databases """
    main_dataframe = pd.DataFrame(pd.read_csv("sample_data.csv"))
    protein_info = main_dataframe.drop(['Hit', 'Score(Bits)', 'Identities(%)', 'Positives(%)', 'E()'],
                                       axis=1).drop_duplicates()
    protein_info.reset_index(drop=True, inplace=True)
    similarity_db = main_dataframe.drop(['DB', 'Description', 'Organism', 'Length'], axis=1)
    similarity_db.reset_index(drop=True, inplace=True)
    similarity_db['Protein1'] = None
    for i in range(similarity_db.shape[0]):
        if similarity_db["Hit"][i] == 1:
            qp = similarity_db.loc[i, 'Accession']
        similarity_db['Protein1'][i] = qp
    similarity_db.rename(columns={'Accession': 'Protein2', 'Score(Bits)': 'Score',
                                  'Identities(%)': 'Identities', 'Positives(%)': 'Positives', 'E()': 'E'},
                         inplace=True)
    similarity_db.reset_index(drop=True, inplace=True)
    return similarity_db


def get_similarity_data(query):
    """ Creating dataframe of similar proteins.
     To be replaced with a function to query the database
     and maybe obtain a result dataframe with the 20 most similar proteins. """

    # similarity_db = pd.DataFrame(pd.read_csv("final.csv"))
    # results = similarity_db.drop(['Hit', 'DB', 'Organism', 'Length', 'Score', 'Positives', 'E'], axis=1)

    similarity_db = create_sample_db()
    results = similarity_db.drop(['Hit', 'Score', 'Positives', 'E'], axis=1)

    similarity_db.sort_values(by=['Protein1', 'Identities'], ascending=False, inplace=True)
    similarity_db.reset_index(drop=True, inplace=True)
    similar = list(similarity_db['Protein2'][similarity_db['Protein1'] == query])
    similar.remove(query)
    top20 = similar[:20]

    for i in range(results.shape[0]):
        if results['Protein1'][i] != query:
            if results['Protein1'][i] not in top20 or \
                    (results['Protein1'][i] in top20 and results['Protein2'][i] not in top20):
                results.drop(labels=i, inplace=True, axis=0)
        else:
            if results["Protein1"][i] == results["Protein2"][i] or results['Protein2'][i] not in top20:
                results.drop(labels=i, inplace=True, axis=0)

    results.reset_index(drop=True, inplace=True)
    return results


def create_network(similar_proteins):
    """ Creating network diagram """
    graph = nx.from_pandas_edgelist(similar_proteins, 'Protein1', 'Protein2', edge_attr='Identities')
    pos = nx.spring_layout(graph, k=0.5, iterations=50, weight='Identities')
    for n, p in pos.items():
        graph.nodes[n]['pos'] = p

    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['pos']
        x1, y1 = graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#aaa'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    # Try hovertemplate instead of hoverinfo to display more information
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
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
    node_adjacency = []
    node_text = []
    for node, adjacencies in enumerate(graph.adjacency()):
        node_adjacency.append(len(adjacencies[1]))
        node_text.append(adjacencies[0])

    node_trace.marker.color = node_adjacency
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
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
    fig.show()


def get_visualization(query):
    """ Call this function to get the similarity network for a query """
    similar_proteins = get_similarity_data(query)
    create_network(similar_proteins)


if __name__ == "__main__":
    similarity_db = create_sample_db()
    # similarity_db = pd.DataFrame(pd.read_csv("final.csv"))
    print(similarity_db['Protein1'].unique())
    query = input("Query ID: ")
    get_visualization(query)