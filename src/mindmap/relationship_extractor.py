#!/usr/bin/env python3
"""
Relationship extraction module for mindmap clustering system
Implements FR2.3: Extract relationships between concepts with confidence scores
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RelationshipExtractor:
    """
    Extracts semantic relationships between concepts within clusters
    """
    
    def __init__(self, similarity_threshold=0.7, max_relationships_per_concept=5):
        self.similarity_threshold = similarity_threshold
        self.max_relationships_per_concept = max_relationships_per_concept
    
    def extract_relationships(self, clustering_result, embeddings, texts):
        """
        Extract directed relationships within each cluster based on cosine similarity
        
        Args:
            clustering_result: Output from dynamic clustering
            embeddings: Concept embeddings array
            texts: List of text segments
            
        Returns:
            dict: Enhanced clustering result with relationships
        """
        
        print(f"🔗 Extracting relationships (threshold: {self.similarity_threshold})")
        
        labels = clustering_result['primary_labels']
        
        # Group concepts by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'index': i,
                'text': texts[i],
                'embedding': embeddings[i]
            })
        
        # Extract relationships for each cluster
        cluster_relationships = {}
        total_relationships = 0
        
        for cluster_id, concepts in clusters.items():
            if len(concepts) < 2:
                cluster_relationships[cluster_id] = []
                continue
            
            relationships = self._extract_cluster_relationships(concepts, cluster_id)
            cluster_relationships[cluster_id] = relationships
            total_relationships += len(relationships)
            
            print(f"   Cluster {cluster_id}: {len(relationships)} relationships from {len(concepts)} concepts")
        
        print(f"✅ Extracted {total_relationships} total relationships")
        
        # Add relationships to clustering result
        enhanced_result = clustering_result.copy()
        enhanced_result['relationships'] = cluster_relationships
        enhanced_result['relationship_stats'] = {
            'total_relationships': total_relationships,
            'similarity_threshold': self.similarity_threshold,
            'relationship_type': 'directed_semantic'
        }
        
        return enhanced_result
    
    def _extract_cluster_relationships(self, concepts, cluster_id):
        """
        Extract relationships within a single cluster
        
        Args:
            concepts: List of concept dictionaries with embeddings
            cluster_id: Cluster identifier
            
        Returns:
            list: List of relationship dictionaries
        """
        
        if len(concepts) < 2:
            return []
        
        relationships = []
        
        # Calculate pairwise similarities
        embeddings_matrix = np.array([concept['embedding'] for concept in concepts])
        similarity_matrix = cosine_similarity(embeddings_matrix)
        
        # Extract directed relationships
        for i, source_concept in enumerate(concepts):
            # Get similarities for this source concept
            similarities = similarity_matrix[i]
            
            # Find target concepts above threshold (excluding self)
            potential_targets = []
            for j, target_concept in enumerate(concepts):
                if i != j and similarities[j] >= self.similarity_threshold:
                    potential_targets.append({
                        'target_index': j,
                        'target_concept': target_concept,
                        'similarity': similarities[j]
                    })
            
            # Sort by similarity (strongest first) and limit
            potential_targets.sort(key=lambda x: x['similarity'], reverse=True)
            selected_targets = potential_targets[:self.max_relationships_per_concept]
            
            # Create relationship objects
            for target in selected_targets:
                relationship = {
                    'source_concept_index': source_concept['index'],  # Global index
                    'target_concept_index': target['target_concept']['index'],  # Global index
                    'source_local_index': i,  # Local cluster index
                    'target_local_index': target['target_index'],  # Local cluster index
                    'confidence_score': float(target['similarity']),
                    'relationship_type': 'semantic_similarity',
                    'cluster_id': cluster_id,
                    'source_text': source_concept['text'][:100] + "..." if len(source_concept['text']) > 100 else source_concept['text'],
                    'target_text': target['target_concept']['text'][:100] + "..." if len(target['target_concept']['text']) > 100 else target['target_concept']['text']
                }
                relationships.append(relationship)
        
        return relationships
    
    def enhance_mindmap_with_relationships(self, mindmap_result, relationship_data):
        """
        Add relationship information to mindmap structure
        
        Args:
            mindmap_result: Original mindmap result from clustering system
            relationship_data: Enhanced clustering result with relationships
            
        Returns:
            dict: Enhanced mindmap with relationship information
        """
        
        print("🌐 Enhancing mindmap with relationships...")
        
        enhanced_mindmap = mindmap_result.copy()
        
        # Add relationships to each branch
        for branch in enhanced_mindmap['mindmap']['branches']:
            cluster_id = int(branch['id'].split('_')[1])
            
            if cluster_id in relationship_data['relationships']:
                branch_relationships = relationship_data['relationships'][cluster_id]
                
                # Convert to branch-local format for easier visualization
                local_relationships = []
                for rel in branch_relationships:
                    local_rel = {
                        'source_index': rel['source_local_index'],
                        'target_index': rel['target_local_index'],
                        'confidence': rel['confidence_score'],
                        'type': rel['relationship_type']
                    }
                    local_relationships.append(local_rel)
                
                branch['relationships'] = local_relationships
                branch['relationship_count'] = len(local_relationships)
            else:
                branch['relationships'] = []
                branch['relationship_count'] = 0
        
        # Add global relationship statistics
        enhanced_mindmap['relationship_stats'] = relationship_data['relationship_stats']
        
        # Calculate relationship density per branch
        for branch in enhanced_mindmap['mindmap']['branches']:
            concept_count = branch['size']
            relationship_count = branch['relationship_count']
            
            if concept_count > 1:
                max_possible = concept_count * (concept_count - 1)  # Directed relationships
                branch['relationship_density'] = relationship_count / max_possible
            else:
                branch['relationship_density'] = 0.0
        
        print(f"✅ Enhanced mindmap with relationship data")
        
        return enhanced_mindmap
    
    def get_relationship_summary(self, enhanced_result):
        """
        Generate a summary of extracted relationships
        
        Args:
            enhanced_result: Result with relationship data
            
        Returns:
            dict: Relationship summary statistics
        """
        
        relationships = enhanced_result.get('relationships', {})
        
        total_relationships = sum(len(rels) for rels in relationships.values())
        cluster_count = len(relationships)
        
        if total_relationships == 0:
            return {
                'total_relationships': 0,
                'average_per_cluster': 0,
                'strongest_relationship': None,
                'weakest_relationship': None
            }
        
        # Find strongest and weakest relationships
        all_relationships = []
        for cluster_rels in relationships.values():
            all_relationships.extend(cluster_rels)
        
        if all_relationships:
            strongest = max(all_relationships, key=lambda x: x['confidence_score'])
            weakest = min(all_relationships, key=lambda x: x['confidence_score'])
            
            return {
                'total_relationships': total_relationships,
                'average_per_cluster': total_relationships / cluster_count if cluster_count > 0 else 0,
                'strongest_relationship': {
                    'confidence': strongest['confidence_score'],
                    'source': strongest['source_text'],
                    'target': strongest['target_text']
                },
                'weakest_relationship': {
                    'confidence': weakest['confidence_score'],
                    'source': weakest['source_text'],
                    'target': weakest['target_text']
                },
                'confidence_range': {
                    'min': weakest['confidence_score'],
                    'max': strongest['confidence_score'],
                    'average': np.mean([rel['confidence_score'] for rel in all_relationships])
                }
            }
        
        return {'total_relationships': 0}

# Integration function for easy use
def extract_and_enhance_relationships(clustering_result, embeddings, texts, 
                                    similarity_threshold=0.7, max_relationships=5):
    """
    Convenience function to extract relationships and enhance mindmap
    
    Args:
        clustering_result: Output from clustering system
        embeddings: Concept embeddings
        texts: Text segments
        similarity_threshold: Minimum similarity for relationships
        max_relationships: Maximum relationships per concept
        
    Returns:
        tuple: (enhanced_clustering_result, relationship_summary)
    """
    
    extractor = RelationshipExtractor(
        similarity_threshold=similarity_threshold,
        max_relationships_per_concept=max_relationships
    )
    
    # Extract relationships
    enhanced_result = extractor.extract_relationships(clustering_result, embeddings, texts)
    
    # Generate summary
    summary = extractor.get_relationship_summary(enhanced_result)
    
    return enhanced_result, summary

