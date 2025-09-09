# 🌐 Global Concurrency Control Upgrade
Global Concurrency Control Upgrade Documentation

## 📋 Upgrade Overview

This upgrade adds global account-level concurrency control to the `replicate_batch_process` project, ensuring that multiple batch processing instances do not exceed the Replicate API account concurrency limits.

### 🔑 Core Features

1. **Global Account-Level Concurrency Control** - All batch processing instances share the same global semaphore
2. **Environment Variable Priority System** - Supports payload > .env > error priority hierarchy
3. **Singleton Global Manager** - Ensures all instances use the same global state
4. **Dual Concurrency Control** - Maintains local concurrency control + adds global concurrency control
5. **Backward Compatibility** - Existing code works without modifications

## 🚀 Usage

### Method 1: Environment Variables (Recommended)

```bash
# Set environment variables
export REPLICATE_API_TOKEN="r8_your_token_here"
export REPLICATE_GLOBAL_MAX_CONCURRENT=60

# Use in Python code
await intelligent_batch_process(
    prompts=["beautiful sunset", "mountain landscape"],
    model_name="black-forest-labs/flux-dev",
    max_concurrent=5  # Local concurrency limit
)
```

### Method 2: Parameter Passing (Highest Priority)

```python
await intelligent_batch_process(
    prompts=["beautiful sunset", "mountain landscape"],
    model_name="black-forest-labs/flux-dev",
    max_concurrent=5,  # Local concurrency limit
    replicate_api_token="r8_your_token_here",  # Highest priority
    global_max_concurrent=60  # Global concurrency limit, highest priority
)
```

### Method 3: Direct Processor Class Usage

```python
from replicate_batch_process.intelligent_batch_processor import IntelligentBatchProcessor

# Create processor with global concurrency control
processor = IntelligentBatchProcessor(
    max_concurrent=8,  # Local concurrency
    replicate_api_token="r8_your_token_here",
    global_max_concurrent=60  # Global concurrency
)

# Process batch
results = await processor.process_intelligent_batch(requests)
```

## 🏗️ Technical Architecture

### Core Components

1. **GlobalReplicateConcurrencyManager** (`global_concurrency_manager.py`)
   - Singleton pattern global manager
   - Environment variable priority system
   - Global semaphore management
   - Statistics and monitoring

2. **IntelligentBatchProcessor** Upgrade
   - Integrated global concurrency manager
   - Dual concurrency control (local + global)
   - Backward-compatible constructor

3. **Convenience Function Upgrade**
   - `intelligent_batch_process()` supports global concurrency parameters
   - Automatic global manager initialization

### Concurrency Control Flow

```
Request → Local Semaphore Acquire → Global Semaphore Acquire → API Call → Release Global Semaphore → Release Local Semaphore
```

### Priority System

```
Payload Parameters > Environment Variables > Default Values/Error
```

## 📊 Performance Characteristics

### Dual Concurrency Control

- **Local Concurrency**: Per-batch-processing-instance concurrency limit
- **Global Concurrency**: Account-level limit shared across all instances

### Example Scenario

```
Scenario: 3 batch processing instances running simultaneously
- Instance A: max_concurrent=5
- Instance B: max_concurrent=8  
- Instance C: max_concurrent=6
- Global limit: global_max_concurrent=10

Result: 
- At any moment, maximum 10 API requests are running (global limit)
- Each instance still respects its own local concurrency limit
```

## 🧪 Testing and Validation

Run the test script to verify functionality:

```bash
cd /path/to/replicate_batch_process
python test_global_concurrency.py
```

### Test Coverage

1. **Global Concurrency Manager Basic Functionality**
   - Semaphore acquire/release
   - Concurrency control verification
   - Statistics tracking

2. **Singleton Pattern Behavior Verification**
   - Instance sharing verification
   - Global state consistency

3. **Batch Processing Integration Test**
   - Parameter passing verification
   - Global concurrency control integration

4. **Multi-Instance Sharing Test**
   - Global state sharing verification
   - Singleton pattern verification

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REPLICATE_API_TOKEN` | API Token | Required | `r8_xxx...` |
| `REPLICATE_GLOBAL_MAX_CONCURRENT` | Global max concurrent | 60 | `80` |

### Function Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `replicate_api_token` | `Optional[str]` | API Token (highest priority) | `None` |
| `global_max_concurrent` | `Optional[int]` | Global concurrency limit (highest priority) | `None` |

## 💡 Best Practices

### 1. Production Environment Configuration

```bash
# Production - Use environment variables
export REPLICATE_API_TOKEN="r8_production_token"
export REPLICATE_GLOBAL_MAX_CONCURRENT=80
```

### 2. Development Environment Configuration

```python
# Development - Use parameter passing
await intelligent_batch_process(
    prompts=test_prompts,
    model_name="black-forest-labs/flux-dev",
    replicate_api_token="r8_development_token",
    global_max_concurrent=30  # Use smaller value during development
)
```

### 3. Concurrency Settings Recommendations

- **Global Concurrency**: Set based on Replicate account limits (typically 30-80, recommended 60 based on 600 requests/minute)
- **Local Concurrency**: Set based on task complexity and resources (typically 8-20)
- **Relationship**: `local_concurrent <= global_concurrent` (e.g., local=20, global=60)

### 4. Monitoring and Debugging

```python
from replicate_batch_process.global_concurrency_manager import get_global_status

# Get global status
status = get_global_status()
print(f"Global concurrency status: {status}")
```

## 🔒 Security Considerations

1. **API Token Security**
   - Prefer environment variables for storing API tokens
   - Avoid hardcoding sensitive information in code

2. **Concurrency Limits**
   - Set reasonable global concurrency limits to avoid triggering API limits
   - Monitor API usage to avoid exceeding quotas

## 🔄 Migration Guide

### Existing Code Migration

**No code changes required!** The new version is fully backward compatible.

To use global concurrency control, simply:

1. Set environment variables or pass parameters
2. Enjoy automatic global concurrency control

### Upgrade Steps

1. Update code to new version
2. Set `REPLICATE_API_TOKEN` environment variable
3. Optional: Set `REPLICATE_GLOBAL_MAX_CONCURRENT` environment variable
4. Test and verify functionality

## 🐛 Troubleshooting

### Common Issues

1. **Understanding Singleton Pattern**
   ```
   Q: Why doesn't the configuration update when creating a second manager?
   A: Singleton pattern ensures global state consistency - this is expected behavior.
   ```

2. **Concurrency Control Not Working**
   ```
   Q: Why doesn't concurrency seem to be limited?
   A: Check if global_max_concurrent parameter is properly set.
   ```

3. **API Token Issues**
   ```
   Q: Getting 401 Unauthenticated error?
   A: Check if REPLICATE_API_TOKEN is correctly set.
   ```

### Debugging Methods

1. **Check Global Status**
   ```python
   from replicate_batch_process.global_concurrency_manager import get_global_status
   print(get_global_status())
   ```

2. **Check Environment Variables**
   ```python
   import os
   print(f"API Token: {os.getenv('REPLICATE_API_TOKEN', 'Not Set')}")
   print(f"Global Concurrent: {os.getenv('REPLICATE_GLOBAL_MAX_CONCURRENT', 'Not Set')}")
   ```

## 📈 Version Information

- **Upgrade Version**: v2.0 (Global Concurrency Control)
- **Compatibility**: Fully backward compatible with v1.x
- **New Files**: `global_concurrency_manager.py`
- **Modified Files**: `intelligent_batch_processor.py`

## 🎯 Summary

This upgrade successfully implements:

✅ **Global Account-Level Concurrency Control** - Prevents exceeding Replicate API limits  
✅ **Environment Variable Priority System** - Flexible configuration management  
✅ **Singleton Global Management** - Ensures multi-instance state consistency  
✅ **Full Backward Compatibility** - No changes required to existing code  
✅ **Comprehensive Test Coverage** - Ensures functionality stability  

Now you can safely generate images across multiple batch processing instances without worrying about exceeding your account's concurrency limits! 🎉