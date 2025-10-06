import networkx as nx
import plotly.graph_objects as go


def visualize_mindmap(tree, title="🧠 Mindmap Visualization"):
    """
    Visualize the hierarchical mindmap tree using NetworkX and Plotly.
    Each node is labeled and connected to its parent cluster.
    """
    G = nx.DiGraph()

    def add_nodes(node, parent_label=None):
        label = node.get("label", "Unnamed")
        desc = node.get("description", "")
        size = node.get("size", 10)
        G.add_node(label, description=desc, size=size)

        if parent_label:
            G.add_edge(parent_label, label)

        for _, child in node.get("clusters", {}).items():
            add_nodes(child, label)

    # Build the graph recursively
    add_nodes(tree)

    # --- Layout ---
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

    # --- Create Plotly traces ---
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#888"),
        hoverinfo="none",
        mode="lines"
    )

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"<b>{node}</b><br>{G.nodes[node].get('description', '')}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[n for n in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="Blues",
            reversescale=True,
            color=[len(list(G.neighbors(n))) for n in G.nodes()],
            size=[max(10, G.nodes[n].get("size", 10) / 2) for n in G.nodes()],
          
            line_width=2
        )
    )

    # --- Combine ---
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        titlefont_size=20,
                        showlegend=False,
                        hovermode="closest",
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))

    return fig
