# Replicate Batch Process

**[中文版 README](README_CN.md)** | **English** | **[PyPI Package](https://pypi.org/project/replicate-batch-process/)**

[![PyPI version](https://badge.fury.io/py/replicate-batch-process.svg)](https://badge.fury.io/py/replicate-batch-process)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intelligent batch processing tool for Replicate models with **automatic fallback mechanisms** and concurrent processing.

## ✨ Key Features

- 🔄 **Intelligent Fallback System** - Automatic model switching on incompatibility
- ⚡ **Smart Concurrency Control** - Adaptive rate limiting and batch processing
- 🎯 **Three Usage Modes** - Single, batch same-model, and mixed-model processing
- 📝 **Custom File Naming** - Ordered output with correspondence control
- 🛡️ **Error Resilience** - Comprehensive retry and recovery mechanisms

## 📦 Installation

```bash
pip install replicate-batch-process
```

## 🚀 Quick Start

### 1. Initialize Environment
```bash
# Set up API keys (first time only)
replicate-init
```

### 2. Single Image Generation
```python
from replicate_batch_process import replicate_model_calling

file_paths = replicate_model_calling(
    prompt="A beautiful sunset over mountains",
    model_name="black-forest-labs/flux-dev",
    output_filepath="output/sunset.jpg"
)
```

### 3. Batch Processing
```python
import asyncio
from replicate_batch_process import intelligent_batch_process

files = await intelligent_batch_process(
    prompts=["sunset", "city", "forest"],
    model_name="black-forest-labs/flux-dev",
    max_concurrent=8
)
```

## 🔄 Intelligent Fallback System

**Automatic model switching when issues arise:**

### Reference Image Auto-Detection
```python
# User provides reference image to non-supporting model
replicate_model_calling(
    prompt="Generate based on this image",
    model_name="black-forest-labs/flux-dev",  # Doesn't support reference images
    input_image="path/to/image.jpg"           # → Auto-switches to flux-kontext-max
)
```

### Parameter Compatibility Handling
```python
# Unsupported parameters automatically cleaned and model switched
replicate_model_calling(
    prompt="Generate image",
    model_name="black-forest-labs/flux-kontext-max",
    guidance=3.5,        # Unsupported parameter
    num_outputs=2        # → Auto-switches to compatible model
)
```

### API Error Recovery
Automatic fallback chain: `Flux Dev` → `Qwen Image` → `Imagen 4 Ultra`

## 📋 Usage Scenarios

| Mode | Use Case | Command |
|------|----------|---------|
| **Single** | One-off generation, testing | `replicate_model_calling()` |
| **Batch Same** | Multiple prompts, same model | `intelligent_batch_process()` |
| **Mixed Models** | Different models/parameters | `IntelligentBatchProcessor()` |

## 🧠 Smart Processing Strategies

The system automatically selects optimal processing strategy:

- **Immediate Processing**: Tasks ≤ available quota → Full concurrency
- **Window Processing**: Tasks ≤ 600 but > current quota → Wait then batch
- **Dynamic Queue**: Tasks > 600 → Continuous processing with queue management

## ⚙️ Configuration

### API Keys
Get your Replicate API token: [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)

### Custom Fallback Rules
Modify `config.py`:
```python
FALLBACK_MODELS = {
    'your-model': {
        'fail': {
            'fallback_model': 'backup-model',
            'condition': 'api_error'
        }
    }
}
```

## 📊 Rate Limiting

- **Replicate API**: 600 requests/minute (shared across all models)
- **Recommended Concurrency**: 5-8 (conservative) to 12 (aggressive)
- **Auto-Retry**: Built-in 429 error handling with exponential backoff

## 💡 Best Practices

```python
# For large batches, use chunking
def process_large_batch(prompts, chunk_size=50):
    for chunk in chunks(prompts, chunk_size):
        files = await intelligent_batch_process(chunk, model_name)
        yield files

# Error handling
for result in results:
    if result.success:
        print(f"✅ Generated: {result.file_paths}")
    else:
        print(f"❌ Failed: {result.error}")
```

## 🏗️ Project Structure

```
replicate-batch-process/
├── main.py                      # Single image generation
├── intelligent_batch_processor.py  # Batch processing engine
├── config.py                    # Model configurations & fallbacks
├── init_environment.py          # Environment setup
└── example_usage.py            # Complete examples
```

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/preangelleo/replicate_batch_process.git

# Install in development mode
pip install -e .

# Run examples
python example_usage.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔗 Links

- **PyPI**: https://pypi.org/project/replicate-batch-process/
- **GitHub**: https://github.com/preangelleo/replicate_batch_process
- **Issues**: https://github.com/preangelleo/replicate_batch_process/issues

---

**Made with ❤️ for the AI community**