#!/usr/bin/env python3
"""
Global Replicate Concurrency Manager
全局Replicate账号并发控制管理器

This module provides global concurrency control for Replicate API calls across multiple
batch processing instances to ensure safe image generation within account limits.

Based on the volcengine-concurrent-tts global semaphore pattern.
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ReplicateCredentials:
    """Replicate API 凭据配置"""
    api_token: str
    global_max_concurrent: int = 10
    
    def __post_init__(self):
        if not self.api_token:
            raise ValueError("api_token is required")


class GlobalReplicateConcurrencyManager:
    """
    全局Replicate账号并发控制管理器
    
    确保所有批处理实例共享同一个全局信号量，防止超出Replicate账号并发限制。
    支持环境变量优先级：payload credentials > .env credentials > error
    
    Usage:
        # 方式1: 使用环境变量
        manager = GlobalReplicateConcurrencyManager()
        
        # 方式2: 传入凭据（优先级最高）
        manager = GlobalReplicateConcurrencyManager(
            api_token="r8_xxx",
            global_max_concurrent=15
        )
        
        # 在批处理中使用全局信号量
        async with manager.get_global_semaphore():
            # 执行Replicate API调用
            result = replicate.run(model, input=params)
    """
    
    _instance: Optional['GlobalReplicateConcurrencyManager'] = None
    _global_semaphore: Optional[asyncio.Semaphore] = None
    _credentials: Optional[ReplicateCredentials] = None
    _lock = asyncio.Lock()
    
    def __new__(cls, api_token: Optional[str] = None, global_max_concurrent: Optional[int] = None):
        """单例模式，确保全局只有一个管理器实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, api_token: Optional[str] = None, global_max_concurrent: Optional[int] = None):
        """
        初始化全局并发管理器
        
        Args:
            api_token: Replicate API token (优先级最高)
            global_max_concurrent: 全局最大并发数 (优先级最高)
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self._stats = {
            'total_requests': 0,
            'concurrent_requests': 0,
            'max_concurrent_reached': 0,
            'created_at': time.time()
        }
        
        # 获取凭据（支持优先级）
        self._credentials = self._get_credentials(api_token, global_max_concurrent)
        
        # 创建全局信号量
        if self._global_semaphore is None:
            self._global_semaphore = asyncio.Semaphore(self._credentials.global_max_concurrent)
        
        # 设置环境变量
        os.environ["REPLICATE_API_TOKEN"] = self._credentials.api_token
        
        self._initialized = True
        
        print(f"🌐 Global Replicate Concurrency Manager initialized:")
        print(f"   Global max concurrent: {self._credentials.global_max_concurrent}")
        print(f"   API token: {self._credentials.api_token[:12]}...")
    
    def _get_credentials(self, payload_api_token: Optional[str], payload_max_concurrent: Optional[int]) -> ReplicateCredentials:
        """
        获取凭据，支持优先级：payload > .env > error
        
        Args:
            payload_api_token: 从payload传入的API token (最高优先级)
            payload_max_concurrent: 从payload传入的并发数 (最高优先级)
            
        Returns:
            ReplicateCredentials: 凭据配置
            
        Raises:
            ValueError: 当无法获取必需凭据时
        """
        # 优先级1: Payload凭据 (最高优先级)
        api_token = payload_api_token
        max_concurrent = payload_max_concurrent
        
        # 优先级2: 环境变量
        if not api_token:
            api_token = os.getenv("REPLICATE_API_TOKEN")
        
        if max_concurrent is None:
            env_concurrent = os.getenv("REPLICATE_GLOBAL_MAX_CONCURRENT")
            if env_concurrent:
                try:
                    max_concurrent = int(env_concurrent)
                except ValueError:
                    print(f"⚠️ Invalid REPLICATE_GLOBAL_MAX_CONCURRENT value: {env_concurrent}, using default")
                    max_concurrent = 60
            else:
                max_concurrent = 60
        
        # 验证必需参数
        if not api_token:
            raise ValueError(
                "REPLICATE_API_TOKEN is required. Please set it in environment variables or pass it as parameter."
            )
        
        print(f"🔑 Credentials loaded:")
        print(f"   Source: {'payload' if payload_api_token else 'environment'}")
        print(f"   Max concurrent: {max_concurrent}")
        
        return ReplicateCredentials(
            api_token=api_token,
            global_max_concurrent=max_concurrent
        )
    
    def get_global_semaphore(self) -> asyncio.Semaphore:
        """
        获取全局信号量
        
        Returns:
            asyncio.Semaphore: 全局并发控制信号量
        """
        if self._global_semaphore is None:
            raise RuntimeError("Global semaphore not initialized")
        return self._global_semaphore
    
    async def acquire_global_quota(self) -> bool:
        """
        获取全局配额（非阻塞）
        
        Returns:
            bool: 是否成功获取配额
        """
        semaphore = self.get_global_semaphore()
        acquired = semaphore.locked()
        
        if not acquired:
            self._stats['total_requests'] += 1
            self._stats['concurrent_requests'] += 1
            self._stats['max_concurrent_reached'] = max(
                self._stats['max_concurrent_reached'],
                self._stats['concurrent_requests']
            )
        
        return not acquired
    
    async def release_global_quota(self):
        """释放全局配额"""
        self._stats['concurrent_requests'] = max(0, self._stats['concurrent_requests'] - 1)
    
    def get_global_status(self) -> Dict[str, Any]:
        """
        获取全局并发状态
        
        Returns:
            dict: 全局状态信息
        """
        semaphore = self.get_global_semaphore()
        
        return {
            'global_max_concurrent': self._credentials.global_max_concurrent,
            'current_concurrent': self._credentials.global_max_concurrent - semaphore._value,
            'available_slots': semaphore._value,
            'utilization_percentage': ((self._credentials.global_max_concurrent - semaphore._value) / self._credentials.global_max_concurrent) * 100,
            'total_requests': self._stats['total_requests'],
            'max_concurrent_reached': self._stats['max_concurrent_reached'],
            'uptime_seconds': time.time() - self._stats['created_at']
        }
    
    def update_credentials(self, api_token: Optional[str] = None, global_max_concurrent: Optional[int] = None):
        """
        动态更新凭据（慎用 - 会影响正在运行的任务）
        
        Args:
            api_token: 新的API token
            global_max_concurrent: 新的全局并发数
        """
        print("⚠️ Dynamically updating credentials - this may affect running tasks")
        
        # 更新凭据
        if api_token:
            self._credentials.api_token = api_token
            os.environ["REPLICATE_API_TOKEN"] = api_token
            print(f"   Updated API token: {api_token[:12]}...")
        
        if global_max_concurrent:
            old_concurrent = self._credentials.global_max_concurrent
            self._credentials.global_max_concurrent = global_max_concurrent
            
            # 重新创建信号量（危险操作）
            self._global_semaphore = asyncio.Semaphore(global_max_concurrent)
            
            print(f"   Updated max concurrent: {old_concurrent} -> {global_max_concurrent}")
            print("   ⚠️ Global semaphore recreated - existing acquisitions may be affected")


# 工厂函数，便于创建管理器
def create_global_manager(api_token: Optional[str] = None, global_max_concurrent: Optional[int] = None) -> GlobalReplicateConcurrencyManager:
    """
    工厂函数：创建全局Replicate并发管理器
    
    Args:
        api_token: Replicate API token (可选，优先级高于环境变量)
        global_max_concurrent: 全局最大并发数 (可选，优先级高于环境变量)
        
    Returns:
        GlobalReplicateConcurrencyManager: 全局并发管理器实例
    """
    return GlobalReplicateConcurrencyManager(api_token, global_max_concurrent)


# 便捷函数：获取全局信号量
def get_global_semaphore() -> asyncio.Semaphore:
    """
    便捷函数：获取全局信号量
    
    Returns:
        asyncio.Semaphore: 全局并发控制信号量
        
    Raises:
        RuntimeError: 当管理器未初始化时
    """
    manager = GlobalReplicateConcurrencyManager()
    return manager.get_global_semaphore()


# 便捷函数：获取全局状态
def get_global_status() -> Dict[str, Any]:
    """
    便捷函数：获取全局并发状态
    
    Returns:
        dict: 全局状态信息
    """
    manager = GlobalReplicateConcurrencyManager()
    return manager.get_global_status()


if __name__ == "__main__":
    # 演示用法
    async def demo():
        print("🧪 Global Concurrency Manager Demo")
        
        # 创建管理器
        manager = create_global_manager(
            api_token="r8_demo_token_12345678901234567890",
            global_max_concurrent=5
        )
        
        # 获取状态
        status = manager.get_global_status()
        print(f"📊 Global status: {status}")
        
        # 模拟并发控制
        print("\n🔄 Testing global semaphore...")
        semaphore = manager.get_global_semaphore()
        
        async def test_task(task_id: int):
            async with semaphore:
                print(f"  Task {task_id} acquired global quota")
                await asyncio.sleep(1)  # 模拟API调用
                print(f"  Task {task_id} completed")
        
        # 启动多个任务测试全局并发控制
        tasks = [test_task(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        # 查看最终状态
        final_status = manager.get_global_status()
        print(f"\n📊 Final status: {final_status}")
    
    asyncio.run(demo())