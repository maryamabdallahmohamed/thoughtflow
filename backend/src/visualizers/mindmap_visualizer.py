

import os
import webbrowser
import plotly.graph_objects as go

def visualize_mindmap_tree(mindmap_data, output_html="mindmap_output.html"):
    """
    Visualize a hierarchical mindmap (tree layout) using Plotly with auto spacing.
    """
    nodes = []
    edges = []

    # Compute layout dynamically so children spread horizontally
    def traverse(node, parent_id=None, depth=0, x_offset=0):
        node_id = id(node)
        label = node.get("label") or (" ".join(node.get("texts", []))[:60] + "...")
        desc = node.get("description", "")
        children = list(node.get("clusters", {}).values())

        # Recursively get width (number of leaf nodes)
        def get_subtree_width(n):
            c = n.get("clusters", {})
            if not c:
                return 1
            return sum(get_subtree_width(child) for child in c.values())

        width = get_subtree_width(node)
        node_x = x_offset + width / 2.0  # center of this subtree
        node_y = -depth * 2.0  # vertical distance between levels

        nodes.append({
            "id": node_id,
            "label": label,
            "desc": desc,
            "depth": depth,
            "parent": parent_id,
            "x": node_x,
            "y": node_y
        })

        if parent_id:
            edges.append((parent_id, node_id))

        # Spread children horizontally
        child_x = x_offset
        for child in children:
            child_width = get_subtree_width(child)
            traverse(child, node_id, depth + 1, child_x)
            child_x += child_width

    # Start traversal from root
    traverse(mindmap_data)

    # Build edges
    edge_x, edge_y = [], []
    node_positions = {n["id"]: (n["x"], n["y"]) for n in nodes}
    for parent, child in edges:
        x0, y0 = node_positions[parent]
        x1, y1 = node_positions[child]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    # Build node traces
    node_x = [n["x"] for n in nodes]
    node_y = [n["y"] for n in nodes]
    labels = [n["label"] for n in nodes]
    hover_texts = [f"<b>{n['label']}</b><br>{n['desc']}" for n in nodes]

    fig = go.Figure()

    # Edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color='rgba(100,100,100,0.5)'),
        hoverinfo='none'
    ))

    # Nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=labels,
        textposition='bottom center',
        hoverinfo='text',
        hovertext=hover_texts,
        marker=dict(size=12, color='lightblue', line=dict(width=1, color='darkblue'))
    ))

    # Layout
    fig.update_layout(
        title="🌳 Hierarchical Mindmap (Tree Layout)",
        showlegend=False,
        hovermode='closest',
        margin=dict(t=60, l=20, r=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white',
        height=1000,
        width=1600
    )

    # Save and open
    fig.write_html(output_html)
    abs_path = os.path.abspath(output_html)
    print(f"✅ Tree mindmap saved to {output_html}")
    webbrowser.open(f"file://{abs_path}")