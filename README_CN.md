# Replicate 模型调用工具 - 完整使用指南

## 🚀 概述

这个工具提供了三种方式调用 Replicate 模型，从单个图像生成到大规模批量处理：

1. **单个图像生成** - 直接调用，适合测试和单次使用
2. **简单批量处理** - 便捷接口，适合相同参数的批量生成
3. **高级批量处理** - 灵活配置，适合混合模型和复杂需求

## 🔄 智能Fallback机制 - 核心特色

**自动模型切换，无需担心兼容性！**

我们的系统能够智能检测模型兼容性问题，并自动切换到最佳替代模型：

### 三种Fallback触发条件：

1. **Reference Image自动切换**
   ```python
   # 用户给不支持图片的模型传入reference image
   replicate_model_calling(
       prompt="Generate based on this image", 
       model_name="black-forest-labs/flux-dev",  # 不支持reference image
       input_image="path/to/image.jpg"           # 系统自动切换到flux-kontext-max
   )
   ```

2. **参数不兼容自动处理**
   ```python
   # 用户传入不支持的参数，系统自动清理并切换
   replicate_model_calling(
       prompt="Generate image",
       model_name="black-forest-labs/flux-kontext-max",
       guidance=3.5,        # 不支持的参数
       num_outputs=2        # 自动切换到支持的模型
   )
   ```

3. **API错误自动重试**
   ```python
   # 如果主模型调用失败，自动尝试备用模型
   # Flux Dev -> Qwen Image -> Imagen 4 Ultra
   ```

### 🛠️ 自定义Fallback配置

如果你有特定的模型偏好，可以修改fallback规则：

**修改位置**: `config.py` 文件中的 `FALLBACK_MODELS` 和 `FALLBACK_PARAMETER_MAPPING`

**示例修改**：
```python
# 在 config.py 中自定义fallback
FALLBACK_MODELS = {
    'your-preferred-model': {
        'fail': {
            'fallback_model': 'your-backup-model',
            'condition': 'api_error',
            'description': '自定义fallback描述'
        }
    }
}
```

## 📦 文件结构

```
replicate_model_call/
├── setup.py                     # 环境初始化脚本 🚀
├── main.py                      # 单个图像生成核心函数
├── config.py                    # 模型配置
├── intelligent_batch_processor.py  # 智能批处理器
├── example_usage.py            # 三种场景的完整使用示例 ⭐
├── .env                         # API密钥配置（首次运行后生成）
├── .gitignore                   # Git忽略规则（自动创建/更新）
├── output/                      # 输出目录（自动创建）
└── README.md                   # 本文档
```

## 🎯 三种使用方式

### 方式1: 单个图像生成

**适用场景**: 单次生成、测试模型、交互式使用

```python
# 详细示例请查看 example_usage.py 中的 SINGLE_IMAGE_PARAMS

from main import replicate_model_calling

# 核心调用代码
file_paths = replicate_model_calling(
    prompt="A beautiful sunset over mountains",
    model_name="black-forest-labs/flux-dev",
    output_filepath="output/my_image.jpg",
    aspect_ratio="16:9",
    output_quality=80
)

print(f"生成的文件: {file_paths[0]}")
```

**特点**:
- ✅ 简单直接，无需额外设置
- ✅ 立即返回结果
- ✅ 支持所有模型参数自定义
- ✅ 每完成一个图像立即下载保存

### 方式2: 简单批量处理

**适用场景**: 相同模型、相同参数的批量生成

```python
# 详细示例请查看 example_usage.py 中的 BATCH_SAME_MODEL_PARAMS

import asyncio
from intelligent_batch_processor import intelligent_batch_process

# 核心调用代码
files = await intelligent_batch_process(
    prompts=["sunset", "city", "robot", "forest"],  # 提示词列表
    model_name="black-forest-labs/flux-dev",
    max_concurrent=8,
    output_filepath=["output/scene_01_sunset.jpg", "output/scene_02_city.jpg", 
                     "output/scene_03_robot.jpg", "output/scene_04_forest.jpg"],  # 可选: 自定义文件路径
    aspect_ratio="16:9",
    output_quality=90
)

print(f"生成了 {len(files)} 个文件")
```

**特点**:
- 🚀 **智能策略选择** - 自动选择最优处理方式
- ⚡ **即时下载** - 每完成一个任务立即下载
- 📊 **进度监控** - 实时显示处理进度
- 🔄 **自动重试** - 智能处理429错误
- 📝 **自定义文件路径** - 支持自定义输出文件路径，确保文件与内容对应
- 🔄 **智能Fallback机制** - 自动检测兼容性并切换最佳模型

### 方式3: 高级批量处理

**适用场景**: 混合模型、不同参数、复杂批处理需求

```python
# 详细示例请查看 example_usage.py 中的 MIXED_MODEL_REQUESTS

import asyncio
from intelligent_batch_processor import IntelligentBatchProcessor, BatchRequest

# 核心调用代码
requests = [
    BatchRequest(
        prompt="High quality portrait photo",
        model_name="google/imagen-4-ultra",
        kwargs={"aspect_ratio": "4:3", "output_quality": 95}
    ),
    BatchRequest(
        prompt="Anime style character", 
        model_name="black-forest-labs/flux-dev",
        kwargs={"aspect_ratio": "1:1", "guidance": 4}
    ),
]

processor = IntelligentBatchProcessor(max_concurrent=15, max_retries=3)
results = await processor.process_intelligent_batch(requests)

# 处理结果
for result in results:
    if result.success:
        print(f"✅ 成功: {result.file_paths}")
    else:
        print(f"❌ 失败: {result.error}")
```

**特点**:
- 🧠 **智能策略选择** - 根据任务量自动选择处理策略
- 🔀 **混合模型支持** - 同时使用多种不同模型
- ⚙️ **精细控制** - 每个请求独立配置参数
- 📈 **详细统计** - 完整的成功/失败统计信息

## 🚀 环境初始化（首次使用必须）

### **第一步**: 运行初始化脚本

```bash
# 自动检查和设置API密钥
python setup.py
```

初始化脚本会：
- ✅ 检查 `.env` 文件和API密钥
- 🔑 提示输入缺失的API密钥
- 💾 自动创建和配置 `.env` 文件
- 📁 创建必要的目录结构
- 🔒 设置安全的文件权限
- 🧪 测试API连接

### **API密钥获取**:
- **Replicate API Token**: 访问 [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)

## 🎯 快速开始

### **推荐方式**: 使用 `example_usage.py`

```bash
# 1. 交互式选择运行哪个示例
python example_usage.py

# 2. 运行所有三个示例
python example_usage.py all

# 3. 在你的代码中导入使用
from example_usage import single_image_generation, batch_same_model, advanced_mixed_models
```

### **Vibe Coder 友好**: 复制即用的格式

1. **修改参数配置** - 在文件顶部修改 `PARAMS` 变量
2. **复制核心代码** - 找到 🚀 标记的核心调用代码
3. **直接使用** - 粘贴到你的项目中即可

## 🧠 智能批处理策略

批处理器会根据任务量自动选择最优策略：

### 策略1: 立即全部处理
**条件**: 任务数 ≤ 当前可用配额
```
✅ 12个任务，当前配额450 → 立即并发处理所有任务
```

### 策略2: 单窗口批处理  
**条件**: 任务数 ≤ 窗口配额(600)，但大于当前配额
```
⏳ 450个任务，当前配额200 → 等待配额足够后批量处理
```

### 策略3: 动态队列处理
**条件**: 任务数 > 窗口配额(600)
```
🔄 1200个任务 → 分批动态处理，完成一个补充一个
```

## 🎯 使用场景对比

| 使用方式 | 任务数量 | 配置复杂度 | 推荐场景 |
|---------|---------|-----------|----------|
| **单个图像** | 1 | 简单 | 测试、演示、单次生成 |
| **简单批量** | 2-50 | 中等 | 相同参数的批量生成 |
| **高级批量** | 10-1000+ | 高 | 混合模型、复杂需求 |

## 📊 速率限制和并发控制

### Replicate API 限制
- **创建预测**: 600 requests/分钟 (所有模型共享)
- **超出限制**: 返回 429 错误

### 安全并发建议
```python
# 保守设置 (推荐新手)
max_concurrent = 5

# 平衡设置 (推荐大多数用户) 
max_concurrent = 8

# 激进设置 (需要良好重试机制)
max_concurrent = 12
```

## 🔄 JSON数据批处理示例

如果你有结构化的JSON数据，可以使用测试脚本：

```bash
# 运行JSON批处理测试
python json_batch_test.py
```

这会演示如何从JSON数据中提取图像描述并批量生成。

## 💡 最佳实践

### 1. 选择合适的方式
```python
# 单个图像 - 直接调用main
if len(prompts) == 1:
    result = replicate_model_calling(prompt, model_name)

# 批量相同参数 - 简单接口  
elif all_same_params:
    files = await intelligent_batch_process(prompts, model_name)

# 复杂需求 - 高级接口
else:
    processor = IntelligentBatchProcessor()
    results = await processor.process_intelligent_batch(requests)
```

### 2. 错误处理
```python
# 检查批处理结果
successful_files = []
failed_count = 0

for result in results:
    if result.success:
        successful_files.extend(result.file_paths)
    else:
        failed_count += 1
        print(f"失败: {result.error}")

print(f"成功: {len(successful_files)}, 失败: {failed_count}")
```

### 3. 输出管理
```python
import time
import os

# 使用时间戳避免文件冲突
timestamp = int(time.time())
output_dir = f"output/batch_{timestamp}"
os.makedirs(output_dir, exist_ok=True)
```

### 4. 大批量处理
```python
# 分批处理大量任务
def chunk_prompts(prompts, chunk_size=50):
    for i in range(0, len(prompts), chunk_size):
        yield prompts[i:i + chunk_size]

all_files = []
for batch in chunk_prompts(huge_prompt_list, 50):
    files = await intelligent_batch_process(batch, model_name)
    all_files.extend(files)
```

## 🚨 重要注意事项

1. **API配额共享**: 所有模型调用都共享600/分钟限制
2. **即时下载**: 每个任务完成后立即下载，不会等待全部完成
3. **并发控制**: 建议从较低并发数开始，逐步调整
4. **成本控制**: 批量处理会快速消耗API配额，注意成本
5. **存储空间**: 确保有足够磁盘空间存储生成的文件

## 🔧 故障排除

### 常见问题解决

1. **429错误** (速率限制)
   ```python
   # 降低并发数
   max_concurrent = 5  # 从8降到5
   ```

2. **导入错误**
   ```python
   # 确保在正确目录
   import sys
   sys.path.append('/path/to/replicate_model_call')
   ```

3. **文件路径问题**
   ```python
   # 使用绝对路径
   import os
   output_dir = os.path.abspath("output/my_batch")
   ```

## 🎯 完整使用流程

```bash
# 1️⃣ 首次使用 - 环境初始化
python setup.py

# 2️⃣ 运行示例
python example_usage.py

# 3️⃣ 或在你的代码中使用
python your_script.py
```

## 🚀 快速开始模板

```python
# 🚀 方式1: 查看完整示例
python example_usage.py

# 🚀 方式2: 直接复制使用
from example_usage import BATCH_SAME_MODEL_PARAMS
from intelligent_batch_processor import intelligent_batch_process
import asyncio

# 修改参数配置
BATCH_SAME_MODEL_PARAMS["prompts"] = ["你的提示词1", "你的提示词2"]
BATCH_SAME_MODEL_PARAMS["model_name"] = "black-forest-labs/flux-dev"

# 核心调用
files = asyncio.run(intelligent_batch_process(
    prompts=BATCH_SAME_MODEL_PARAMS["prompts"],
    model_name=BATCH_SAME_MODEL_PARAMS["model_name"],
    max_concurrent=BATCH_SAME_MODEL_PARAMS["max_concurrent"]
))

print(f"✅ 生成完成! 共 {len(files)} 个文件")
```

现在你已经掌握了从单个图像到大规模批处理的完整工具链! 🚀

**推荐**: 直接使用 `example_usage.py` - 经过测试、标准化、Vibe Coder友好！