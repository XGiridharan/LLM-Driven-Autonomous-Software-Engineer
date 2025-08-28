#!/usr/bin/env python3
"""
Comprehensive error checking script for the autonomous engineering system.
This script validates all modules, imports, and core functionality.
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def check_module_import(module_path, module_name):
    """Check if a module can be imported successfully."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✓ {module_name} imported successfully")
        return True, module
    except Exception as e:
        print(f"✗ {module_name} import failed: {e}")
        traceback.print_exc()
        return False, None

def check_class_instantiation(module, class_name, *args, **kwargs):
    """Check if a class can be instantiated."""
    try:
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            print(f"✓ {class_name} instantiated successfully")
            return True, instance
        else:
            print(f"✗ {class_name} not found in module")
            return False, None
    except Exception as e:
        print(f"✗ {class_name} instantiation failed: {e}")
        return False, None

def main():
    """Run comprehensive error checking."""
    print("🔍 Comprehensive Error Check - Autonomous Engineering System")
    print("=" * 70)
    
    # Set up environment
    os.environ.setdefault('GEMINI_API_KEY', 'test_key')
    
    all_passed = True
    
    # Check core modules
    print("\n📦 Checking Core Modules:")
    
    modules_to_check = [
        ("config/settings.py", "settings"),
        ("src/core/gemini_client.py", "gemini_client"),
        ("src/core/memory_manager.py", "memory_manager"),
        ("src/core/task_planner.py", "task_planner"),
        ("src/core/autonomous_engine.py", "autonomous_engine"),
        ("src/tools/code_generator.py", "code_generator"),
        ("src/tools/tester.py", "tester"),
        ("src/tools/deployer.py", "deployer"),
        ("src/tools/file_manager.py", "file_manager"),
    ]
    
    imported_modules = {}
    
    for module_path, module_name in modules_to_check:
        full_path = project_root / module_path
        if full_path.exists():
            success, module = check_module_import(full_path, module_name)
            if success:
                imported_modules[module_name] = module
            else:
                all_passed = False
        else:
            print(f"✗ {module_path} not found")
            all_passed = False
    
    # Check class instantiations
    print("\n🏗️  Checking Class Instantiations:")
    
    if 'gemini_client' in imported_modules:
        success, _ = check_class_instantiation(
            imported_modules['gemini_client'], 'GeminiClient'
        )
        if not success:
            all_passed = False
    
    if 'memory_manager' in imported_modules:
        success, _ = check_class_instantiation(
            imported_modules['memory_manager'], 'MemoryManager', 'test_project'
        )
        if not success:
            all_passed = False
    
    if 'task_planner' in imported_modules:
        success, _ = check_class_instantiation(
            imported_modules['task_planner'], 'TaskPlanner'
        )
        if not success:
            all_passed = False
    
    # Check main entry point
    print("\n🚀 Checking Main Entry Point:")
    main_file = project_root / "main.py"
    if main_file.exists():
        success, main_module = check_module_import(main_file, "main")
        if not success:
            all_passed = False
    else:
        print("✗ main.py not found")
        all_passed = False
    
    # Check test file
    print("\n🧪 Checking Test Suite:")
    test_file = project_root / "test_enhanced_system.py"
    if test_file.exists():
        success, _ = check_module_import(test_file, "test_enhanced_system")
        if not success:
            all_passed = False
    else:
        print("✗ test_enhanced_system.py not found")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! The system is ready to run.")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY environment variable")
        print("2. Run: python main.py")
        print("3. Or run tests: python test_enhanced_system.py")
        return 0
    else:
        print("❌ SOME CHECKS FAILED! Please fix the issues above.")
        return 1

if __name__ == "__main__":
    import importlib.util
    exit_code = main()
    sys.exit(exit_code)
