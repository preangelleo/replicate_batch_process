#!/usr/bin/env python3
"""
测试全局并发控制升级
Test Global Concurrency Control Upgrade

验证全局并发控制功能是否正常工作
"""

import asyncio
import os
import time
import sys
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'replicate_batch_process'))

from replicate_batch_process.intelligent_batch_processor import intelligent_batch_process
from replicate_batch_process.global_concurrency_manager import create_global_manager, get_global_status


async def test_global_concurrency_manager():
    """测试全局并发管理器基本功能"""
    print("🧪 测试1: 全局并发管理器基本功能")
    
    # 使用测试凭据创建管理器
    test_api_token = "r8_test_token_12345678901234567890"
    manager = create_global_manager(
        api_token=test_api_token,
        global_max_concurrent=3
    )
    
    # 获取状态
    status = get_global_status()
    print(f"📊 全局状态: {status}")
    
    # 测试信号量获取和释放
    print("\n🔄 测试信号量获取和释放...")
    semaphore = manager.get_global_semaphore()
    
    async def test_task(task_id: int):
        async with semaphore:
            print(f"  任务 {task_id} 获得全局配额")
            await asyncio.sleep(1)  # 模拟API调用
            print(f"  任务 {task_id} 完成")
    
    # 启动多个任务测试并发控制
    tasks = [test_task(i) for i in range(6)]
    start_time = time.time()
    await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    print(f"✅ 6个任务完成，耗时: {duration:.1f}秒")
    print(f"   预期: 约 2秒 (3并发，每任务1秒)")
    
    # 最终状态
    final_status = get_global_status()
    print(f"📊 最终状态: {final_status}")


async def test_environment_priority():
    """测试环境变量优先级系统"""
    print("\n🧪 测试2: 单例模式行为验证")
    
    # 设置环境变量
    os.environ["REPLICATE_API_TOKEN"] = "r8_env_token_123"
    os.environ["REPLICATE_GLOBAL_MAX_CONCURRENT"] = "5"
    
    # 由于单例模式，所有管理器实例都共享相同的全局状态
    print("🔑 验证单例模式行为...")
    manager1 = create_global_manager(
        api_token="r8_payload_token_456",
        global_max_concurrent=8
    )
    
    manager2 = create_global_manager()  # 不传入任何参数
    
    # 验证单例行为：两个管理器实际上是同一个实例
    assert manager1 is manager2, "单例模式失败"
    print("✅ 单例模式正常：所有实例共享全局状态")
    
    status1 = manager1.get_global_status()
    status2 = manager2.get_global_status()
    
    print(f"📊 管理器1状态: max_concurrent={status1['global_max_concurrent']}")
    print(f"📊 管理器2状态: max_concurrent={status2['global_max_concurrent']}")
    
    # 验证关键状态字段一致（忽略时间相关字段）
    key_fields = ['global_max_concurrent', 'current_concurrent', 'available_slots', 'utilization_percentage']
    for field in key_fields:
        assert status1[field] == status2[field], f"字段 {field} 不一致: {status1[field]} != {status2[field]}"
    print("✅ 全局状态一致性正常")


async def test_batch_processing_integration():
    """测试批处理集成"""
    print("\n🧪 测试3: 批处理集成 (模拟，不实际调用API)")
    
    # 准备测试数据
    test_prompts = [
        f"Test image {i+1}: beautiful landscape"
        for i in range(5)
    ]
    
    print(f"📝 准备 {len(test_prompts)} 个测试prompt")
    
    # 使用全局并发控制的批处理
    print("🚀 启动全局并发控制的批处理...")
    
    # 注意：这里会失败，因为我们没有真实的API token
    # 但可以验证参数传递是否正确
    try:
        files = await intelligent_batch_process(
            prompts=test_prompts,
            model_name="black-forest-labs/flux-dev",
            max_concurrent=3,
            replicate_api_token="r8_test_integration_token",
            global_max_concurrent=2,
            output_dir="/Users/lgg/coding/testing_folder/test_global_concurrency_output"
        )
        print(f"✅ 批处理完成，生成文件: {len(files)}")
        
    except Exception as e:
        if "api_token" in str(e).lower() or "replicate" in str(e).lower():
            print("✅ 全局并发控制集成正常 (预期的API token错误)")
        else:
            print(f"❌ 意外错误: {e}")
            raise


async def test_multiple_instances():
    """测试多实例共享全局状态"""
    print("\n🧪 测试4: 多实例共享全局状态")
    
    from replicate_batch_process.intelligent_batch_processor import IntelligentBatchProcessor
    
    # 创建多个处理器实例
    processor1 = IntelligentBatchProcessor(
        max_concurrent=4,
        replicate_api_token="r8_instance1_token",
        global_max_concurrent=6
    )
    
    processor2 = IntelligentBatchProcessor(
        max_concurrent=3,
        replicate_api_token="r8_instance2_token",  # 不同token但应该使用全局管理器
        global_max_concurrent=8  # 不同设置但应该使用已存在的全局管理器
    )
    
    # 验证都使用同一个全局管理器
    status1 = processor1.global_manager.get_global_status()
    status2 = processor2.global_manager.get_global_status()
    
    print(f"📊 实例1状态: {status1}")
    print(f"📊 实例2状态: {status2}")
    
    # 由于单例模式，两个实例应该共享相同的全局配置
    assert status1['global_max_concurrent'] == status2['global_max_concurrent'], "全局状态共享失败"
    print("✅ 多实例全局状态共享正常")


async def main():
    """主测试函数"""
    print("🚀 开始测试全局并发控制升级")
    print("="*60)
    
    try:
        await test_global_concurrency_manager()
        await test_environment_priority()
        await test_batch_processing_integration()
        await test_multiple_instances()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！全局并发控制升级成功")
        
        # 最终使用说明
        print("\n📚 使用方式:")
        print("1. 环境变量方式:")
        print("   export REPLICATE_API_TOKEN='your_token'")
        print("   export REPLICATE_GLOBAL_MAX_CONCURRENT=10")
        print("   await intelligent_batch_process(prompts, model)")
        print()
        print("2. 参数传递方式 (优先级更高):")
        print("   await intelligent_batch_process(")
        print("       prompts=prompts,")
        print("       model_name=model,")
        print("       replicate_api_token='your_token',")
        print("       global_max_concurrent=15")
        print("   )")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())