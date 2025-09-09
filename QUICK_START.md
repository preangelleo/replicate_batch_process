# 🚀 Quick Start - Global Concurrency Control
Quick Start Guide for Global Concurrency Control

## 🎯 5-Minute Setup Guide

### Step 1: Set Environment Variables

```bash
# Set your Replicate API Token
export REPLICATE_API_TOKEN="r8_your_actual_token_here"

# Set global max concurrent (optional, defaults to 10)
export REPLICATE_GLOBAL_MAX_CONCURRENT=60
```

### Step 2: Basic Usage

```python
import asyncio
from replicate_batch_process.intelligent_batch_processor import intelligent_batch_process

async def generate_images():
    prompts = [
        "Beautiful sunset over mountains",
        "Peaceful lake with reflections", 
        "Modern city skyline at night"
    ]
    
    # Automatically uses global concurrency control
    files = await intelligent_batch_process(
        prompts=prompts,
        model_name="black-forest-labs/flux-dev",
        max_concurrent=5  # Local concurrency limit
    )
    
    print(f"Generated {len(files)} image files!")
    return files

# Run
asyncio.run(generate_images())
```

### Step 3: Advanced Configuration (Optional)

```python
# Use parameter passing (highest priority)
files = await intelligent_batch_process(
    prompts=prompts,
    model_name="black-forest-labs/flux-dev",
    max_concurrent=5,
    replicate_api_token="r8_your_token",  # Higher priority than environment variables
    global_max_concurrent=20,  # Global concurrency limit
    output_dir="my_output_folder"
)
```

## 🎛️ Key Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `max_concurrent` | Local concurrency limit | 8 | 5 |
| `global_max_concurrent` | Global concurrency limit | 10 | 15 |
| `replicate_api_token` | API token | Environment variable | "r8_xxx" |

## 💡 Best Practices

### ✅ Recommended Practices

```python
# 1. Use environment variables for sensitive information
export REPLICATE_API_TOKEN="your_token"

# 2. Set reasonable concurrency numbers
local_concurrent = 5    # Per-instance concurrency
global_concurrent = 15  # Account-wide concurrency limit

# 3. Specify output directory
await intelligent_batch_process(
    prompts=prompts,
    model_name="flux-dev",
    output_dir="output/my_project"
)
```

### ❌ Things to Avoid

```python
# Don't hardcode API tokens in code
api_token = "r8_hardcoded_token"  # ❌

# Don't set excessively high concurrency
global_max_concurrent = 150  # ❌ May trigger API limits

# Don't ignore output directory management
# All files mixed together ❌
```

## 🔍 Monitoring and Debugging

### Check Global Status

```python
from replicate_batch_process.global_concurrency_manager import get_global_status

# Get real-time status
status = get_global_status()
print(f"Current concurrent: {status['current_concurrent']}/{status['global_max_concurrent']}")
print(f"Utilization: {status['utilization_percentage']:.1f}%")
```

### Common Issue Diagnosis

```python
import os

# Check environment variables
print(f"API Token: {os.getenv('REPLICATE_API_TOKEN', 'Not Set')}")
print(f"Global Concurrent: {os.getenv('REPLICATE_GLOBAL_MAX_CONCURRENT', 'Not Set')}")
```

## 🏃‍♂️ Run Examples

```bash
# Download and run examples
cd replicate_batch_process
python example_global_concurrency.py
```

## 🆘 Having Issues?

1. **401 Authentication Error**: Check if `REPLICATE_API_TOKEN` is correctly set
2. **Concurrency Not Working**: Confirm `global_max_concurrent` parameter is set
3. **File Generation Failed**: Check output directory permissions and disk space

## 📚 More Resources

- 📖 [Complete Upgrade Documentation](GLOBAL_CONCURRENCY_UPGRADE.md)
- 🧪 [Test Script](test_global_concurrency.py) 
- 💡 [Usage Examples](example_global_concurrency.py)

---

**🎉 Congratulations! You can now safely perform large-scale image batch processing!**