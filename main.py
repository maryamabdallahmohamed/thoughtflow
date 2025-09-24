from src.mindmap.clustering_system import MindmapClusteringSystem
from src.mindmap.generate_descriptive_captions import MindmapDescriptionGenerator
from src.mindmap.generate_topic_captions import MindmapCaptionGenerator
from src.loader.json_loader import JSONPreprocessor


system=MindmapClusteringSystem()
processor= JSONPreprocessor()
#load json data
path='/Users/maryamsaad/Documents/Graduation_Proj/junk/medium_GT.json'
data=processor.load_and_preprocess_data(path)
print(data)
# Basic clustering
result = system.process_document(data)

# Enhance with AI captions
caption_gen = MindmapCaptionGenerator()
result = caption_gen.apply_captions_to_mindmap(result)

# Add hover descriptions  
desc_gen = MindmapDescriptionGenerator()
result = desc_gen.apply_descriptions_to_mindmap(result)

print(result)