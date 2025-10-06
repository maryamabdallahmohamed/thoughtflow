# Test script
from backend.src.core.node_labeler import NodeLabelerService
from backend.src.core.node_description import NodeDescriptionService

labeler = NodeLabelerService()
describer = NodeDescriptionService()

test_texts = [
    "Machine learning algorithms can be categorized into supervised and unsupervised learning.",
    "Supervised learning uses labeled data to train models.",
    "Common algorithms include decision trees, neural networks, and support vector machines."
]

# Generate label
label_result = labeler.generate_label(test_texts, depth=1, parent_label="AI Concepts")
print(f"Label: {label_result.label}")

# Generate description
description = describer.generate_description(test_texts, label_result.label, depth=1)
print(f"Description: {description}")