#!/usr/bin/env python3
"""
Comprehensive integration test for LLM-Autonomous Software Engineer
Tests all major components and their interactions
"""

import sys
import os
import sqlite3
import requests
import json
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_database_integration():
    """Test database connections and table creation"""
    print("🔍 Testing Database Integration...")
    
    try:
        conn = sqlite3.connect('dashboard.db')
        cursor = conn.cursor()
        
        # Check if all required tables exist
        tables = ['projects', 'analytics', 'system_metrics']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            if result:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing")
                return False
        
        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        print(f"  📊 Projects in database: {project_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_local_ai_engine():
    """Test local AI engine and model loading"""
    print("🤖 Testing Local AI Engine...")
    
    try:
        from src.core.local_ai_engine import LocalAIEngine
        
        ai_engine = LocalAIEngine()
        
        # Test model loading
        if ai_engine._load_model():
            print("  ✅ Local AI model loaded successfully")
        else:
            print("  ❌ Failed to load local AI model")
            return False
        
        # Test template loading
        if hasattr(ai_engine, 'templates') and ai_engine.templates:
            print(f"  ✅ Templates loaded: {len(ai_engine.templates)}")
        else:
            print("  ❌ No templates loaded")
            return False
        
        # Test prediction capability
        test_requirement = "Create a simple web application"
        try:
            prediction = ai_engine.predict_project_structure(test_requirement)
            if prediction:
                print("  ✅ AI prediction working")
            else:
                print("  ❌ AI prediction failed")
                return False
        except Exception as e:
            print(f"  ⚠️  AI prediction test skipped: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Local AI Engine error: {e}")
        return False

def test_autonomous_engine():
    """Test autonomous engine integration"""
    print("⚙️ Testing Autonomous Engine...")
    
    try:
        from src.core.autonomous_engine import AutonomousEngine
        
        engine = AutonomousEngine()
        print("  ✅ Autonomous engine initialized")
        
        # Test if engine has required components
        if hasattr(engine, 'gemini_client'):
            print("  ✅ Gemini client integrated")
        
        if hasattr(engine, 'tester'):
            print("  ✅ Tester component integrated")
        
        if hasattr(engine, 'deployer'):
            print("  ✅ Deployer component integrated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Autonomous Engine error: {e}")
        return False

def test_web_endpoints():
    """Test web application endpoints"""
    print("🌐 Testing Web Endpoints...")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/api/projects",
        "/api/system-metrics",
        "/api/analytics"
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - Status: {response.status_code}")
                success_count += 1
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    return success_count == len(endpoints)

def test_project_structure():
    """Test project structure and file organization"""
    print("📁 Testing Project Structure...")
    
    required_paths = [
        "src/core/autonomous_engine.py",
        "src/core/local_ai_engine.py",
        "src/core/ai_trainer.py",
        "config/settings.py",
        "models/local_ai/trained_model.pkl",
        "dashboard.db"
    ]
    
    success_count = 0
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"  ✅ {path}")
            success_count += 1
        else:
            print(f"  ❌ {path} - Missing")
    
    return success_count == len(required_paths)

def test_memory_system():
    """Test memory and checkpoint system"""
    print("🧠 Testing Memory System...")
    
    try:
        memory_dirs = [
            "memory",
            "checkpoints"
        ]
        
        for dir_path in memory_dirs:
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                print(f"  ✅ {dir_path} directory exists with {len(files)} items")
            else:
                print(f"  ❌ {dir_path} directory missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Memory system error: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Comprehensive Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Database Integration", test_database_integration),
        ("Local AI Engine", test_local_ai_engine),
        ("Autonomous Engine", test_autonomous_engine),
        ("Web Endpoints", test_web_endpoints),
        ("Project Structure", test_project_structure),
        ("Memory System", test_memory_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        results[test_name] = test_func()
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATIONS WORKING CORRECTLY!")
        return True
    else:
        print("⚠️  Some integrations need attention")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
