#!/usr/bin/env python3
"""
Visualization scripts for mindmap clustering - Optional module
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

class MindmapVisualizer:
    """
    Comprehensive visualization system for mindmap clustering results
    """
    
    def __init__(self):
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
    
    def create_visualizations(self, result, visualization_type='interactive', save_path=None):
        """
        Create comprehensive visualizations of the mindmap
        
        Args:
            result: Output from MindmapClusteringSystem.process_document()
            visualization_type: 'interactive', 'static', 'network', 'dashboard', or 'all'
            save_path: Path to save visualizations (optional)
        """
        
        if not result['clustering']:
            print("⚠️  No clustering data available for visualization")
            return
        
        embeddings = result['embeddings']
        labels = result['clustering']['primary_labels']
        texts = result['texts']
        branches = result['mindmap']['branches']
        
        print(f"🎨 Creating {visualization_type} visualization...")
        
        if visualization_type == 'interactive' or visualization_type == 'all':
            self._create_interactive_mindmap(embeddings, labels, texts, branches, save_path)
        
        if visualization_type == 'static' or visualization_type == 'all':
            self._create_static_mindmap(embeddings, labels, texts, branches, save_path, result)
        
        if visualization_type == 'network' or visualization_type == 'all':
            self._create_network_mindmap(embeddings, labels, texts, branches, save_path)
        
        if visualization_type == 'dashboard' or visualization_type == 'all':
            self._create_mindmap_dashboard(result, save_path)
    
    def _create_display_text(self, text, max_length=60):
        """Create shortened display text for mindmap nodes"""
        if len(text) <= max_length:
            return text
        
        # Try to cut at word boundary
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."
    
    def _create_interactive_mindmap(self, embeddings, labels, texts, branches, save_path=None):
        """Create interactive plotly mindmap visualization"""
        
        # Reduce dimensionality for visualization
        if embeddings.shape[1] > 2:
            pca = PCA(n_components=2)
            coords_2d = pca.fit_transform(embeddings)
        else:
            coords_2d = embeddings
        
        # Create color mapping
        color_map = {i: self.colors[i % len(self.colors)] for i in range(len(set(labels)))}
        
        # Create interactive scatter plot
        fig = go.Figure()
        
        # Add points for each cluster
        for cluster_id in set(labels):
            cluster_mask = labels == cluster_id
            cluster_coords = coords_2d[cluster_mask]
            cluster_texts = [texts[i] for i, mask in enumerate(cluster_mask) if mask]
            
            # Find branch info
            branch = next((b for b in branches if int(b['id'].split('_')[1]) == cluster_id), None)
            branch_title = branch['title'] if branch else f"Cluster {cluster_id}"
            
            fig.add_trace(go.Scatter(
                x=cluster_coords[:, 0],
                y=cluster_coords[:, 1],
                mode='markers+text',
                name=branch_title,
                text=[f"C{cluster_id}-{i+1}" for i in range(len(cluster_coords))],
                textposition="middle center",
                hovertext=[self._create_display_text(text, 100) for text in cluster_texts],
                hovertemplate="<b>%{text}</b><br>%{hovertext}<extra></extra>",
                marker=dict(
                    size=12,
                    color=color_map[cluster_id],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                )
            ))
        
        # Add cluster centers
        for cluster_id in set(labels):
            cluster_mask = labels == cluster_id
            cluster_coords = coords_2d[cluster_mask]
            center = np.mean(cluster_coords, axis=0)
            
            # Add cluster center
            branch = next((b for b in branches if int(b['id'].split('_')[1]) == cluster_id), None)
            branch_title = branch['title'] if branch else f"Cluster {cluster_id}"
            
            fig.add_trace(go.Scatter(
                x=[center[0]],
                y=[center[1]],
                mode='markers+text',
                name=f"Center: {branch_title}",
                text=[branch_title],
                textposition="bottom center",
                showlegend=False,
                marker=dict(
                    size=20,
                    color=color_map[cluster_id],
                    symbol='diamond',
                    line=dict(width=3, color='black')
                )
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': "🧠 Interactive Mindmap Visualization",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            hovermode='closest',
            width=1000,
            height=700,
            template='plotly_white'
        )
        
        if save_path:
            fig.write_html(f"{save_path}_interactive_mindmap.html")
            print(f"💾 Interactive mindmap saved to {save_path}_interactive_mindmap.html")
        
        fig.show()
    
    def _create_static_mindmap(self, embeddings, labels, texts, branches, save_path=None, result=None):
        """Create static matplotlib mindmap visualization"""
        
        # Reduce dimensionality
        if embeddings.shape[1] > 2:
            pca = PCA(n_components=2)
            coords_2d = pca.fit_transform(embeddings)
        else:
            coords_2d = embeddings
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🧠 Mindmap Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Main scatter plot
        color_map = {i: self.colors[i % len(self.colors)] for i in range(len(set(labels)))}
        
        for cluster_id in set(labels):
            cluster_mask = labels == cluster_id
            cluster_coords = coords_2d[cluster_mask]
            
            ax1.scatter(cluster_coords[:, 0], cluster_coords[:, 1], 
                       c=color_map[cluster_id], s=100, alpha=0.7, 
                       label=f'Cluster {cluster_id}')
            
            # Add cluster center
            center = np.mean(cluster_coords, axis=0)
            ax1.scatter(center[0], center[1], c='black', s=200, marker='*', 
                       edgecolors=color_map[cluster_id], linewidth=2)
        
        ax1.set_title('Cluster Distribution')
        ax1.set_xlabel('Dimension 1')
        ax1.set_ylabel('Dimension 2')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Cluster sizes bar chart
        cluster_sizes = [len([l for l in labels if l == cluster_id]) for cluster_id in set(labels)]
        cluster_names = [f'Cluster {i}' for i in set(labels)]
        
        bars = ax2.bar(cluster_names, cluster_sizes, color=[color_map[i] for i in set(labels)])
        ax2.set_title('Cluster Sizes')
        ax2.set_ylabel('Number of Concepts')
        plt.setp(ax2.get_xticklabels(), rotation=45)
        
        # Add value labels on bars
        for bar, size in zip(bars, cluster_sizes):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(size), ha='center', va='bottom')
        
        # 3. Branch hierarchy visualization
        branch_data = [(branch['title'][:20] + "..." if len(branch['title']) > 20 else branch['title'], 
                       branch['size']) for branch in branches]
        branch_titles, branch_sizes = zip(*branch_data)
        
        wedges, texts_pie, autotexts = ax3.pie(branch_sizes, labels=branch_titles, autopct='%1.1f%%',
                                              colors=[branch['color'] for branch in branches])
        ax3.set_title('Branch Distribution')
        
        # 4. Quality metrics
        metrics_data = {
            'Total Concepts': len(texts),
            'Clusters': len(set(labels)),
            'Avg Cluster Size': np.mean(cluster_sizes),
            'Quality Score': result.get('metadata', {}).get('quality_score', 0) * 100 if result else 0
        }
        
        metric_names = list(metrics_data.keys())
        metric_values = list(metrics_data.values())
        
        bars = ax4.barh(metric_names, metric_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax4.set_title('Mindmap Metrics')
        ax4.set_xlabel('Values')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, metric_values)):
            ax4.text(bar.get_width() + max(metric_values) * 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{value:.1f}', ha='left', va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}_static_mindmap.png", dpi=300, bbox_inches='tight')
            print(f"💾 Static mindmap saved to {save_path}_static_mindmap.png")
        
        plt.show()
    
    def _create_network_mindmap(self, embeddings, labels, texts, branches, save_path=None):
        """Create network graph visualization of the mindmap"""
        
        G = nx.Graph()
        
        # Add central node
        G.add_node("MAIN", type="center", label="Main Topic")
        
        # Add cluster nodes and connections
        cluster_centers = {}
        for cluster_id in set(labels):
            cluster_label = f"Cluster_{cluster_id}"
            branch = next((b for b in branches if int(b['id'].split('_')[1]) == cluster_id), None)
            branch_title = branch['title'] if branch else f"Cluster {cluster_id}"
            
            G.add_node(cluster_label, type="cluster", label=branch_title, 
                      color=branch['color'] if branch else '#CCCCCC')
            G.add_edge("MAIN", cluster_label)
            cluster_centers[cluster_id] = cluster_label
        
        # Add concept nodes
        for i, (text, label) in enumerate(zip(texts, labels)):
            concept_id = f"Concept_{i}"
            display_text = self._create_display_text(text, 30)
            
            G.add_node(concept_id, type="concept", label=display_text, full_text=text)
            G.add_edge(cluster_centers[label], concept_id)
        
        # Create visualization
        plt.figure(figsize=(14, 10))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw different node types
        center_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'center']
        cluster_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'cluster']
        concept_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'concept']
        
        # Draw center node
        nx.draw_networkx_nodes(G, pos, nodelist=center_nodes, node_color='red', 
                              node_size=1000, alpha=0.9)
        
        # Draw cluster nodes
        cluster_colors = [G.nodes[n].get('color', '#CCCCCC') for n in cluster_nodes]
        nx.draw_networkx_nodes(G, pos, nodelist=cluster_nodes, node_color=cluster_colors, 
                              node_size=500, alpha=0.8)
        
        # Draw concept nodes
        nx.draw_networkx_nodes(G, pos, nodelist=concept_nodes, node_color='lightblue', 
                              node_size=200, alpha=0.7)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.5, width=1)
        
        # Add labels
        labels_dict = {n: d['label'] for n, d in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels_dict, font_size=8)
        
        plt.title("🕸️ Network Mindmap Visualization", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        if save_path:
            plt.savefig(f"{save_path}_network_mindmap.png", dpi=300, bbox_inches='tight')
            print(f"💾 Network mindmap saved to {save_path}_network_mindmap.png")
        
        plt.show()
    
    def _create_mindmap_dashboard(self, result, save_path=None):
        """Create comprehensive dashboard with multiple views"""
        
        embeddings = result['embeddings']
        labels = result['clustering']['primary_labels']
        texts = result['texts']
        branches = result['mindmap']['branches']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cluster Distribution', 'Cluster Sizes', 'Quality Metrics', 'Text Length Distribution'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )
        
        # 1. Cluster distribution (PCA)
        if embeddings.shape[1] > 2:
            pca = PCA(n_components=2)
            coords_2d = pca.fit_transform(embeddings)
        else:
            coords_2d = embeddings
        
        color_map = {i: self.colors[i % len(self.colors)] for i in range(len(set(labels)))}
        
        for cluster_id in set(labels):
            cluster_mask = labels == cluster_id
            cluster_coords = coords_2d[cluster_mask]
            
            fig.add_trace(
                go.Scatter(
                    x=cluster_coords[:, 0],
                    y=cluster_coords[:, 1],
                    mode='markers',
                    name=f'Cluster {cluster_id}',
                    marker=dict(color=color_map[cluster_id], size=8),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # 2. Cluster sizes
        cluster_sizes = [len([l for l in labels if l == cluster_id]) for cluster_id in set(labels)]
        cluster_names = [f'Cluster {i}' for i in set(labels)]
        
        fig.add_trace(
            go.Bar(
                x=cluster_names,
                y=cluster_sizes,
                marker_color=[color_map[i] for i in set(labels)],
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Quality metrics
        metrics = {
            'Total Concepts': len(texts),
            'Clusters': len(set(labels)),
            'Quality Score': result.get('metadata', {}).get('quality_score', 0) * 100
        }
        
        fig.add_trace(
            go.Bar(
                x=list(metrics.keys()),
                y=list(metrics.values()),
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. Text length distribution
        text_lengths = [len(text.split()) for text in texts]
        
        fig.add_trace(
            go.Histogram(
                x=text_lengths,
                nbinsx=10,
                marker_color='lightgreen',
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="🧠 Mindmap Analysis Dashboard",
            title_x=0.5,
            height=800,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(f"{save_path}_dashboard.html")
            print(f"💾 Dashboard saved to {save_path}_dashboard.html")
        
        fig.show()

# Standalone usage
def visualize_mindmap_result(result, visualization_type='all', save_path=None):
    """
    Standalone function to visualize mindmap results
    
    Args:
        result: Output from MindmapClusteringSystem.process_document()
        visualization_type: 'interactive', 'static', 'network', 'dashboard', or 'all'
        save_path: Path to save visualizations (optional)
    """
    visualizer = MindmapVisualizer()
    visualizer.create_visualizations(result, visualization_type, save_path)

if __name__ == "__main__":
    print("🎨 Mindmap Visualization Scripts")
    print("This module provides visualization capabilities for mindmap clustering results.")
    print("Import and use MindmapVisualizer class or visualize_mindmap_result function.")