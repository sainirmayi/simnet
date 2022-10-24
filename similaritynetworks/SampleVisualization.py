import plotly.graph_objects as go
import networkx as nx
import pandas as pd

''' Creating dataframe from sample data '''

main_dataframe = pd.DataFrame(pd.read_csv("sample_data.csv"))
protein_info = main_dataframe.drop(['Unnamed: 0', 'Hit', 'Score(Bits)', 'Identities(%)', 'Positives(%)', 'E()'],
                                   axis=1).drop_duplicates()
protein_info.reset_index(drop=True, inplace=True)
similarities = main_dataframe.drop(['Unnamed: 0', 'DB', 'Description', 'Organism', 'Length'], axis=1)
similarities.reset_index(drop=True, inplace=True)
similarities['Query'] = None
for i in range(440):
    if similarities["Hit"][i] == 1:
        qp = similarities.loc[i, 'Accession']
    similarities['Query'][i] = qp
similarities.rename(columns={'Accession': 'Target'}, inplace=True)
for i in range(440):
    if similarities["Query"][i] == similarities["Target"][i]:
        similarities.drop(labels=i, inplace=True, axis=0)
similarities.reset_index(drop=True, inplace=True)
print(similarities['Query'].unique())
query = input("Query ID: ")
matches = similarities['Target'][similarities['Query'] == query]
results = similarities.drop(['Hit', 'Score(Bits)', 'Positives(%)', 'E()'], axis=1)
for i in range(419):
    if results['Query'][i] != query:
        if results['Query'][i] not in list(matches) or (
                results['Query'][i] in list(matches) and results['Target'][i] not in list(matches)):
            results.drop(labels=i, inplace=True, axis=0)
results.reset_index(drop=True, inplace=True)
G = nx.from_pandas_edgelist(results, 'Query', 'Target', edge_attr='Identities(%)')



''' Creating network diagram '''

pos = nx.spring_layout(G, k=0.5, iterations=50, weight='Identities(%)')
for n, p in pos.items():
    G.nodes[n]['pos'] = p

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
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
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    textposition='middle right',
    textfont=dict(size=10, color='black'),
    marker=dict(
        showscale=False,

        # colorscale options
        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
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
node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append(adjacencies[0])

node_trace.marker.color = node_adjacencies
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
