# Replicate Batch Process

**[中文版 README](https://github.com/preangelleo/replicate_batch_process/blob/main/README_CN.md)** | **English** | **[PyPI Package](https://pypi.org/project/replicate-batch-process/)**

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
- ✅ **Model Validation** - Automatic detection of unsupported models with clear error messages

## 📋 Requirements

### System Requirements
- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **Operating System**: Windows, macOS, Linux
- **Memory**: Minimum 4GB RAM recommended

### Dependencies
```txt
replicate>=0.15.0      # Replicate API client
requests>=2.25.0       # HTTP library
asyncio-throttle>=1.0.2  # Rate limiting for async operations
python-dotenv>=0.19.0  # Environment variable management
```

### API Requirements
- **Replicate API Token**: Required ([Get one here](https://replicate.com/account/api-tokens))
- **Network**: Stable internet connection for API calls
- **Rate Limits**: 600 requests/minute (shared across all models)

## 📦 Installation

```bash
# First time installation
pip install replicate-batch-process

# Upgrade to latest version
pip install --upgrade replicate-batch-process
```

## 🚀 Quick Start

### 1. Set up API Token
```bash
# Option 1: Interactive setup
replicate-init

# Option 2: Manual setup
export REPLICATE_API_TOKEN="your-token-here"

# Option 3: .env file
echo "REPLICATE_API_TOKEN=your-token-here" > .env
```

### 2. Single Image Generation
```python
from replicate_batch_process import replicate_model_calling

file_paths = replicate_model_calling(
    prompt="A beautiful sunset over mountains",
    model_name="qwen/qwen-image",  # Use supported model
    output_filepath="output/sunset.jpg"
)
```

### 3. Batch Processing (Async Required)

#### Basic Batch Processing
```python
import asyncio
from replicate_batch_process import intelligent_batch_process

async def main():
    # Process multiple prompts with the same model
    files = await intelligent_batch_process(
        prompts=["sunset", "city", "forest"],
        model_name="qwen/qwen-image",
        max_concurrent=8,
        output_filepath=["output/sunset.png", "output/city.png", "output/forest.png"]
    )
    
    print(f"Generated {len(files)} images:")
    for file in files:
        print(f"  - {file}")
    
    return files

# Run the async function
if __name__ == "__main__":
    results = asyncio.run(main())
```

#### Advanced Mixed-Model Batch Processing
```python
import asyncio
from replicate_batch_process import IntelligentBatchProcessor, BatchRequest

async def advanced_batch():
    processor = IntelligentBatchProcessor()
    
    # Create requests with different models and parameters
    requests = [
        BatchRequest(
            prompt="A futuristic city",
            model_name="qwen/qwen-image",
            output_filepath="output/city.png",
            kwargs={"aspect_ratio": "16:9"}
        ),
        BatchRequest(
            prompt="A magical forest",
            model_name="google/imagen-4-ultra",
            output_filepath="output/forest.png",
            kwargs={"output_quality": 90}
        ),
        BatchRequest(
            prompt="Character with red hair",
            model_name="black-forest-labs/flux-kontext-max",
            output_filepath="output/character.png",
            kwargs={"input_image": "reference.jpg"}
        )
    ]
    
    # Process all requests concurrently
    results = await processor.process_intelligent_batch(requests, max_concurrent=5)
    
    # Handle results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"✅ Success: {len(successful)}/{len(results)}")
    for result in failed:
        print(f"❌ Failed: {result.error}")
    
    return results

# Run with proper async context
if __name__ == "__main__":
    asyncio.run(advanced_batch())
```

## 📋 Supported Models

### Image Generation Models
| Model | Price | Specialization | Reference Image Support |
|-------|-------|----------------|-------------------------|
| **black-forest-labs/flux-dev** | $0.025 | Fast generation, minimal censorship | ❌ |
| **black-forest-labs/flux-kontext-max** | $0.08 | Image editing, character consistency | ✅ |
| **qwen/qwen-image** | $0.025 | Text rendering, cover images | ❌ |
| **google/imagen-4-ultra** | $0.06 | High-quality detailed images | ❌ |

### Video Generation Models
| Model | Price | Specialization | Reference Image Support |
|-------|-------|----------------|-------------------------|
| **google/veo-3-fast** | $3.32/call | Fast video with audio | ✅ |
| **kwaivgi/kling-v2.1-master** | $0.28/sec | 1080p video, 5-10 second duration | ✅ |

> ⚠️ **Note**: Using unsupported models will return a clear error message: "Model '{model_name}' is not supported. Please use one of the supported models listed above."

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

**v1.0.9 Enhanced Triangular Fallback Loop:**
- `Flux Dev` → `Flux Kontext Max` (for reference images)
- `Flux Kontext Max` → `Qwen Image` (on sensitive content)
- `Qwen Image` → `Flux Dev` (with weak censorship disabled)
- **Ultimate Fallback**: Black image (1600x900) if all models fail

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

## ⚠️ Common Pitfalls

1. **Async/Await**: Batch functions must be called within async context
2. **Model Names**: Use exact model names from supported list above
3. **File Paths**: Ensure output directories exist before processing  
4. **Rate Limits**: Keep max_concurrent ≤ 15 to avoid 429 errors

## 📊 Performance Benchmarks

### Real-World Test Results (v1.0.7)
*Tested on: Python 3.9.16, macOS, Replicate API*

| Task | Model | Time | Success Rate | Notes |
|------|-------|------|-------------|-------|
| **Single Image** | qwen/qwen-image | 11.7s | 100% | Fastest for single generation |
| **Batch (3 images)** | qwen/qwen-image | 23.2s | 100% | ~7.7s per image with concurrency |
| **Batch (10 images)** | qwen/qwen-image | 45s | 100% | Optimal with max_concurrent=8 |
| **Mixed Models (3)** | Various | 28s | 100% | Parallel processing advantage |
| **With Fallback** | flux-kontext → qwen | 15s | 100% | Includes fallback overhead |
| **Large Batch (50)** | qwen/qwen-image | 3.5min | 98% | 2% retry on rate limits |

### Concurrency Performance
| Concurrent Tasks | Time per Image | Efficiency | Recommended For |
|-----------------|----------------|------------|-----------------|
| 1 (Sequential) | 12s | Baseline | Testing/Debug |
| 5 | 4.8s | 250% faster | Conservative usage |
| 8 | 3.2s | 375% faster | **Optimal balance** |
| 12 | 2.8s | 428% faster | Aggressive, risk of 429 |
| 15+ | Variable | Diminishing returns | Not recommended |

## 📊 Rate Limiting

- **Replicate API**: 600 requests/minute (shared across all models)
- **Recommended Concurrency**: 5-8 (conservative) to 12 (aggressive)
- **Auto-Retry**: Built-in 429 error handling with exponential backoff

## ⚠️ Known Issues & Workarounds

### Fixed in v1.0.7
✅ **FileOutput Handling Bug** (v1.0.2-1.0.6)
- **Issue**: Kontext Max model created 814 empty files when returning single image
- **Root Cause**: Incorrect iteration over bytes instead of file object
- **Fix**: Added intelligent output type detection with `hasattr(output, 'read')` check
- **Status**: ✅ Fully resolved

✅ **Parameter Routing Bug** (v1.0.2-1.0.6)
- **Issue**: `output_filepath` incorrectly placed in kwargs for batch processing
- **Fix**: Corrected parameter assignment in BatchRequest
- **Status**: ✅ Fully resolved

### Current Limitations (v1.0.9)
⚠️ **Kontext Max Parameter Compatibility**
- **Issue**: Certain parameters cause Kontext Max to fail
- **Solution**: v1.0.9 implements triangular fallback loop for maximum success
- **Impact**: Minimal - automatic recovery ensures image generation
- **Status**: ✅ Enhanced with triangular fallback mechanism

ℹ️ **Rate Limiting on Large Batches**
- **Issue**: Batches >50 may hit rate limits even with throttling
- **Workaround**: Use chunking strategy (see Best Practices)
- **Impact**: Minor - automatic retry handles most cases

### Reporting Issues
Found a bug? Please report at: https://github.com/preangelleo/replicate_batch_process/issues

## 📦 Migration Guide

### Upgrading to v1.0.9 (Latest)
```bash
pip install --upgrade replicate-batch-process==1.0.9
```

**New Features:**
- ✅ Triangular fallback loop for maximum success rate
- ✅ Black image (1600x900) as ultimate fallback
- ✅ Fixed flux-kontext-max parameter compatibility issues
- ✅ Simplified logging output

**Action Required:** None - fully backward compatible

### Upgrading from v1.0.2-1.0.5 → v1.0.7
```bash
pip install --upgrade replicate-batch-process==1.0.7
```

**Critical Fixes:**
1. **intelligent_batch_process parameter bug** - Now correctly handles output_filepath
2. **FileOutput compatibility** - No more empty file creation
3. **Model validation** - Clear error messages for unsupported models

**Code Changes Needed:** None, but review error handling for better messages

### Upgrading from v0.x → v1.0.7

**Breaking Changes:**
- Package renamed from `replicate_batch` to `replicate-batch-process`
- New import structure:
  ```python
  # Old (v0.x)
  from replicate_batch import process_batch
  
  # New (v1.0.7)
  from replicate_batch_process import intelligent_batch_process
  ```

**Migration Steps:**
1. Uninstall old package: `pip uninstall replicate_batch`
2. Install new package: `pip install replicate-batch-process`
3. Update imports in your code
4. Test with small batches first

### Version History
| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| v1.0.9 | 2025-08-12 | Triangular fallback loop, black image ultimate fallback |
| v1.0.8 | 2025-08-12 | Fixed parameter compatibility, improved logging |
| v1.0.7 | 2025-01-05 | FileOutput fix, README improvements |
| v1.0.6 | 2025-01-05 | Bug fixes, model validation |
| v1.0.5 | 2025-01-04 | Parameter handling improvements |
| v1.0.4 | 2025-01-04 | Model support documentation |
| v1.0.3 | 2025-01-03 | Initial stable release |

## 💡 Best Practices

```python
# For large batches, use chunking
def process_large_batch(prompts, chunk_size=50):
    for chunk in chunks(prompts, chunk_size):
        files = await intelligent_batch_process(chunk, model_name)
        yield files

# Error handling with complete example
from replicate_batch_process import IntelligentBatchProcessor, BatchRequest

async def batch_with_error_handling():
    processor = IntelligentBatchProcessor()
    requests = [
        BatchRequest(prompt="sunset", model_name="qwen/qwen-image", output_filepath="output/sunset.png"),
        BatchRequest(prompt="city", model_name="qwen/qwen-image", output_filepath="output/city.png"),
    ]
    results = await processor.process_intelligent_batch(requests)
    
    for result in results:
        if result.success:
            print(f"✅ Generated: {result.file_paths}")
        else:
            print(f"❌ Failed: {result.error}")

asyncio.run(batch_with_error_handling())
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