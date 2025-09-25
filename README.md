# 🧠 AI Mind-Map Builder

> Transform any text into intelligent, interactive mind maps using advanced NLP and machine learning.

## ✨ Features

- **🤖 AI-Powered**: Automatically extract concepts and relationships from any text
- **📄 Multi-Format Input**: Support for text, PDF, Markdown, URLs, and voice
- **🎯 Smart Clustering**: Hierarchical topic modeling with BERTopic and HDBSCAN  
- **🔗 Relationship Discovery**: Identify cause-effect, similarity, and hierarchical connections
- **🎨 Interactive Canvas**: Drag-and-drop editing with real-time visualization
- **📊 Multiple Exports**: JSON, Mermaid, GraphViz, PNG, SVG formats
- **🔍 Source Traceability**: Click any node to see original text with confidence scores

## 🚀 Quick Start

### Web Interface

1. **Upload or paste your content** (text, PDF, URL)
2. **Wait for AI processing** (30-60 seconds for large documents)
3. **Explore the generated mind map** with interactive controls
4. **Edit and refine** nodes and connections as needed
5. **Export** in your preferred format

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Layer   │───▶│  AI Processing   │───▶│  Visualization  │
│                 │    │                  │    │                 │
│ • Text/PDF      │    │ • Embeddings     │    │ • Interactive   │
│ • URLs          │    │ • Clustering     │    │ • Editable      │
│ • Voice         │    │ • Relations      │    │ • Exportable    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

- **Ingest & Preprocess**: Text extraction and cleaning
- **Representation**: Semantic embeddings with sentence-transformers
- **Structure Discovery**: Hierarchical clustering and relation extraction  
- **Visualization**: Interactive web-based canvas with editing tools

## 🛠️ Configuration
## 📈 Roadmap

- [ ] **Phase 1**: Basic pipeline with Mermaid export
- [ ] **Phase 2**: Interactive web interface
- [ ] **Phase 3**: Advanced editing and collaboration
- [ ] **Phase 4**: API service and integrations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



---

⭐ **Star this repository** if you find it useful!