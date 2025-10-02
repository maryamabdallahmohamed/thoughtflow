from src.loader.json_loader import JSONPreprocessor
from src.core.mindmap_builder import build_mindmap
from utils.language_detector import returnlang
from pyvis.network import Network


def visualize_mindmap_interactive(mindmap, output_html="mindmap.html"):
    net = Network(notebook=True, directed=True)
    
    def add_nodes(node, parent=None):
        net.add_node(node["id"], label=node["label"], title=node["label"])
        if parent:
            net.add_edge(parent, node["id"])
        for child in node.get("children", []):
            add_nodes(child, node["id"])
    
    add_nodes(mindmap)
    net.show(output_html)
processor=JSONPreprocessor()
data = processor.load_and_preprocess_data("/Users/maryamsaad/Documents/Graduation_Proj/junk/chapter4_GT.json")
print(data)
print(type(data))
lang=returnlang(data[0])
print(lang)
mindmap_data=build_mindmap(
    data,
    lang
)
print(mindmap_data)
print(type(mindmap_data))
print(mindmap_data.keys())
for value in mindmap_data.values():
    print("."*100)
    print(value.values if hasattr(value, "values") else value)
visualize_mindmap_interactive(mindmap_data)