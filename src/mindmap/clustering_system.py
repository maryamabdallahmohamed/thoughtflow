from src.core.dynamic_clustering import create_dynamic_mindmap_clusters
from src.core.embedder import Embedder
from src.core.ingestion_pipeline import ingestion_pipeline
import json

class MindmapClusteringSystem:
    """
    Complete clustering system for mindmap application - FIXED VERSION
    """
    
    def __init__(self):
        self.embedder = Embedder()
        
    def process_document(self, document_content, document_type="text"):
        """
        Process a document and create dynamic clusters for mindmap
        """
        
        print(f"📄 Processing document ({document_type})...")
        
        # 1. Text Processing & Segmentation
        if document_type == "json":
            texts = self._extract_from_json(document_content)
        elif isinstance(document_content, list):
            texts = document_content
        else:
            texts = [document_content]
        
        print(f"📚 Extracted {len(texts)} raw texts")
        
        # Clean and segment texts
        cleaned_texts = ingestion_pipeline(texts)
        print(f"📝 Processed {len(cleaned_texts)} text segments")
        
        if len(cleaned_texts) < 2:
            return self._handle_insufficient_data(cleaned_texts)
        
        # 2. Generate Embeddings
        print("🔢 Generating embeddings...")
        embeddings = self.embedder.encode(cleaned_texts)
        
        # 3. Dynamic Clustering
        print("🎯 Applying dynamic clustering...")
        clustering_result = create_dynamic_mindmap_clusters(embeddings, cleaned_texts)
        
        # 4. Create Mindmap Structure
        mindmap_structure = self._create_mindmap_structure(
            cleaned_texts, 
            clustering_result
        )
        
        return {
            'texts': cleaned_texts,
            'embeddings': embeddings,
            'clustering': clustering_result,
            'mindmap': mindmap_structure,
            'metadata': {
                'total_segments': len(cleaned_texts),
                'cluster_count': len(set(clustering_result['primary_labels'])),
                'quality_score': clustering_result['score']
            }
        }
    
    def _extract_from_json(self, json_content):
        """Extract texts from JSON content - FIXED"""
        try:
            if isinstance(json_content, str):
                # If it's a file path
                if json_content.endswith('.json'):
                    with open(json_content, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    # If it's a JSON string
                    data = json.loads(json_content)
            else:
                data = json_content
            
            # Extract texts properly
            if isinstance(data, dict):
                if 'texts' in data:
                    return data['texts']  # This is the correct field!
                elif 'content' in data:
                    return data['content'] if isinstance(data['content'], list) else [data['content']]
                else:
                    # Fallback: collect all string values
                    texts = []
                    for value in data.values():
                        if isinstance(value, str) and len(value.strip()) > 10:
                            texts.append(value)
                        elif isinstance(value, list):
                            texts.extend([str(item) for item in value if isinstance(item, str)])
                    return texts
            elif isinstance(data, list):
                return [str(item) for item in data]
            else:
                return [str(data)]
                
        except Exception as e:
            print(f"⚠️  JSON extraction error: {e}")
            return [str(json_content)]
    
    def _handle_insufficient_data(self, texts):
        """Handle cases with very little data"""
        return {
            'texts': texts,
            'embeddings': None,
            'clustering': None,
            'mindmap': {
                'main_topic': texts[0] if texts else "No content",
                'branches': [],
                'structure': 'single_node'
            },
            'metadata': {
                'total_segments': len(texts),
                'algorithm_used': 'none',
                'cluster_count': 1,
                'quality_score': 0.0,
                'warning': 'Insufficient data for clustering'
            }
        }
    
    def _create_mindmap_structure(self, texts, clustering_result):
        """Create hierarchical mindmap structure from clustering results"""
        labels = clustering_result['primary_labels']
        
        # Group texts by primary clusters
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'index': i,
                'text': texts[i],
                'display_text': self._create_display_text(texts[i])
            })
        
        # Create main branches
        branches = []
        for cluster_id, cluster_texts in clusters.items():
            branch = {
                'id': f'branch_{cluster_id}',
                'title': self._generate_branch_title(cluster_texts),
                'concepts': cluster_texts,
                'size': len(cluster_texts),
                'color': self._assign_branch_color(cluster_id)
            }
            branches.append(branch)
        
        # Sort branches by size (largest first)
        branches.sort(key=lambda x: x['size'], reverse=True)
        
        return {
            'main_topic': self._generate_main_topic(texts),
            'branches': branches,
            'structure': 'hierarchical',
            'layout_suggestions': self._suggest_layout(branches)
        }
    
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
    
    def _generate_branch_title(self, cluster_texts):
        """Generate a title for a branch based on its content"""
        if not cluster_texts:
            return "Branch"
        
        # Use the first text's beginning as title
        first_text = cluster_texts[0]['text']
        words = first_text.split()[:4]
        return ' '.join(words) + ("..." if len(words) == 4 else "")
    
    def _generate_main_topic(self, texts):
        """Generate main topic title from all texts"""
        if not texts:
            return "Document"
        
        # Simple approach: use first text's beginning
        first_text_words = texts[0].split()[:3]
        return ' '.join(first_text_words) + "..."
    
    def _assign_branch_color(self, cluster_id):
        """Assign colors to branches for visualization"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
        return colors[cluster_id % len(colors)]
    
    def _suggest_layout(self, branches):
        """Suggest layout configuration based on branch count and sizes"""
        n_branches = len(branches)
        
        if n_branches <= 3:
            return {'type': 'radial', 'arrangement': 'balanced'}
        elif n_branches <= 6:
            return {'type': 'tree', 'arrangement': 'hierarchical'}
        else:
            return {'type': 'force_directed', 'arrangement': 'clustered'}
    
    def visualize_mindmap(self, result, visualization_type='interactive', save_path=None):
        """
        Optional visualization integration - imports visualization module when needed
        
        Args:
            result: Output from process_document()
            visualization_type: 'interactive', 'static', 'network', 'dashboard', or 'all'
            save_path: Path to save visualizations (optional)
        """
        try:
            from utils.visualization_scripts import MindmapVisualizer
            
            if not result['clustering']:
                print("⚠️  No clustering data available for visualization")
                return
            
            print(f"🎨 Creating {visualization_type} visualization...")
            
            # Create visualizer instance and generate plots
            visualizer = MindmapVisualizer()
            visualizer.create_visualizations(result, visualization_type, save_path)
            
        except ImportError as e:
            print(f"⚠️  Visualization dependencies not available: {e}")
            print("💡 Install visualization dependencies: pip install matplotlib plotly seaborn networkx")
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            print("💡 Make sure utils/visualization_scripts.py exists and is properly configured")


