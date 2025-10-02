# ThoughtFlow - AI-Powered Mindmap Generation System

A modular, language-aware mindmap generation system built with clean architecture principles.

## 🌟 Features

- **Language-Aware Processing**: Automatically detects input language and generates labels in the same language (Arabic, English, etc.)
- **Hierarchical Clustering**: Uses dynamic clustering to create meaningful hierarchical structures
- **Clean Architecture**: Modular design with clear separation of concerns
- **Meaningful Node Labels**: Human-readable IDs and concise, descriptive labels optimized for graph visualization
- **API-First Design**: RESTful API with FastAPI
- **Multiple Input Formats**: Supports JSON and PDF file uploads
- **LLM-Powered Labels**: Uses GROQ LLM for generating contextual topic labels
- **Multilingual Embeddings**: LaBSE model for cross-lingual semantic understanding

## 📁 Project Structure

```
thoughtflow/
├── config/
│   ├── __init__.py
│   └── settings.py                  # Application configuration
│
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── mindmap_routes.py    # API endpoints
│   │   ├── __init__.py
│   │   └── dependencies.py          # Dependency injection
│   │
│   ├── core/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── node.py              # MindmapNode class
│   │   │   └── schemas.py           # Pydantic models
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── mindmap_service.py   # Main business logic
│   │   │   ├── clustering_service.py # Clustering operations
│   │   │   └── label_service.py     # LLM label generation
│   │   │
│   │   ├── builders/
│   │   │   ├── __init__.py
│   │   │   └── mindmap_builder.py   # Facade pattern
│   │   │
│   │   └── __init__.py
│   │
│   ├── infrastructure/
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract LLM interface
│   │   │   ├── groq_client.py       # GROQ implementation
│   │   │   └── prompt_manager.py    # Prompt management
│   │   │
│   │   ├── embedding/
│   │   │   ├── __init__.py
│   │   │   └── embedder.py          # Sentence embeddings
│   │   │
│   │   └── __init__.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── language_detector.py     # Language detection
│   │   ├── text_processor.py        # Text utilities
│   │   └── validators.py            # Input/output validation
│   │
│   └── loader/
│       ├── json_loader.py           # JSON preprocessing
│       └── pdf_loader.py            # PDF text extraction
│
├── prompts/
│   ├── topic_system_prompt.yaml     # Topic label prompt
│   └── descriptive_system_prompt.yaml # Description prompt
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── main.py                          # Application entry point
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- GROQ API key

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd thoughtflow
```

2. **Create virtual environment**:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:

Create a `.env` file:
```env
# GROQ API
Groq_API=your_groq_api_key_here

# Device Configuration
DEVICE=cpu  # or cuda if GPU available
CACHE_DIR=./cache
```

## 🎯 Usage

### Starting the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Endpoints

#### 1. Generate Mindmap from Text

```bash
POST /api/v1/generate-mindmap
Content-Type: application/json

{
  "document": "Your text here...",
  "lang": "en",  # Optional: "en", "ar", or null for auto-detect
  "max_depth": 3,
  "min_size": 2
}
```

#### 2. Preprocess File

```bash
POST /api/v1/preprocess-file
Content-Type: multipart/form-data

file: <your_file.json or your_file.pdf>
```

#### 3. Generate Mindmap from File

```bash
POST /api/v1/generate-from-file
Content-Type: multipart/form-data

file: <your_file.json or your_file.pdf>
lang: en  # Optional
max_depth: 3
min_size: 2
```

### Python Usage

```python
from src.core.builders.mindmap_builder import build_mindmap

# Simple usage
document = """
Climate change affects weather patterns globally.
Rising temperatures cause extreme weather events.
"""

mindmap = build_mindmap(
    doc=document,
    lang="en",  # Optional, will auto-detect if None
    max_depth=3,
    min_size=2
)

print(mindmap)
```

## 🏗️ Architecture

### Design Principles

1. **Clean Architecture**: Clear separation between domain logic, infrastructure, and API layers
2. **Dependency Injection**: Services are injected through FastAPI dependencies
3. **Interface Segregation**: Abstract base classes for swappable implementations
4. **Single Responsibility**: Each module has one clear purpose
5. **Language Consistency**: End-to-end language preservation from input to output

### Key Components

#### Models Layer
- `MindmapNode`: Core data structure with human-readable IDs
- Pydantic schemas for API validation

#### Service Layer
- `MindmapService`: Orchestrates the generation pipeline
- `ClusteringService`: Handles hierarchical clustering
- `LabelGenerationService`: LLM-powered label generation

#### Infrastructure Layer
- `GroqClient`: LLM client with validation and retry logic
- `EmbeddingService`: Multilingual sentence embeddings
- `PromptManager`: Template loading and formatting

#### Utilities
- `LanguageDetector`: Auto-detect input language
- `TextProcessor`: Text cleaning and preprocessing
- `InputValidator` / `OutputValidator`: Data validation

## 🔧 Configuration

Configure the application via environment variables or `config/settings.py`:

```python
# LLM Settings
GROQ_MODEL = "qwen/qwen3-32b"
GROQ_TEMPERATURE = 0.0

# Embedding Settings
EMBEDDING_MODEL = "sentence-transformers/LaBSE"
EMBEDDING_DEVICE = "cpu"  # or "cuda"

# Mindmap Generation
DEFAULT_MAX_DEPTH = 3
DEFAULT_MIN_SIZE = 2
```

## 🌍 Language Support

The system automatically detects and preserves the input language:

- **Arabic** (ar) → Arabic labels
- **English** (en) → English labels
- Auto-detection if language not specified

### Example: Arabic Input

```python
document = "الذكاء الاصطناعي يغير العالم"
mindmap = build_mindmap(doc=document)  # Auto-detects Arabic
```

Output labels will be in Arabic: `"الذكاء الاصطناعي والتعلم الآلي"`

## 📊 Node Structure

Nodes have meaningful, human-readable IDs:

```json
{
  "id": "climate_change",  // Snake_case, descriptive
  "label": "Climate Change Impact",  // Concise, 5-10 words
  "children": [
    {
      "id": "climate_change_0",
      "label": "Rising Temperatures",
      "children": []
    }
  ]
}
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src tests/
```

## 📝 Development

### Adding a New LLM Provider

1. Create a new class in `src/infrastructure/llm/`:
```python
from src.infrastructure.llm.base import BaseLLMClient

class MyLLMClient(BaseLLMClient):
    def generate(self, prompt, **kwargs):
        # Implementation
        pass
```

2. Update dependencies in `src/api/dependencies.py`

### Customizing Prompts

Edit YAML files in `prompts/`:

```yaml
SYSTEM_PROMPT: |
  Your custom prompt here with {placeholders}
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from project root
2. **GROQ API Errors**: Verify API key in `.env`
3. **CUDA Errors**: Set `DEVICE=cpu` if no GPU available

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ using FastAPI, GROQ, and SentenceTransformers
