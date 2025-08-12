#!/usr/bin/env python3
"""
智能批处理器 - 合并版本
整合了动态队列和智能策略的最佳功能
"""

import asyncio
import time
import math
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque

from .main import replicate_model_calling


@dataclass
class BatchRequest:
    """批处理请求"""
    prompt: str
    model_name: str
    output_filepath: Optional[str] = None
    kwargs: Dict[str, Any] = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.request_id is None:
            import time
            self.request_id = f"req_{int(time.time()*1000)}"


@dataclass
class BatchResult:
    """批处理结果"""
    request_id: str
    prompt: str
    model_name: str
    success: bool
    file_paths: Optional[List[str]] = None
    error: Optional[str] = None
    duration: Optional[float] = None


@dataclass
class QueuedTask:
    """队列中的任务"""
    request: BatchRequest
    future: asyncio.Future
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    attempts: int = 0


class IntelligentRateLimiter:
    """智能速率限制器 - 精确的动态配额管理"""
    
    def __init__(self, max_requests: int = 600, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_timestamps = deque()  # 存储请求时间戳
        self.lock = asyncio.Lock()
        
        print(f"🧠 智能速率限制器: {max_requests}请求/{window_seconds}秒")
    
    async def get_available_quota(self) -> int:
        """获取当前可用配额"""
        async with self.lock:
            now = time.time()
            
            # 清理超出时间窗口的请求
            while self.request_timestamps and now - self.request_timestamps[0] > self.window_seconds:
                self.request_timestamps.popleft()
            
            used_quota = len(self.request_timestamps)
            available_quota = self.max_requests - used_quota
            
            return max(0, available_quota)
    
    async def can_make_request(self) -> tuple[bool, float]:
        """检查是否可以发起请求，返回(可以发起, 需要等待的秒数)"""
        async with self.lock:
            now = time.time()
            
            # 清理超出窗口的旧请求
            while self.request_timestamps and now - self.request_timestamps[0] > self.window_seconds:
                self.request_timestamps.popleft()
            
            # 检查是否还有配额
            if len(self.request_timestamps) < self.max_requests:
                return True, 0.0
            
            # 计算需要等待多长时间
            oldest_request = self.request_timestamps[0]
            wait_time = self.window_seconds - (now - oldest_request) + 0.1  # 额外0.1秒缓冲
            return False, max(0, wait_time)
    
    async def reserve_quota(self, count: int) -> bool:
        """预留配额"""
        async with self.lock:
            now = time.time()
            
            # 清理超出时间窗口的请求（复制 get_available_quota 的逻辑，避免死锁）
            while self.request_timestamps and now - self.request_timestamps[0] > self.window_seconds:
                self.request_timestamps.popleft()
            
            used_quota = len(self.request_timestamps)
            available_quota = self.max_requests - used_quota
            available = max(0, available_quota)
            
            if available >= count:
                for _ in range(count):
                    self.request_timestamps.append(now)
                return True
            return False
    
    async def record_request(self):
        """记录一个新请求"""
        async with self.lock:
            self.request_timestamps.append(time.time())
    
    async def wait_for_quota(self, needed: int) -> float:
        """等待配额可用，返回需要等待的秒数"""
        available = await self.get_available_quota()
        
        if available >= needed:
            return 0.0
        
        # 计算需要等待多长时间
        now = time.time()
        
        # 找到最早的请求时间，计算何时会有足够配额
        requests_to_expire = needed - available
        if len(self.request_timestamps) >= requests_to_expire:
            earliest_expire_time = self.request_timestamps[requests_to_expire - 1] + self.window_seconds
            wait_time = max(0, earliest_expire_time - now + 0.1)  # 额外0.1秒缓冲
            return wait_time
        
        return 0.0
    
    def get_status(self) -> dict:
        """获取当前状态"""
        now = time.time()
        recent_requests = [t for t in self.request_timestamps if now - t <= self.window_seconds]
        
        return {
            'used_quota': len(recent_requests),
            'available_quota': self.max_requests - len(recent_requests),
            'usage_percentage': (len(recent_requests) / self.max_requests) * 100,
            'window_seconds': self.window_seconds,
            'current_requests': len(recent_requests),
            'max_requests': self.max_requests
        }


class IntelligentBatchProcessor:
    """智能批处理器 - 合并最佳功能"""
    
    def __init__(self, 
                 max_concurrent: int = 8,
                 rate_limit_per_minute: int = 600,
                 max_retries: int = 3,
                 retry_delay: float = 2.0,
                 progress_callback: Optional[Callable] = None):
        
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.progress_callback = progress_callback
        
        # 智能速率限制器
        self.rate_limiter = IntelligentRateLimiter(rate_limit_per_minute, 60)
        
        # 队列和任务管理
        self.pending_queue = asyncio.Queue()  # 待处理任务队列
        self.active_tasks = {}  # 正在处理的任务
        self.completed_results = []
        self.failed_tasks = []
        
        # 统计信息
        self.stats = {
            'total_submitted': 0,
            'total_completed': 0,
            'total_failed': 0,
            'total_retried': 0,
            'start_time': None,
            'end_time': None
        }
        
        print(f"🧠 智能批处理器初始化:")
        print(f"   最大并发: {max_concurrent}")
        print(f"   速率限制: {rate_limit_per_minute}/分钟")
        print(f"   最大重试: {max_retries}")
    
    async def analyze_batch_strategy(self, requests: List[BatchRequest]) -> dict:
        """分析批处理策略"""
        total_requests = len(requests)
        current_quota = await self.rate_limiter.get_available_quota()
        
        strategy = {
            'total_requests': total_requests,
            'current_quota': current_quota,
            'can_process_all_immediately': total_requests <= current_quota,
            'recommended_approach': '',
            'estimated_completion_time': 0,
            'batches_needed': 1
        }
        
        if total_requests <= current_quota:
            # 策略1: 可以一次性处理所有任务
            strategy['recommended_approach'] = 'immediate_full_batch'
            strategy['estimated_completion_time'] = max(total_requests / self.max_concurrent * 25, 60)
            print(f"💡 策略分析: 任务量({total_requests}) <= 当前配额({current_quota})")
            print(f"   推荐: 一次性全部处理")
            
        elif total_requests <= self.rate_limiter.max_requests:
            # 策略2: 单个时间窗口内可以处理
            strategy['recommended_approach'] = 'single_window_batch'
            wait_time = await self.rate_limiter.wait_for_quota(total_requests)
            strategy['estimated_completion_time'] = wait_time + (total_requests / self.max_concurrent * 25)
            print(f"💡 策略分析: 任务量({total_requests}) <= 窗口配额({self.rate_limiter.max_requests})")
            print(f"   推荐: 单窗口批处理，等待 {wait_time:.1f} 秒")
            
        else:
            # 策略3: 需要多个时间窗口 + 动态队列
            strategy['recommended_approach'] = 'dynamic_queue_batch'
            strategy['batches_needed'] = math.ceil(total_requests / self.rate_limiter.max_requests)
            strategy['estimated_completion_time'] = strategy['batches_needed'] * 70  # 预估每个窗口70秒
            print(f"💡 策略分析: 任务量({total_requests}) > 窗口配额({self.rate_limiter.max_requests})")
            print(f"   推荐: 动态队列处理，预计需要 {strategy['batches_needed']} 个窗口")
        
        return strategy
    
    async def _process_single_task(self, queued_task: QueuedTask) -> BatchResult:
        """处理单个任务"""
        task_id = queued_task.request.request_id
        
        try:
            # 等待速率限制
            can_proceed, wait_time = await self.rate_limiter.can_make_request()
            if not can_proceed:
                print(f"⏳ 任务 {task_id} 等待速率限制: {wait_time:.1f}秒")
                await asyncio.sleep(wait_time)
            
            # 记录请求
            await self.rate_limiter.record_request()
            queued_task.started_at = time.time()
            
            # 处理请求
            start_time = time.time()
            
            # 调用 Replicate API
            file_paths = await asyncio.to_thread(
                replicate_model_calling,
                queued_task.request.prompt,
                queued_task.request.model_name,
                output_filepath=queued_task.request.output_filepath,
                **queued_task.request.kwargs
            )
            
            duration = time.time() - start_time
            
            return BatchResult(
                request_id=task_id,
                prompt=queued_task.request.prompt,
                model_name=queued_task.request.model_name,
                success=True,
                file_paths=file_paths,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            
            return BatchResult(
                request_id=task_id,
                prompt=queued_task.request.prompt,
                model_name=queued_task.request.model_name,
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def _process_task_simple(self, request: BatchRequest) -> BatchResult:
        """处理单个任务（简单版本，用于批量处理）"""
        start_time = time.time()
        
        try:
            # 调用 Replicate API
            file_paths = await asyncio.to_thread(
                replicate_model_calling,
                request.prompt,
                request.model_name,
                output_filepath=request.output_filepath,
                **request.kwargs
            )
            
            duration = time.time() - start_time
            return BatchResult(
                request_id=request.request_id,
                prompt=request.prompt,
                model_name=request.model_name,
                success=True,
                file_paths=file_paths,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return BatchResult(
                request_id=request.request_id,
                prompt=request.prompt,
                model_name=request.model_name,
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def _worker(self, worker_id: int):
        """工作线程 - 持续从队列中获取任务"""
        print(f"👷 工作线程 {worker_id} 启动")
        
        while True:
            try:
                # 从队列获取任务
                queued_task = await self.pending_queue.get()
                
                # 检查是否是停止信号
                if queued_task is None:
                    print(f"👷 工作线程 {worker_id} 收到停止信号")
                    break
                
                task_id = queued_task.request.request_id
                print(f"👷 工作线程 {worker_id} 开始处理任务 {task_id}")
                
                # 处理任务
                result = await self._process_single_task(queued_task)
                
                # 处理结果
                if result.success:
                    self.completed_results.append(result)
                    self.stats['total_completed'] += 1
                    print(f"✅ 任务 {task_id} 完成 ({result.duration:.1f}s)")
                    
                    if result.file_paths:
                        print(f"   📁 生成文件: {len(result.file_paths)}个")
                else:
                    # 检查是否需要重试
                    queued_task.attempts += 1
                    if queued_task.attempts < self.max_retries and '429' in str(result.error).lower():
                        # 重试
                        print(f"⚠️  任务 {task_id} 失败，准备重试 (第{queued_task.attempts}次)")
                        await asyncio.sleep(self.retry_delay * queued_task.attempts)  # 指数退避
                        await self.pending_queue.put(queued_task)
                        self.stats['total_retried'] += 1
                    else:
                        # 最终失败
                        self.failed_tasks.append(result)
                        self.stats['total_failed'] += 1
                        print(f"❌ 任务 {task_id} 最终失败: {result.error}")
                
                # 通知进度回调
                if self.progress_callback:
                    total_processed = self.stats['total_completed'] + self.stats['total_failed']
                    self.progress_callback(total_processed, self.stats['total_submitted'], result)
                
                # 标记任务完成
                self.pending_queue.task_done()
                
            except asyncio.CancelledError:
                print(f"👷 工作线程 {worker_id} 被取消")
                break
            except Exception as e:
                print(f"❌ 工作线程 {worker_id} 发生错误: {e}")
                self.pending_queue.task_done()
    
    async def _monitor_progress(self):
        """监控处理进度"""
        try:
            while True:
                await asyncio.sleep(10)  # 每10秒报告一次进度
                
                total_processed = self.stats['total_completed'] + self.stats['total_failed']
                pending_count = self.pending_queue.qsize()
                
                # 获取速率限制使用情况
                rate_usage = self.rate_limiter.get_status()
                
                print(f"📊 进度报告:")
                print(f"   已完成: {self.stats['total_completed']}")
                print(f"   已失败: {self.stats['total_failed']}")
                print(f"   队列中: {pending_count}")
                print(f"   速率使用: {rate_usage['current_requests']}/{rate_usage['max_requests']} ({rate_usage['usage_percentage']:.1f}%)")
                
                # 如果全部完成，退出监控
                if total_processed >= self.stats['total_submitted'] and pending_count == 0:
                    break
                    
        except asyncio.CancelledError:
            pass
    
    async def process_intelligent_batch(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """智能批处理 - 根据任务量自动选择最优策略"""
        
        if not requests:
            return []
        
        print(f"🎯 开始智能批处理 - {len(requests)} 个任务")
        
        # 重置统计
        self.stats.update({
            'total_submitted': len(requests),
            'total_completed': 0,
            'total_failed': 0,
            'total_retried': 0,
            'start_time': time.time()
        })
        
        self.completed_results = []
        self.failed_tasks = []
        
        # 分析处理策略
        strategy = await self.analyze_batch_strategy(requests)
        
        if strategy['recommended_approach'] == 'immediate_full_batch':
            # 策略1: 立即全部处理
            results = await self._process_immediate_full_batch(requests)
            
        elif strategy['recommended_approach'] == 'single_window_batch':
            # 策略2: 单窗口批处理
            results = await self._process_single_window_batch(requests)
            
        else:
            # 策略3: 动态队列批处理
            results = await self._process_dynamic_queue_batch(requests)
        
        # 记录结束时间
        self.stats['end_time'] = time.time()
        
        # 打印最终统计
        self._print_final_stats()
        
        return results
    
    async def _process_immediate_full_batch(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """策略1: 立即处理全部任务"""
        print(f"🚀 执行策略1: 立即全部处理")
        
        # 预留配额
        if not await self.rate_limiter.reserve_quota(len(requests)):
            print("❌ 配额预留失败")
            return []
        
        # 创建所有任务
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(request):
            async with semaphore:
                return await self._process_task_simple(request)
        
        # 并发处理所有任务
        tasks = [process_with_semaphore(request) for request in requests]
        results = []
        
        print(f"🔄 并发处理 {len(tasks)} 个任务...")
        
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"[{i+1}/{len(tasks)}] {status} {result.model_name} - {result.duration:.1f}s")
        
        total_time = time.time() - start_time
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # 更新统计数据
        self.stats['total_completed'] = len(successful)
        self.stats['total_failed'] = len(failed)
        self.completed_results = successful
        self.failed_tasks = failed
        
        print(f"✅ 策略1完成: {len(successful)}/{len(requests)} 成功，耗时 {total_time:.1f}秒")
        return results
    
    async def _process_single_window_batch(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """策略2: 单窗口批处理（需要等待配额）"""
        print(f"🚀 执行策略2: 单窗口批处理")
        
        # 等待足够配额
        wait_time = await self.rate_limiter.wait_for_quota(len(requests))
        if wait_time > 0:
            print(f"⏳ 等待配额可用: {wait_time:.1f} 秒")
            await asyncio.sleep(wait_time)
        
        # 预留配额
        if not await self.rate_limiter.reserve_quota(len(requests)):
            print("❌ 配额预留失败")
            return []
        
        # 执行处理（与策略1相同）
        results = await self._process_immediate_full_batch(requests)
        return results
    
    async def _process_dynamic_queue_batch(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """策略3: 动态队列批处理 - 适用于超大任务量"""
        print(f"🚀 执行策略3: 动态队列批处理")
        
        # 将所有任务加入队列
        for request in requests:
            # 生成输出文件路径（如果没有提供）
            if not request.output_filepath:
                timestamp = int(time.time() * 1000)
                model_safe = request.model_name.replace('/', '_').replace('-', '_')
                request.output_filepath = f"output/intelligent_{model_safe}_{timestamp}_{request.request_id}.jpg"
            
            queued_task = QueuedTask(request=request, future=asyncio.Future())
            await self.pending_queue.put(queued_task)
        
        # 启动工作线程
        workers = []
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(i))
            workers.append(worker)
        
        # 监控进度
        monitor_task = asyncio.create_task(self._monitor_progress())
        
        # 等待所有任务完成
        await self.pending_queue.join()
        
        # 停止工作线程
        for _ in range(self.max_concurrent):
            await self.pending_queue.put(None)  # 发送停止信号
        
        # 等待工作线程结束
        await asyncio.gather(*workers, return_exceptions=True)
        
        # 停止监控
        monitor_task.cancel()
        
        # 合并结果
        all_results = self.completed_results + self.failed_tasks
        
        return all_results
    
    def _print_final_stats(self):
        """打印最终统计信息"""
        total_time = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*80)
        print("📊 智能批处理完成统计")
        print("="*80)
        print(f"总任务数: {self.stats['total_submitted']}")
        print(f"✅ 成功: {self.stats['total_completed']}")
        print(f"❌ 失败: {self.stats['total_failed']}")
        print(f"🔄 重试: {self.stats['total_retried']}")
        print(f"⏱️  总用时: {total_time:.1f}秒")
        print(f"🚀 平均速度: {self.stats['total_completed']/total_time:.2f} 任务/秒")
        
        if self.completed_results:
            avg_duration = sum(r.duration for r in self.completed_results) / len(self.completed_results)
            total_files = sum(len(r.file_paths) for r in self.completed_results if r.file_paths)
            print(f"📁 生成文件: {total_files}个")
            print(f"⏱️  平均处理时间: {avg_duration:.2f}秒/任务")
        
        print("="*80)


# 便捷接口函数
async def intelligent_batch_process(
    prompts: List[str],
    model_name: str,
    max_concurrent: int = 8,
    output_dir: str = "output/intelligent_batch",
    **common_kwargs
) -> List[str]:
    """
    智能批处理接口
    
    Args:
        prompts: 提示词列表
        model_name: 模型名称
        max_concurrent: 最大并发数
        output_dir: 输出目录（仅在common_kwargs中没有output_filepath时使用）
        **common_kwargs: 通用参数，包括可选的output_filepath
        
    Returns:
        成功生成的文件路径列表
        
    Raises:
        ValueError: 当模型不被支持时
        
    示例:
        # 自动生成文件名
        files = await intelligent_batch_process(prompts, model_name)
        
        # 通过kwargs指定文件路径（推荐方式）
        files = await intelligent_batch_process(
            prompts=["sunset", "city"], 
            model_name="flux-dev",
            output_filepath=["output/scene_01_sunset.jpg", "output/scene_02_city.jpg"]
        )
    """
    import os
    from .config import REPLICATE_MODELS
    
    # 检查模型是否被支持
    if model_name not in REPLICATE_MODELS:
        supported_models = list(REPLICATE_MODELS.keys())
        supported_models_str = '\n'.join([f'  - {model}' for model in supported_models])
        error_message = f"Model '{model_name}' is not supported.\n\nSupported models:\n{supported_models_str}\n\nPlease use one of the supported models listed above."
        print(f"❌ {error_message}")
        raise ValueError(error_message)
    
    # 创建请求
    requests = []
    timestamp = int(time.time())
    
    for i, prompt in enumerate(prompts):
        # 处理输出文件路径
        kwargs_for_this_request = common_kwargs.copy()
        
        # 确定 output_filepath
        if 'output_filepath' in common_kwargs:
            output_filepath = common_kwargs['output_filepath']
            if isinstance(output_filepath, list):
                if len(output_filepath) != len(prompts):
                    raise ValueError(f"output_filepath 列表长度({len(output_filepath)}) 必须与 prompts 长度({len(prompts)}) 相同")
                filepath_for_this_request = output_filepath[i]
            else:
                # 如果是单个字符串，则所有请求使用相同路径
                filepath_for_this_request = output_filepath
            # 从 kwargs 中移除 output_filepath
            kwargs_for_this_request.pop('output_filepath', None)
        else:
            # 自动生成输出目录和文件名
            os.makedirs(output_dir, exist_ok=True)
            model_safe = model_name.replace('/', '_').replace('-', '_')
            filename = f"intelligent_{model_safe}_{timestamp}_{i:03d}.jpg"
            filepath_for_this_request = os.path.join(output_dir, filename)
        
        request = BatchRequest(
            prompt=prompt,
            model_name=model_name,
            output_filepath=filepath_for_this_request,
            kwargs=kwargs_for_this_request,
            request_id=f"intelligent_{timestamp}_{i:03d}"
        )
        requests.append(request)
    
    # 智能处理
    processor = IntelligentBatchProcessor(max_concurrent=max_concurrent)
    results = await processor.process_intelligent_batch(requests)
    
    # 返回成功文件
    successful_files = []
    for result in results:
        if result.success and result.file_paths:
            successful_files.extend(result.file_paths)
    
    return successful_files


# 演示
async def demo_intelligent_processing():
    """演示智能处理"""
    
    prompts = [
        f"Intelligent test image {i+1}: beautiful landscape scene"
        for i in range(15)  # 测试15个任务
    ]
    
    print("🧠 智能批处理演示")
    files = await intelligent_batch_process(
        prompts=prompts,
        model_name="black-forest-labs/flux-dev",
        max_concurrent=6,
        output_dir="output/intelligent_demo",
        aspect_ratio="16:9"
    )
    
    print(f"✅ 完成! 生成 {len(files)} 个文件")


if __name__ == "__main__":
    asyncio.run(demo_intelligent_processing())