import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import linkage, fcluster
import matplotlib.pyplot as plt

class DynamicClusterer:
    """
    Dynamic Agglomerative Clustering system for mindmap creation
    """
    
    def __init__(self, min_clusters=2, max_clusters=10, min_cluster_size=2):
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.min_cluster_size = min_cluster_size
        self.best_params = None
        self.best_score = -1
        
    def find_optimal_clusters(self, embeddings, texts=None):
        """
        Automatically find the optimal clustering configuration
        """
        n_samples = len(embeddings)
        
        # Adjust max_clusters based on data size
        effective_max_clusters = min(self.max_clusters, n_samples // self.min_cluster_size)
        
        print(f"🔍 Finding optimal clusters for {n_samples} samples...")
        print(f"Testing cluster range: {self.min_clusters} to {effective_max_clusters}")
        
        results = self._test_agglomerative(embeddings, effective_max_clusters)
        best_config = self._select_best_configuration(results, n_samples)
        
        if best_config:
            self.best_params = best_config['params']
            self.best_score = best_config['score']
            
            print(f"\n🏆 Optimal Configuration:")
            print(f"   Parameters: {self.best_params}")
            print(f"   Score: {self.best_score:.3f}")
            
            return self._apply_clustering(embeddings, self.best_params['n_clusters'])
        else:
            print("⚠️ No suitable clustering found, using fallback (3 clusters)")
            return self._fallback_clustering(embeddings)
    
    def _test_agglomerative(self, embeddings, max_clusters):
        """Test different numbers of clusters for Agglomerative clustering"""
        results = []
        
        print("\n📊 Testing Agglomerative Clustering...")
        
        for n_clusters in range(self.min_clusters, max_clusters + 1):
            try:
                agg = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
                labels = agg.fit_predict(embeddings)
                
                # Calculate metrics
                silhouette = silhouette_score(embeddings, labels)
                calinski = calinski_harabasz_score(embeddings, labels)
                
                # Cluster balance (prefer balanced clusters)
                cluster_sizes = np.bincount(labels)
                balance_score = 1 - (np.std(cluster_sizes) / np.mean(cluster_sizes))
                
                # Combined score
                mindmap_score = self._calculate_mindmap_score(
                    n_clusters, len(embeddings), silhouette, balance_score
                )
                
                results.append({
                    'params': {'n_clusters': n_clusters},
                    'labels': labels,
                    'silhouette': silhouette,
                    'calinski': calinski,
                    'balance': balance_score,
                    'score': mindmap_score,
                    'n_clusters': n_clusters
                })
                
                print(f"   n_clusters={n_clusters}: sil={silhouette:.3f}, score={mindmap_score:.3f}")
                
            except Exception as e:
                print(f"   n_clusters={n_clusters}: Failed - {e}")
                continue
        
        return results
    
    def _calculate_mindmap_score(self, n_clusters, n_samples, silhouette, balance_score):
        """
        Calculate a score optimized for mindmap creation
        """
        # Ideal cluster count for mindmaps (3-7 main branches)
        ideal_clusters = min(7, max(3, n_samples // 4))
        cluster_score = max(0, 1 - abs(n_clusters - ideal_clusters) / ideal_clusters)
        
        # Weighted final score
        final_score = (
            silhouette * 0.5 +           # Cluster quality
            cluster_score * 0.3 +        # Reasonable number of clusters
            balance_score * 0.2          # Balanced cluster sizes
        )
        
        return max(0, final_score)
    
    def _select_best_configuration(self, results, n_samples):
        """Select the best clustering configuration"""
        if not results:
            return None
        
        valid_results = results
        valid_results.sort(key=lambda x: x['score'], reverse=True)
        return valid_results[0] if valid_results else None
    
    def _apply_clustering(self, embeddings, n_clusters):
        """Apply Agglomerative clustering with chosen parameters"""
        agg = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
        return agg.fit_predict(embeddings)
    
    def _fallback_clustering(self, embeddings):
        """Fallback clustering when optimization fails"""
        n_clusters = min(3, len(embeddings) // 2)
        agg = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
        return agg.fit_predict(embeddings)
    
    def get_hierarchical_levels(self, embeddings, max_levels=3):
        """
        Create multiple hierarchical levels for the mindmap
        """
        linkage_matrix = linkage(embeddings, method='ward')
        levels = {}
        base_clusters = max(2, len(embeddings) // 8)
        
        for level in range(max_levels):
            n_clusters = max(2, base_clusters + level)
            if n_clusters >= len(embeddings):
                break
                
            labels = fcluster(linkage_matrix, t=n_clusters, criterion='maxclust')
            levels[f'Level_{level+1}'] = labels - 1 
        
        return levels
    
    def adapt_to_content_size(self, n_texts):
        """
        Dynamically adjust clustering parameters based on content size
        """
        if n_texts < 10:
            return {'min_clusters': 2, 'max_clusters': 3, 'strategy': 'simple'}
        elif n_texts < 50:
            return {'min_clusters': 3, 'max_clusters': 7, 'strategy': 'moderate'}
        elif n_texts < 200:
            return {'min_clusters': 5, 'max_clusters': 12, 'strategy': 'detailed'}
        else:
            return {'min_clusters': 8, 'max_clusters': 20, 'strategy': 'comprehensive'}


def create_dynamic_mindmap_clusters(embeddings, texts=None):
    """
    Main function to create dynamic clusters for mindmap
    """
    clusterer = DynamicClusterer()
    
    # Adapt parameters based on content size
    adaptation = clusterer.adapt_to_content_size(len(embeddings))
    clusterer.min_clusters = adaptation['min_clusters']
    clusterer.max_clusters = adaptation['max_clusters']
    
    print(f"🎯 Strategy: {adaptation['strategy']}")
    print(f"📊 Cluster range: {adaptation['min_clusters']}-{adaptation['max_clusters']}")
    
    # Find optimal clustering
    labels = clusterer.find_optimal_clusters(embeddings, texts)
    
    # Get hierarchical levels for multi-level mindmap
    hierarchical_levels = clusterer.get_hierarchical_levels(embeddings)
    
    return {
        'primary_labels': labels,
        'hierarchical_levels': hierarchical_levels,
        'params': clusterer.best_params,
        'score': clusterer.best_score
    }
