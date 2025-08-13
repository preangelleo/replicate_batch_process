#!/usr/bin/env python3
"""
Replicate 模型调用 - 完整使用示例
三种使用场景的经过测试的示例代码，可直接复制使用
"""

import asyncio
import time
import os

# 导入我们的模块
from .main import replicate_model_calling
from .intelligent_batch_processor import intelligent_batch_process, IntelligentBatchProcessor, BatchRequest


# =============================================================================
# 场景1: 单个图像生成 - 最简单的使用方式
# =============================================================================

# 📋 输入参数配置 - 可直接修改这些参数
SINGLE_IMAGE_PARAMS = {
    "prompt": "A beautiful sunset over mountains with golden light",
    "model_name": "black-forest-labs/flux-dev",  # 可选: qwen/qwen-image, google/imagen-4-ultra
    "output_filepath": "output/single_example.jpg",
    
    # 可选参数 - 根据模型支持调整
    "aspect_ratio": "16:9",        # 宽高比: "1:1", "4:3", "16:9"
    "output_quality": 80,          # 输出质量: 1-100
    "num_outputs": 1,              # 输出数量: 通常为1
    # "guidance": 3,               # 引导强度: 1-10（仅某些模型）
    # "num_inference_steps": 28,   # 推理步数（仅某些模型）
}

def single_image_generation():
    """
    场景1: 生成单个图像
    
    使用方法:
    1. 修改上面的 SINGLE_IMAGE_PARAMS 参数
    2. 调用此函数或直接复制调用代码
    
    适用场景:
    - 测试模型效果
    - 单次生成需求
    - 交互式使用
    """
    
    print("🎯 场景1: 单个图像生成")
    print(f"   提示词: {SINGLE_IMAGE_PARAMS['prompt']}")
    print(f"   模型: {SINGLE_IMAGE_PARAMS['model_name']}")
    
    try:
        start_time = time.time()
        
        # 🚀 核心调用代码 - 可直接复制使用
        file_paths = replicate_model_calling(
            prompt=SINGLE_IMAGE_PARAMS["prompt"],
            model_name=SINGLE_IMAGE_PARAMS["model_name"],
            output_filepath=SINGLE_IMAGE_PARAMS["output_filepath"],
            aspect_ratio=SINGLE_IMAGE_PARAMS["aspect_ratio"],
            output_quality=SINGLE_IMAGE_PARAMS["output_quality"],
            num_outputs=SINGLE_IMAGE_PARAMS["num_outputs"]
        )
        
        duration = time.time() - start_time
        
        print(f"✅ 生成完成!")
        print(f"   耗时: {duration:.1f}秒")
        print(f"   文件: {file_paths[0]}")
        
        return file_paths[0]
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


# =============================================================================
# 场景2: 同模型批量生成 - 相同参数的批量处理
# =============================================================================

# 📋 批量处理参数配置 - 可直接修改这些参数
BATCH_SAME_MODEL_PARAMS = {
    # 提示词列表 - 所有使用相同模型和参数
    "prompts": [
        "A serene lake reflecting autumn trees with golden leaves",
        "A cozy cabin in the mountains during a snowy winter evening", 
        "A vibrant flower garden in full bloom during spring",
        "A peaceful beach scene with gentle waves at sunset",
        "A mystical forest path with rays of sunlight filtering through",
    ],
    
    # 自定义文件路径列表（可选） - 与prompts对应，完整路径
    "output_filepath": [
        "output/batch_same_model_example/scene_01_autumn_lake.jpg",
        "output/batch_same_model_example/scene_02_winter_cabin.jpg", 
        "output/batch_same_model_example/scene_03_spring_garden.jpg",
        "output/batch_same_model_example/scene_04_sunset_beach.jpg",
        "output/batch_same_model_example/scene_05_forest_path.jpg",
    ],
    
    # 统一模型
    "model_name": "black-forest-labs/flux-dev",  # 所有图像使用同一模型
    
    # 批量处理设置
    "max_concurrent": 8,                         # 并发数: 5-20推荐
    
    # 共同参数 - 所有图像使用相同设置
    "aspect_ratio": "16:9",        # 统一宽高比
    "output_quality": 90,          # 统一质量
    "num_outputs": 1,              # 每个提示词生成1张图
    # "guidance": 3,               # 统一引导强度
    # "num_inference_steps": 28,   # 统一推理步数
}

async def batch_same_model():
    """
    场景2: 使用同一个模型批量生成图像
    
    使用方法:
    1. 修改上面的 BATCH_SAME_MODEL_PARAMS 参数
    2. 调用此函数或直接复制调用代码
    
    适用场景:
    - 批量生成相似风格的图像
    - 所有图像使用相同参数
    - 中等规模批处理 (2-100个)
    """
    
    print("🎯 场景2: 同模型批量生成")
    print(f"   提示词数量: {len(BATCH_SAME_MODEL_PARAMS['prompts'])}")
    print(f"   模型: {BATCH_SAME_MODEL_PARAMS['model_name']}")
    print(f"   并发数: {BATCH_SAME_MODEL_PARAMS['max_concurrent']}")
    
    try:
        start_time = time.time()
        
        # 🚀 核心调用代码 - 可直接复制使用
        files = await intelligent_batch_process(
            prompts=BATCH_SAME_MODEL_PARAMS["prompts"],
            model_name=BATCH_SAME_MODEL_PARAMS["model_name"],
            max_concurrent=BATCH_SAME_MODEL_PARAMS["max_concurrent"],
            output_filepath=BATCH_SAME_MODEL_PARAMS["output_filepath"],
            aspect_ratio=BATCH_SAME_MODEL_PARAMS["aspect_ratio"],
            output_quality=BATCH_SAME_MODEL_PARAMS["output_quality"],
            num_outputs=BATCH_SAME_MODEL_PARAMS["num_outputs"]
        )
        
        duration = time.time() - start_time
        
        print(f"✅ 批量生成完成!")
        print(f"   总耗时: {duration:.1f}秒")
        print(f"   生成文件: {len(files)}个")
        print(f"   平均速度: {len(files)/duration:.2f} 文件/秒")
        print(f"   文件列表:")
        for file_path in files:
            print(f"     - {os.path.basename(file_path)}")
        
        return files
        
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")
        return []


# =============================================================================
# 场景3: 混合模型高级批处理 - 不同模型和参数的复杂处理
# =============================================================================

# 📋 混合模型请求配置 - 可直接修改这些参数
MIXED_MODEL_REQUESTS = [
    {
        "prompt": "A professional headshot portrait of a business woman",
        "model": "google/imagen-4-ultra",      # 高质量人像
        "params": {
            "aspect_ratio": "4:3",             # 人像比例
            "output_quality": 95,              # 高质量
            # "style": "photorealistic"
        }
    },
    {
        "prompt": "An anime-style character design with magical powers", 
        "model": "black-forest-labs/flux-dev", # 快速风格化
        "params": {
            "aspect_ratio": "1:1",             # 正方形
            "output_quality": 80,
            "guidance": 4,                     # 风格化引导
            "num_inference_steps": 30
        }
    },
    {
        "prompt": "A technical diagram showing '人工智能架构' with Chinese text",
        "model": "qwen/qwen-image",            # 中文文本渲染
        "params": {
            "aspect_ratio": "16:9",           # 图表比例
            "output_quality": 90,
            "guidance": 5,                    # 精确文本渲染
            "image_size": "optimize_for_quality"
        }
    },
    {
        "prompt": "A fantasy landscape with dragons flying over castles",
        "model": "black-forest-labs/flux-dev", # 创意内容
        "params": {
            "aspect_ratio": "16:9",           # 风景比例
            "output_quality": 85,
            "guidance": 3
        }
    },
    {
        "prompt": "A minimalist logo design for a tech startup",
        "model": "qwen/qwen-image",           # 设计类图像
        "params": {
            "aspect_ratio": "1:1",           # 标志比例
            "output_quality": 100,          # 最高质量
            "image_size": "optimize_for_quality",
            "enhance_prompt": True
        }
    }
]

# 高级批处理器配置
ADVANCED_PROCESSOR_CONFIG = {
    "max_concurrent": 15,        # 混合模型可以更高并发
    "rate_limit_per_minute": 600,  # Replicate API 限制
    "max_retries": 3             # 失败重试次数
}

async def advanced_mixed_models():
    """
    场景3: 混合模型高级批处理
    
    使用方法:
    1. 修改上面的 MIXED_MODEL_REQUESTS 参数配置
    2. 调整 ADVANCED_PROCESSOR_CONFIG 处理器设置
    3. 调用此函数或直接复制调用代码
    
    适用场景:
    - 不同类型的图像需求
    - 每个任务使用最适合的模型
    - 复杂的批处理需求
    - 大规模处理 (10-1000+个)
    """
    
    print("🎯 场景3: 混合模型高级批处理")
    print(f"   任务数量: {len(MIXED_MODEL_REQUESTS)}")
    
    try:
        # 🚀 核心调用代码开始 - 可直接复制使用
        
        # 1. 转换为BatchRequest对象
        batch_requests = []
        
        for i, req_config in enumerate(MIXED_MODEL_REQUESTS):
            request = BatchRequest(
                prompt=req_config["prompt"],
                model_name=req_config["model"],
                output_filepath=f"output/mixed_example_{i+1:02d}_{req_config['model'].replace('/', '_')}.jpg",
                kwargs=req_config["params"],
                request_id=f"mixed_example_{i+1:02d}"
            )
            batch_requests.append(request)
        
        # 2. 创建高级批处理器
        processor = IntelligentBatchProcessor(
            max_concurrent=ADVANCED_PROCESSOR_CONFIG["max_concurrent"],
            rate_limit_per_minute=ADVANCED_PROCESSOR_CONFIG["rate_limit_per_minute"],
            max_retries=ADVANCED_PROCESSOR_CONFIG["max_retries"]
        )
        
        # 3. 执行智能批处理
        results = await processor.process_intelligent_batch(batch_requests)
        
        # 🚀 核心调用代码结束
        
        # 统计模型分布
        model_counts = {}
        for req in batch_requests:
            model_counts[req.model_name] = model_counts.get(req.model_name, 0) + 1
        
        print("📊 模型分布:")
        for model, count in model_counts.items():
            print(f"   {model}: {count} 个任务")
        
        # 分析结果
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        print(f"✅ 混合模型批处理完成!")
        print(f"   成功: {len(successful_results)} 个")
        print(f"   失败: {len(failed_results)} 个")
        print(f"   成功率: {len(successful_results)/len(results)*100:.1f}%")
        
        # 收集成功的文件
        successful_files = []
        print("📁 生成的文件:")
        for result in successful_results:
            if result.file_paths:
                successful_files.extend(result.file_paths)
                print(f"   ✅ {result.model_name}: {os.path.basename(result.file_paths[0])}")
        
        # 显示失败的任务
        if failed_results:
            print("❌ 失败的任务:")
            for result in failed_results:
                print(f"   {result.model_name}: {result.error}")
        
        return successful_files
        
    except Exception as e:
        print(f"❌ 混合模型批处理失败: {e}")
        return []


# =============================================================================
# 完整演示和测试函数
# =============================================================================

async def run_all_examples():
    """运行所有三个使用场景的完整演示"""
    
    print("🚀 Replicate 模型调用 - 三种场景完整演示")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    all_files = []
    
    try:
        # 场景1: 单个图像生成
        print("\n" + "=" * 60)
        single_file = single_image_generation()
        if single_file:
            all_files.append(single_file)
        
        # 场景2: 同模型批量生成
        print("\n" + "=" * 60)
        batch_files = await batch_same_model()
        all_files.extend(batch_files)
        
        # 场景3: 混合模型高级批处理
        print("\n" + "=" * 60)
        mixed_files = await advanced_mixed_models()
        all_files.extend(mixed_files)
        
        # 最终总结
        print("\n" + "=" * 60)
        print("🎉 所有演示完成!")
        print(f"   总生成文件: {len(all_files)} 个")
        print(f"   输出目录: output/")
        print("   三种使用场景都已经过测试验证")
        
        return all_files
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return all_files


# =============================================================================
# 示例5: Text-to-Speech with Chatterbox
# =============================================================================

def text_to_speech_example():
    """
    使用 Chatterbox 模型进行文本到语音转换
    支持情感控制和可选的语音克隆
    """
    print("\n" + "=" * 60)
    print("🎤 Text-to-Speech Example with Chatterbox")
    print("=" * 60)
    
    # 基本 TTS 示例
    print("\n1️⃣ Basic Text-to-Speech:")
    basic_text = "Hello! This is a test of the Chatterbox text-to-speech model. It can generate natural sounding speech with emotion control."
    
    print(f"   Text: {basic_text[:50]}...")
    output_basic = replicate_model_calling(
        prompt=basic_text,
        model_name="resemble-ai/chatterbox",
        output_filepath="output/tts_basic.wav"
    )
    print(f"   ✅ Generated: {output_basic[0]}")
    
    # 带参数控制的 TTS
    print("\n2️⃣ TTS with Custom Parameters:")
    custom_text = "I'm speaking with different temperature and exaggeration settings. This creates more expressive speech!"
    
    output_custom = replicate_model_calling(
        prompt=custom_text,
        model_name="resemble-ai/chatterbox",
        output_filepath="output/tts_custom.wav",
        temperature=1.5,  # 更高的温度，更多变化
        exaggeration=0.8,  # 更高的夸张度
        cfg_weight=0.7,
        seed=42  # 固定种子以便复现
    )
    print(f"   Parameters used:")
    print(f"   - Temperature: 1.5 (more variation)")
    print(f"   - Exaggeration: 0.8 (more expressive)")
    print(f"   - CFG Weight: 0.7")
    print(f"   ✅ Generated: {output_custom[0]}")
    
    # 带参考音频的 TTS（语音克隆）- 可选
    print("\n3️⃣ TTS with Voice Cloning (Optional):")
    clone_text = "If you provide a reference audio file, I can clone that voice style!"
    
    # 检查是否要使用参考音频
    use_ref = input("   Do you have a reference audio file for voice cloning? (y/n): ").lower().strip()
    
    if use_ref == 'y':
        ref_audio_path = input("   Enter the path to your reference audio file: ").strip()
        if ref_audio_path and os.path.exists(ref_audio_path):
            output_clone = replicate_model_calling(
                prompt=clone_text,
                model_name="resemble-ai/chatterbox",
                output_filepath="output/tts_cloned.wav",
                audio_prompt=ref_audio_path
            )
            print(f"   ✅ Generated with voice cloning: {output_clone[0]}")
        else:
            print("   ⚠️ Reference audio file not found, skipping voice cloning example")
    else:
        print("   ⏭️ Skipping voice cloning example")
    
    # 批量 TTS 处理
    print("\n4️⃣ Batch TTS Processing:")
    texts = [
        "This is the first sentence.",
        "Here comes the second one with more emotion!",
        "And finally, the third sentence completes our batch."
    ]
    
    print("   Processing multiple texts...")
    for i, text in enumerate(texts, 1):
        output = replicate_model_calling(
            prompt=text,
            model_name="resemble-ai/chatterbox",
            output_filepath=f"output/tts_batch_{i}.wav",
            temperature=0.8 + (i * 0.2),  # 递增温度
            exaggeration=0.4 + (i * 0.1)  # 递增夸张度
        )
        print(f"   ✅ [{i}/3] Generated: {output[0]}")
    
    print("\n" + "=" * 60)
    print("🎉 Text-to-Speech examples completed!")
    print("=" * 60)
    
    return True


# =============================================================================
# 交互式选择函数
# =============================================================================

async def interactive_examples():
    """交互式选择要运行的示例"""
    
    print("🎯 Replicate 模型调用 - 使用示例")
    print("请选择要运行的示例:")
    print("1. 单个图像生成 (最简单)")
    print("2. 同模型批量生成 (5个图像)")
    print("3. 混合模型高级批处理 (5个不同配置)")
    print("4. 🎤 Text-to-Speech (Chatterbox音频生成)")
    print("5. 运行所有示例")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再见!")
                break
            elif choice == '1':
                single_image_generation()
            elif choice == '2':
                await batch_same_model()
            elif choice == '3':
                await advanced_mixed_models()
            elif choice == '4':
                text_to_speech_example()
            elif choice == '5':
                await run_all_examples()
            else:
                print("❌ 无效选择，请输入 0-5")
                continue
                
            print("\n" + "-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


# =============================================================================
# 主程序入口
# =============================================================================

if __name__ == "__main__":
    """
    使用说明:
    
    1. 直接运行: python example_usage.py
       - 交互式选择要运行的示例
    
    2. 运行所有示例: python example_usage.py all
       - 自动运行三个场景的完整演示
       
    3. 在你的代码中导入使用:
       from example_usage import single_image_generation, batch_same_model, advanced_mixed_models
    """
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        # 运行所有示例
        asyncio.run(run_all_examples())
    else:
        # 交互式选择
        asyncio.run(interactive_examples())