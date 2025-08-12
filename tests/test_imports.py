#!/usr/bin/env python3
"""
Import test for replicate-batch-process package
Tests all critical imports to ensure package is properly structured
"""

def test_package_import():
    """Test basic package import"""
    try:
        import replicate_batch_process
        print("✅ replicate_batch_process imported successfully")
        print(f"   Version: {replicate_batch_process.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import replicate_batch_process: {e}")
        return False

def test_main_function_import():
    """Test main function import"""
    try:
        from replicate_batch_process import replicate_model_calling
        print("✅ replicate_model_calling imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import replicate_model_calling: {e}")
        return False

def test_batch_processor_import():
    """Test batch processor imports"""
    try:
        from replicate_batch_process import intelligent_batch_process
        print("✅ intelligent_batch_process imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import intelligent_batch_process: {e}")
        return False

def test_classes_import():
    """Test class imports"""
    try:
        from replicate_batch_process import IntelligentBatchProcessor, BatchRequest
        print("✅ IntelligentBatchProcessor and BatchRequest imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import classes: {e}")
        return False

def test_all_exports():
    """Test all exported functions"""
    try:
        import replicate_batch_process
        expected_exports = [
            'replicate_model_calling',
            'intelligent_batch_process', 
            'IntelligentBatchProcessor',
            'BatchRequest'
        ]
        
        for export in expected_exports:
            if not hasattr(replicate_batch_process, export):
                print(f"❌ Missing export: {export}")
                return False
                
        print(f"✅ All exports available: {expected_exports}")
        return True
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False

def run_all_tests():
    """Run all import tests"""
    print("🔍 Running import tests for replicate-batch-process v1.0.2...")
    print("-" * 60)
    
    tests = [
        test_package_import,
        test_main_function_import,
        test_batch_processor_import,
        test_classes_import,
        test_all_exports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("-" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL IMPORT TESTS PASSED! Package is ready for use.")
        return True
    else:
        print("💥 IMPORT TESTS FAILED! Package has structural issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)