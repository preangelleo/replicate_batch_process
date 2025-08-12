#!/usr/bin/env python3
"""
Fallback机制测试脚本

测试各种fallback场景：
1. Reference image fallback (Flux Dev -> Flux Kontext Max)
2. Parameter invalidation fallback
3. API error fallback
"""

import os
import sys
from main import replicate_model_calling, check_fallback_conditions, map_parameters
from config import FALLBACK_MODELS, FALLBACK_PARAMETER_MAPPING

def test_reference_image_fallback():
    """测试reference image fallback"""
    print("=" * 60)
    print("🧪 测试 1: Reference Image Fallback")
    print("=" * 60)
    print("场景: 用户给Flux Dev传入reference image，应该fallback到Flux Kontext Max")
    print()
    
    # 模拟给Flux Dev传入reference image
    model_name = "black-forest-labs/flux-dev"
    kwargs = {
        "input_image": "https://example.com/reference.jpg",  # 模拟reference image
        "aspect_ratio": "16:9",
        "output_quality": 85
    }
    
    # 检查fallback条件
    should_fallback, reason, fallback_model, mapped_kwargs = check_fallback_conditions(model_name, **kwargs)
    
    print(f"原始模型: {model_name}")
    print(f"原始参数: {kwargs}")
    print(f"是否需要fallback: {should_fallback}")
    
    if should_fallback:
        print(f"✅ Fallback成功!")
        print(f"   Fallback原因: {reason}")
        print(f"   目标模型: {fallback_model}")
        print(f"   映射后参数: {mapped_kwargs}")
    else:
        print("❌ Fallback检测失败")
    
    print()

def test_parameter_invalidation_fallback():
    """测试参数不兼容fallback"""
    print("=" * 60) 
    print("🧪 测试 2: Parameter Invalidation Fallback")
    print("=" * 60)
    print("场景: 用户给Flux Kontext Max传入不支持的参数，应该fallback到Flux Dev")
    print()
    
    model_name = "black-forest-labs/flux-kontext-max"
    kwargs = {
        "guidance": 3.5,  # Flux Kontext Max不支持的参数
        "num_outputs": 2,  # 不支持的参数
        "aspect_ratio": "16:9",
        "output_quality": 90
    }
    
    should_fallback, reason, fallback_model, mapped_kwargs = check_fallback_conditions(model_name, **kwargs)
    
    print(f"原始模型: {model_name}")
    print(f"原始参数: {kwargs}")
    print(f"是否需要fallback: {should_fallback}")
    
    if should_fallback:
        print(f"✅ Fallback成功!")
        print(f"   Fallback原因: {reason}")
        print(f"   目标模型: {fallback_model}")
        print(f"   映射后参数: {mapped_kwargs}")
    else:
        print("❌ Fallback检测失败")
    
    print()

def test_parameter_mapping():
    """测试参数映射功能"""
    print("=" * 60)
    print("🧪 测试 3: Parameter Mapping")
    print("=" * 60)
    print("场景: 测试不同模型之间的参数映射")
    print()
    
    # 测试 Flux Dev -> Qwen Image 映射
    source_model = "black-forest-labs/flux-dev"
    target_model = "qwen/qwen-image"
    
    original_kwargs = {
        "aspect_ratio": "16:9",
        "output_quality": 85,
        "guidance": 3.5,
        "output_format": "jpg",
        "seed": 12345,  # 应该被移除
        "go_fast": True,  # 应该被移除
        "num_inference_steps": 30
    }
    
    print(f"源模型: {source_model}")
    print(f"目标模型: {target_model}")
    print(f"原始参数: {original_kwargs}")
    print()
    
    mapped_kwargs = map_parameters(source_model, target_model, original_kwargs)
    
    print(f"映射后参数: {mapped_kwargs}")
    print()

def test_fallback_chain():
    """测试fallback链"""
    print("=" * 60)
    print("🧪 测试 4: Fallback Chain Analysis")
    print("=" * 60)
    print("分析各个模型的fallback链")
    print()
    
    for model_name, fallback_config in FALLBACK_MODELS.items():
        print(f"📌 {model_name}:")
        for trigger, config in fallback_config.items():
            fallback_model = config['fallback_model']
            description = config['description']
            print(f"   {trigger} -> {fallback_model}")
            print(f"      描述: {description}")
        print()

def test_mapping_coverage():
    """测试映射覆盖度"""
    print("=" * 60)
    print("🧪 测试 5: Mapping Coverage Analysis")
    print("=" * 60)
    print("检查fallback映射的覆盖情况")
    print()
    
    # 收集所有可能的fallback组合
    fallback_pairs = set()
    
    for model_name, fallback_config in FALLBACK_MODELS.items():
        for trigger, config in fallback_config.items():
            fallback_model = config['fallback_model']
            fallback_pairs.add((model_name, fallback_model))
    
    print("🔗 所有可能的fallback组合:")
    for source, target in sorted(fallback_pairs):
        print(f"   {source} -> {target}")
    
    print()
    print("📋 已配置的参数映射:")
    for (source, target) in FALLBACK_PARAMETER_MAPPING.keys():
        print(f"   ✅ {source} -> {target}")
    
    print()
    print("⚠️  缺少参数映射的组合:")
    missing_mappings = fallback_pairs - set(FALLBACK_PARAMETER_MAPPING.keys())
    for source, target in sorted(missing_mappings):
        print(f"   ❌ {source} -> {target}")
    
    if not missing_mappings:
        print("   🎉 所有fallback组合都有参数映射配置！")

def run_all_tests():
    """运行所有测试"""
    print("🚀 Replicate Fallback机制测试")
    print("=" * 60)
    print()
    
    try:
        test_reference_image_fallback()
        test_parameter_invalidation_fallback()
        test_parameter_mapping()
        test_fallback_chain()
        test_mapping_coverage()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()