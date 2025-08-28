"""
Main entry point for the LLM-Driven Autonomous Software Engineer
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.autonomous_engine import AutonomousEngine
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def main():
    """Main application entry point."""
    print("🚀 LLM-Driven Autonomous Software Engineer")
    print("=" * 50)
    
    try:
        # Test Gemini API connection
        engine = AutonomousEngine("demo_project")
        
        # Test connection
        print("Testing Gemini API connection...")
        connection_ok = await engine.llm_client.test_connection()
        
        if not connection_ok:
            print("❌ Failed to connect to Gemini API. Please check your API key.")
            return
        
        print("✅ Gemini API connection successful!")
        
        # Example: Build a todo app
        print("\n🎯 Building a Todo List Application...")
        requirement = "Create a todo list app with user authentication and CRUD operations"
        
        result = await engine.build_application(requirement)
        
        if result["success"]:
            print("✅ Application built successfully!")
            print(f"📁 Project directory: {result['project_directory']}")
            print(f"📊 Summary: {result['summary']['ai_generated_summary'][:200]}...")
        else:
            print("❌ Application build failed!")
            if "error" in result:
                print(f"Error: {result['error']}")
        
        # Get project status
        status = await engine.get_project_status()
        print(f"\n📈 Project Status: {status['task_progress']['status']}")
        print(f"📋 Tasks: {status['task_progress']['completed']}/{status['task_progress']['total_tasks']} completed")
        
        # Cleanup
        await engine.cleanup()
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"❌ Application failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
