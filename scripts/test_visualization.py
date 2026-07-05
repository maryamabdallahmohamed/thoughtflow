import os
import sys

# Ensure the repo root is importable so `backend` resolves when run from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from backend.src.visualizers.mindmap_visualizer import visualize_mindmap_tree

# Load the existing enriched mindmap
with open("enriched_mindmap.json", "r", encoding="utf-8") as f:
    mindmap_data = json.load(f)

# Visualize it with debug output
visualize_mindmap_tree(mindmap_data, output_html="test_mindmap.html", write_html=True, open_in_browser=False)
