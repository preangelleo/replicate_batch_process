# Replicate 批量处理工具

**中文** | **[English README](README.md)** | **[PyPI 包](https://pypi.org/project/replicate-batch-process/)**

[![PyPI version](https://badge.fury.io/py/replicate-batch-process.svg)](https://badge.fury.io/py/replicate-batch-process)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

智能批量处理 Replicate 模型工具，具备**自动Fallback机制**和并发处理能力。

## ✨ 核心特性

- 🔄 **智能Fallback系统** - 模型不兼容时自动切换
- ⚡ **智能并发控制** - 自适应速率限制和批处理
- 🎯 **三种使用模式** - 单个、批量同模型、混合模型处理
- 📝 **自定义文件命名** - 有序输出，内容对应可控
- 🛡️ **错误恢复机制** - 全面的重试和恢复机制

## 📦 安装

```bash
pip install replicate-batch-process
```

## 🚀 快速开始

### 1. 环境初始化
```bash
# 设置API密钥（仅首次需要）
replicate-init
```

### 2. 单个图像生成
```python
from replicate_batch_process import replicate_model_calling

file_paths = replicate_model_calling(
    prompt="山峦上的美丽日落",
    model_name="black-forest-labs/flux-dev",
    output_filepath="output/sunset.jpg"
)
```

### 3. 批量处理
```python
import asyncio
from replicate_batch_process import intelligent_batch_process

files = await intelligent_batch_process(
    prompts=["日落", "城市", "森林"],
    model_name="black-forest-labs/flux-dev",
    max_concurrent=8
)
```

## 🔄 智能Fallback系统

**遇到问题时自动切换模型：**

### 参考图像自动检测
```python
# 用户给不支持参考图像的模型传入图像
replicate_model_calling(
    prompt="根据这张图片生成",
    model_name="black-forest-labs/flux-dev",  # 不支持参考图像
    input_image="path/to/image.jpg"           # → 自动切换到flux-kontext-max
)
```

### 参数兼容性处理
```python
# 不支持的参数自动清理并切换模型
replicate_model_calling(
    prompt="生成图片",
    model_name="black-forest-labs/flux-kontext-max",
    guidance=3.5,        # 不支持的参数
    num_outputs=2        # → 自动切换到兼容模型
)
```

### API错误恢复
自动fallback链：`Flux Dev` → `Qwen Image` → `Imagen 4 Ultra`

## 📋 使用场景

| 模式 | 使用场景 | 命令 |
|------|----------|------|
| **单个** | 一次性生成、测试 | `replicate_model_calling()` |
| **批量同模型** | 多提示词，同模型 | `intelligent_batch_process()` |
| **混合模型** | 不同模型/参数 | `IntelligentBatchProcessor()` |

## 🧠 智能处理策略

系统自动选择最优处理策略：

- **立即处理**：任务数 ≤ 可用配额 → 全并发处理
- **窗口处理**：任务数 ≤ 600 但 > 当前配额 → 等待后批处理
- **动态队列**：任务数 > 600 → 队列管理持续处理

## ⚙️ 配置

### API密钥
获取你的Replicate API token：[replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)

### 自定义Fallback规则
修改 `config.py`：
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

## 📊 速率限制

- **Replicate API**：600请求/分钟（所有模型共享）
- **推荐并发数**：5-8（保守）到12（激进）
- **自动重试**：内置429错误处理，指数退避

## 💡 最佳实践

```python
# 大批量处理使用分块
def process_large_batch(prompts, chunk_size=50):
    for chunk in chunks(prompts, chunk_size):
        files = await intelligent_batch_process(chunk, model_name)
        yield files

# 错误处理
for result in results:
    if result.success:
        print(f"✅ 生成成功：{result.file_paths}")
    else:
        print(f"❌ 失败：{result.error}")
```

## 🏗️ 项目结构

```
replicate-batch-process/
├── main.py                      # 单个图像生成
├── intelligent_batch_processor.py  # 批处理引擎
├── config.py                    # 模型配置和fallback
├── init_environment.py          # 环境设置
└── example_usage.py            # 完整示例
```

## 🔧 开发

```bash
# 克隆仓库
git clone https://github.com/preangelleo/replicate_batch_process.git

# 开发模式安装
pip install -e .

# 运行示例
python example_usage.py
```

## 📄 许可证

MIT许可证 - 详见[LICENSE](LICENSE)文件

## 🤝 贡献

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 🔗 链接

- **PyPI**: https://pypi.org/project/replicate-batch-process/
- **GitHub**: https://github.com/preangelleo/replicate_batch_process
- **Issues**: https://github.com/preangelleo/replicate_batch_process/issues

---

**为AI社区用❤️制作**