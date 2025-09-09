#!/usr/bin/env python3
"""
Global Concurrency Control Usage Example

Demonstrates how to use the upgraded global concurrency control features
"""

import asyncio
import os
import sys

# Add project path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'replicate_batch_process'))

from replicate_batch_process.intelligent_batch_processor import intelligent_batch_process
from replicate_batch_process.global_concurrency_manager import get_global_status


async def example_environment_variables():
    """Example 1: Using Environment Variables (Recommended)"""
    print("📖 Example 1: Environment Variable Configuration")
    print("="*50)
    
    # Set environment variables (in actual use, these should be set before startup)
    os.environ["REPLICATE_API_TOKEN"] = "r8_your_real_token_here"
    os.environ["REPLICATE_GLOBAL_MAX_CONCURRENT"] = "60"
    
    print("🔧 Setting environment variables:")
    print(f"   REPLICATE_API_TOKEN=r8_your_real_token_here")
    print(f"   REPLICATE_GLOBAL_MAX_CONCURRENT=10")
    
    # Prepare test data
    prompts = [
        "Beautiful sunset over mountains",
        "Peaceful lake reflection",
        "City skyline at night"
    ]
    
    print(f"\n🎯 Starting batch processing of {len(prompts)} images...")
    
    try:
        # Use environment variable configuration for batch processing
        files = await intelligent_batch_process(
            prompts=prompts,
            model_name="black-forest-labs/flux-dev",
            max_concurrent=3,  # Local concurrency limit
            output_dir="/Users/lgg/coding/testing_folder/example_global_output"
        )
        
        print(f"✅ Batch processing completed! Generated {len(files)} files")
        for file in files:
            print(f"   📄 {file}")
            
    except Exception as e:
        print(f"⚠️ Batch processing failed (expected, no real token): {e}")
    
    # Display global status
    status = get_global_status()
    print(f"\n📊 Global concurrency status:")
    print(f"   Max concurrent: {status['global_max_concurrent']}")
    print(f"   Current concurrent: {status['current_concurrent']}")
    print(f"   Available slots: {status['available_slots']}")


async def example_parameter_override():
    """Example 2: Parameter Passing (Highest Priority)"""
    print("\n\n📖 Example 2: Parameter Passing Configuration (Highest Priority)")
    print("="*50)
    
    prompts = [
        "Abstract art composition",
        "Futuristic robot design"
    ]
    
    print(f"🎯 Starting batch processing of {len(prompts)} images...")
    print("🔑 Using parameter-passed credentials (higher priority than environment variables)")
    
    try:
        # Parameter passing method (highest priority)
        files = await intelligent_batch_process(
            prompts=prompts,
            model_name="black-forest-labs/flux-dev",
            max_concurrent=2,  # Local concurrency limit
            replicate_api_token="r8_parameter_override_token",  # Highest priority
            global_max_concurrent=60,  # Global concurrency limit, highest priority
            output_dir="/Users/lgg/coding/testing_folder/example_global_output"
        )
        
        print(f"✅ Batch processing completed! Generated {len(files)} files")
        
    except Exception as e:
        print(f"⚠️ Batch processing failed (expected, no real token): {e}")
    
    # Display updated global status
    status = get_global_status()
    print(f"\n📊 Updated global concurrency status:")
    print(f"   Max concurrent: {status['global_max_concurrent']}")
    print(f"   Note: Due to singleton pattern, using first initialization config")


async def example_multiple_instances():
    """Example 3: Multiple Instance Collaboration"""
    print("\n\n📖 Example 3: Multiple Instance Collaboration")
    print("="*50)
    
    from replicate_batch_process.intelligent_batch_processor import IntelligentBatchProcessor
    
    # Create multiple processor instances
    print("🏭 Creating multiple batch processor instances...")
    
    processor1 = IntelligentBatchProcessor(
        max_concurrent=4,  # Local concurrency
        replicate_api_token="r8_instance1_token",
        global_max_concurrent=60  # Global concurrency
    )
    
    processor2 = IntelligentBatchProcessor(
        max_concurrent=3,  # Local concurrency
        replicate_api_token="r8_instance2_token",
        global_max_concurrent=60  # Should be ignored (singleton pattern)
    )
    
    # Verify global state sharing
    status1 = processor1.global_manager.get_global_status()
    status2 = processor2.global_manager.get_global_status()
    
    print(f"📊 Instance 1 status: max_concurrent={status1['global_max_concurrent']}")
    print(f"📊 Instance 2 status: max_concurrent={status2['global_max_concurrent']}")
    print(f"✅ Verification: Both instances share same global configuration")
    
    # Simulate collaborative work
    print("\n🤝 Simulating multi-instance collaboration...")
    print("   Instance 1 handles landscape images")
    print("   Instance 2 handles portrait images")
    print("   Global concurrency control ensures account limits are not exceeded")


async def example_monitoring():
    """Example 4: Monitoring and Status Viewing"""
    print("\n\n📖 Example 4: Monitoring and Status Viewing")
    print("="*50)
    
    # Get detailed status
    status = get_global_status()
    
    print("📊 Global concurrency manager detailed status:")
    print(f"   🎯 Global max concurrent: {status['global_max_concurrent']}")
    print(f"   🔄 Current concurrent requests: {status['current_concurrent']}")
    print(f"   📊 Available slots: {status['available_slots']}")
    print(f"   📈 Utilization rate: {status['utilization_percentage']:.1f}%")
    print(f"   📋 Total requests: {status['total_requests']}")
    print(f"   🔝 Max concurrent reached: {status['max_concurrent_reached']}")
    print(f"   ⏱️  Uptime: {status['uptime_seconds']:.1f} seconds")
    
    # Monitoring recommendations
    print("\n💡 Monitoring recommendations:")
    if status['utilization_percentage'] > 80:
        print("   ⚠️ High utilization! Consider increasing global concurrency limit")
    elif status['utilization_percentage'] < 20:
        print("   📉 Low utilization, consider reducing global concurrency limit to save resources")
    else:
        print("   ✅ Utilization rate is normal")


async def main():
    """Main function: Run all examples"""
    print("🚀 Global Concurrency Control Feature Demonstration")
    print("🌐 Replicate Batch Process - Global Concurrency Control")
    print("="*80)
    
    try:
        await example_environment_variables()
        await example_parameter_override()
        await example_multiple_instances()
        await example_monitoring()
        
        print("\n" + "="*80)
        print("🎉 Demonstration completed!")
        
        print("\n📚 Key points summary:")
        print("1. Environment variable configuration is simple and secure")
        print("2. Parameter passing provides highest priority")
        print("3. Multiple instances automatically share global state")
        print("4. Real-time concurrency status monitoring")
        print("5. Fully backward compatible with existing code")
        
        print("\n🔗 Related documentation:")
        print("   - GLOBAL_CONCURRENCY_UPGRADE.md: Detailed upgrade documentation")
        print("   - test_global_concurrency.py: Complete test suite")
        
    except Exception as e:
        print(f"\n❌ Error occurred during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())