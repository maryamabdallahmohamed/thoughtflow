# Migration Guide - ThoughtFlow Refactoring

This document explains the refactoring changes and how to migrate from the old structure to the new one.

## 🎯 What Changed

### Overview
The system has been completely refactored with:
- **Clean Architecture** with separated concerns
- **Language consistency** guaranteed through enhanced prompts and validation
- **Modular API design** with dependency injection
- **Meaningful node naming** with human-readable IDs
- **Professional directory structure**

---

## 📂 Directory Structure Changes

### Old Structure
```
src/
├── core/
│   ├── llm.py                    # Mixed concerns
│   ├── dynamic_clustering.py     # Tight coupling
│   ├── mindmap_builder.py        # No clear separation
│   ├── node.py
│   └── embedder.py
├── api/
│   └── api.py                    # All endpoints in one file
└── loader/
    ├── json_loader.py
    └── pdf_loader.py
```

### New Structure
```
config/
└── settings.py                   # ✨ Centralized configuration

src/
├── api/
│   ├── routes/
│   │   └── mindmap_routes.py     # ✨ Modular routes
│   └── dependencies.py           # ✨ Dependency injection
│
├── core/
│   ├── models/
│   │   ├── node.py               # ✨ Enhanced with sanitization
│   │   └── schemas.py            # ✨ Pydantic validation
│   │
│   ├── services/
│   │   ├── mindmap_service.py    # ✨ Main orchestration
│   │   ├── clustering_service.py # ✨ Clustering logic
│   │   └── label_service.py      # ✨ LLM operations
│   │
│   └── builders/
│       └── mindmap_builder.py    # ✨ Facade pattern
│
├── infrastructure/
│   ├── llm/
│   │   ├── base.py               # ✨ Abstract interface
│   │   ├── groq_client.py        # ✨ With validation
│   │   └── prompt_manager.py     # ✨ Template management
│   │
│   └── embedding/
│       └── embedder.py           # ✨ Service pattern
│
└── utils/
    ├── language_detector.py      # ✨ Enhanced detection
    ├── text_processor.py         # ✨ Text utilities
    └── validators.py             # ✨ Input/output validation

prompts/
├── topic_system_prompt.yaml      # ✨ Improved prompts
└── descriptive_system_prompt.yaml
```

---

## 🔄 Code Migration

### 1. Importing the Mindmap Builder

#### Old Way
```python
from src.core.mindmap_builder import build_mindmap

mindmap = build_mindmap(doc, lang="ar", max_depth=3, min_size=2)
```

#### New Way
```python
# Option 1: Direct import (backward compatible)
from src.core.builders.mindmap_builder import build_mindmap

mindmap = build_mindmap(doc, lang="ar", max_depth=3, min_size=2)

# Option 2: Using the builder class
from src.core.builders.mindmap_builder import MindmapBuilder

builder = MindmapBuilder()
mindmap = builder.build(
    document=doc,
    language="ar",
    max_depth=3,
    min_size=2
)
```

### 2. Using the LLM Client

#### Old Way
```python
from src.core.llm import GROQ

llm = GROQ()
response = llm.chat_with_groq(prompt)
```

#### New Way
```python
from src.infrastructure.llm.groq_client import GroqClient

llm = GroqClient()
response = llm.generate(prompt)

# With validation
response = llm.generate_with_retry(
    prompt=prompt,
    expected_language="Arabic",
    max_retries=2
)
```

### 3. Language Detection

#### Old Way
```python
from utils.language_detector import returnlang

lang = returnlang(text)  # Returns "English" or "Arabic"
```

#### New Way
```python
from src.utils.language_detector import LanguageDetector

# Option 1: Full name
lang = LanguageDetector.detect(text)  # Returns "English" or "Arabic"

# Option 2: Code
lang_code = LanguageDetector.detect_code(text)  # Returns "en" or "ar"

# Option 3: Backward compatible
from src.utils.language_detector import returnlang
lang = returnlang(text)
```

### 4. Embeddings

#### Old Way
```python
from src.core.embedder import Embedder

embedder = Embedder()
embeddings = embedder.encode(texts)
```

#### New Way
```python
from src.infrastructure.embedding.embedder import get_embedding_service

# Get singleton instance
embedder = get_embedding_service()
embeddings = embedder.encode(texts, batch_size=16, normalize=True)
```

### 5. API Endpoints

#### Old Structure (src/api/api.py)
```python
@app.post("/generate-mindmap")
def generate_mindmap(req: MindmapRequest):
    # All logic in endpoint
    mindmap_data = build_mindmap(req.document, req.lang)
    return {"mindmap": mindmap_data}
```

#### New Structure (src/api/routes/mindmap_routes.py)
```python
@router.post("/generate-mindmap", response_model=MindmapResponse)
async def generate_mindmap(
    request: MindmapGenerationRequest,
    builder: MindmapBuilder = Depends(get_mindmap_builder)  # Dependency injection
):
    mindmap_dict = builder.build(
        document=request.document,
        language=request.lang,
        max_depth=request.max_depth,
        min_size=request.min_size
    )
    return MindmapResponse(success=True, mindmap=mindmap_dict, metadata={...})
```

---

## ✨ Key Improvements

### 1. Language Consistency

#### Problem (Old)
- LLM sometimes returned wrong language
- No validation of output language
- Generic prompts without language emphasis

#### Solution (New)
```python
# Enhanced prompts with language enforcement
SYSTEM_PROMPT: |
  CRITICAL REQUIREMENTS:
  1. Output MUST be in {language} - match the language of the input text exactly
  2. NO markdown formatting
  3. NO explanations, only the label itself

# Validation in LLM client
def validate_response(self, response: str, expected_language: str) -> bool:
    if expected_language.lower() in ["arabic", "ar"]:
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in response)
        if not has_arabic:
            return False
    return True

# Retry logic
response = llm.generate_with_retry(
    prompt=prompt,
    expected_language=language,
    max_retries=2
)
```

### 2. Meaningful Node IDs

#### Old
```python
node_id = "root.0.1.2"  # Not descriptive
```

#### New
```python
class MindmapNode:
    @staticmethod
    def _sanitize_id(id: str) -> str:
        """Convert to human-readable snake_case"""
        # "Climate Change" → "climate_change"
        # "AI & ML" → "ai_ml"
        sanitized = id.lower()
        sanitized = re.sub(r'[^\w]+', '_', sanitized)
        return sanitized.strip('_')

# Result: "climate_change" instead of "root.0"
```

### 3. Clean Label Output

#### Old
```python
label = "**Climate Change** - Global Impact"  # Has markdown
```

#### New
```python
class MindmapNode:
    @staticmethod
    def _sanitize_label(label: str) -> str:
        """Remove markdown and limit length"""
        cleaned = re.sub(r'[*_`#\[\]]+', '', label)
        words = cleaned.split()
        if len(words) > 10:
            cleaned = ' '.join(words[:10]) + '...'
        return cleaned

# Result: "Climate Change Global Impact"
```

### 4. Dependency Injection

#### Old
```python
# Tight coupling - create instances in endpoint
@app.post("/generate-mindmap")
def generate_mindmap(req: MindmapRequest):
    embedder = Embedder()  # Created every time
    llm = GROQ()           # Created every time
    mindmap = build_mindmap(req.document)
    return {"mindmap": mindmap}
```

#### New
```python
# Loose coupling - inject dependencies
@router.post("/generate-mindmap")
async def generate_mindmap(
    request: MindmapGenerationRequest,
    builder: MindmapBuilder = Depends(get_mindmap_builder)  # Cached singleton
):
    mindmap = builder.build(document=request.document)
    return MindmapResponse(mindmap=mindmap)
```

---

## 🧪 Testing the New System

### 1. Start the Server
```bash
python main.py
```

### 2. Test Language Consistency (Arabic)
```bash
curl -X POST http://localhost:8000/api/v1/generate-mindmap \
  -H "Content-Type: application/json" \
  -d '{
    "document": "الذكاء الاصطناعي يغير العالم. التعلم الآلي مهم.",
    "max_depth": 3,
    "min_size": 2
  }'
```

Expected: All labels in Arabic, no markdown.

### 3. Test Node Structure
```bash
curl http://localhost:8000/api/v1/generate-mindmap \
  -X POST -H "Content-Type: application/json" \
  -d '{"document": "Climate change affects weather. Rising temperatures."}' \
  | jq '.mindmap.id'
```

Expected: `"climate_change"` or similar human-readable ID.

---

## 📋 Checklist for Migration

- [ ] Update imports from old paths to new paths
- [ ] Replace `GROQ()` with `GroqClient()`
- [ ] Replace `Embedder()` with `get_embedding_service()`
- [ ] Update API endpoint paths (add `/api/v1` prefix)
- [ ] Update `.env` file with new settings
- [ ] Test language detection with Arabic and English texts
- [ ] Verify node IDs are human-readable
- [ ] Check that labels have no markdown artifacts
- [ ] Run existing tests and update as needed

---

## 🔧 Configuration Updates

### Old (.env)
```env
Groq_API=your_key
DEVICE=cpu
CACHE_DIR=./cache
```

### New (.env) - Same, but now managed by settings.py
```env
# GROQ API (same)
Groq_API=your_key

# Device (same)
DEVICE=cpu
CACHE_DIR=./cache

# New settings can be added without code changes
GROQ_MODEL=qwen/qwen3-32b
GROQ_TEMPERATURE=0.0
```

---

## 🚨 Breaking Changes

### 1. API Endpoint Paths
- Old: `/generate-mindmap`
- New: `/api/v1/generate-mindmap`

### 2. Response Format
```python
# Old
{"mindmap": {...}}

# New
{
  "success": true,
  "mindmap": {...},
  "metadata": {
    "language": "English",
    "node_count": 15,
    "max_depth": 3
  }
}
```

### 3. Node ID Format
- Old: `"root.0.1"` (dotted, numeric)
- New: `"climate_change_0"` (snake_case, descriptive)

---

## 📚 Additional Resources

- [README.md](README.md) - Full documentation
- [config/settings.py](config/settings.py) - All configuration options
- [prompts/](prompts/) - Prompt templates

---

## 💡 Tips

1. **Start Small**: Migrate one component at a time
2. **Use Dependency Injection**: Leverage FastAPI's `Depends()`
3. **Test Language**: Always test with both Arabic and English
4. **Read Logs**: Enhanced logging helps debug issues
5. **Check Node IDs**: Verify they're human-readable

---

## ❓ FAQ

**Q: Can I still use the old `build_mindmap()` function?**
A: Yes! It's available at `src.core.builders.mindmap_builder.build_mindmap` for backward compatibility.

**Q: How do I customize prompts?**
A: Edit YAML files in `prompts/` directory. Changes are auto-loaded.

**Q: What if labels are still in wrong language?**
A: Check `groq_client.py:142` - the validation and retry logic. Increase `max_retries`.

**Q: How do I add a new LLM provider?**
A: Implement `BaseLLMClient` interface in `src/infrastructure/llm/`.

---

Happy migrating! 🚀
