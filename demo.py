"""
Demonstration script for the LLM-Driven Autonomous Software Engineer
"""
import asyncio
import logging
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.autonomous_engine import AutonomousEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demonstrate_todo_app():
    """Demonstrate building a todo app autonomously."""
    print("�� Demonstrating Autonomous Software Engineering")
    print("=" * 60)
    
    # Initialize the autonomous engine
    engine = AutonomousEngine("demo_todo_app")
    
    try:
        # Define the requirement
        requirement = """
        Create a complete todo list application with the following features:
        1. User authentication (login/logout)
        2. CRUD operations for todo items (Create, Read, Update, Delete)
        3. Mark todos as complete/incomplete
        4. RESTful API backend using FastAPI
        5. Simple HTML frontend with JavaScript
        6. SQLite database for data storage
        7. Unit tests for all functionality
        8. Docker containerization
        """
        
        print(f"📋 Requirement: {requirement.strip()}")
        print("\n🚀 Starting autonomous development...")
        
        # Build the application
        result = await engine.build_application(requirement)
        
        # Display results
        print("\n📊 Development Results:")
        print(f"✅ Success: {result['success']}")
        print(f"📁 Project Directory: {result['project_directory']}")
        print(f"🔄 Iterations: {result['iterations']}")
        
        if result['success']:
            print("\n🎉 Application built successfully!")
            print("\n📋 Project Summary:")
            summary = result['summary']['ai_generated_summary']
            print(summary[:500] + "..." if len(summary) > 500 else summary)
            
            # Show project status
            status = await engine.get_project_status()
            print(f"\n📈 Project Status: {status['task_progress']['status']}")
            print(f"📋 Tasks Completed: {status['task_progress']['completed']}/{status['task_progress']['total_tasks']}")
            
        else:
            print("\n❌ Application build failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        # Cleanup
        await engine.cleanup()
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"❌ Demonstration failed: {e}")

async def demonstrate_debugging():
    """Demonstrate debugging capabilities."""
    print("\n🔧 Demonstrating Debugging Capabilities")
    print("=" * 60)
    
    engine = AutonomousEngine("debug_demo")
    
    try:
        # Create a buggy code file
        buggy_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']  # Missing .get() method
    return total

def divide_numbers(a, b):
    return a / b  # No division by zero check

def process_user_data(user):
    if user['age'] > 18:  # Missing .get() method
        return "adult"
    return "minor"
'''
        
        # Save buggy code
        buggy_file = "buggy_code.py"
        with open(buggy_file, 'w') as f:
            f.write(buggy_code)
        
        print(f"🐛 Created buggy code file: {buggy_file}")
        print("🔍 Analyzing and fixing code...")
        
        # Debug and fix the code
        result = await engine.debug_and_fix(
            buggy_file,
            "Code has several bugs including missing error handling and potential crashes"
        )
        
        if result['success']:
            print("✅ Code successfully debugged and fixed!")
            print(f"🔧 Fixes applied: {len(result['fixes_applied'])}")
        else:
            print("❌ Debugging failed!")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        # Cleanup
        await engine.cleanup()
        
    except Exception as e:
        logger.error(f"Debugging demonstration failed: {e}")
        print(f"❌ Debugging demonstration failed: {e}")

async def main():
    """Main demonstration function."""
    print("�� LLM-Driven Autonomous Software Engineer - Live Demo")
    print("=" * 80)
    print("This demonstration showcases the autonomous software engineering capabilities")
    print("powered by Google's Gemini AI.")
    print()
    
    # Run demonstrations
    await demonstrate_todo_app()
    await demonstrate_debugging()
    
    print("\n🎯 Demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("• Autonomous requirement understanding")
    print("• Task planning and execution")
    print("• Code generation and testing")
    print("• Automatic debugging and fixing")
    print("• Project management and deployment")

if __name__ == "__main__":
    asyncio.run(main())
