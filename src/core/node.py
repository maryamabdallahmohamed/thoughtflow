class MindmapNode:
    def __init__(self, id, label, children=None):
        self.id = id
        self.label = label
        self.children = children or []

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "children": [c.to_dict() for c in self.children]
        }