"""
n8n Integration Demo for Autonomous Software Engineer
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8nIntegrationDemo:
    """Demonstrates n8n integration with autonomous software engineer."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the demo."""
        self.api_url = api_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_api_health(self) -> bool:
        """Test if the API is running."""
        try:
            async with self.session.get(f"{self.api_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"API Health Check: {data}")
                    return True
                else:
                    logger.error(f"API health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"API health check error: {e}")
            return False
    
    async def setup_n8n_integration(self, n8n_url: str) -> bool:
        """Set up n8n integration."""
        try:
            async with self.session.post(
                f"{self.api_url}/n8n/setup",
                params={"n8n_url": n8n_url}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"n8n Integration Setup: {data}")
                    return True
                else:
                    logger.error(f"n8n setup failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"n8n setup error: {e}")
            return False
    
    async def create_development_pipeline(self, requirement: str) -> Dict[str, Any]:
        """Create a development pipeline in n8n."""
        try:
            payload = {"requirement": requirement}
            async with self.session.post(
                f"{self.api_url}/n8n/create-pipeline",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Development Pipeline Created: {data}")
                    return data
                else:
                    logger.error(f"Pipeline creation failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Pipeline creation error: {e}")
            return {}
    
    async def plan_development(self, requirement: str) -> Dict[str, Any]:
        """Plan development using autonomous engine."""
        try:
            payload = {"requirement": requirement}
            async with self.session.post(
                f"{self.api_url}/plan",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Development Plan: {data}")
                    return data
                else:
                    logger.error(f"Planning failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Planning error: {e}")
            return {}
    
    async def build_application(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Build application using autonomous engine."""
        try:
            payload = {"plan": plan}
            async with self.session.post(
                f"{self.api_url}/build",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Application Build: {data}")
                    return data
                else:
                    logger.error(f"Build failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Build error: {e}")
            return {}
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get n8n workflow statistics."""
        try:
            async with self.session.get(f"{self.api_url}/n8n/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Workflow Statistics: {data}")
                    return data
                else:
                    logger.error(f"Statistics failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {}
    
    async def run_complete_demo(self):
        """Run the complete n8n integration demo."""
        print("🚀 n8n Integration Demo for Autonomous Software Engineer")
        print("=" * 70)
        
        # Test 1: API Health Check
        print("\n🔍 Test 1: API Health Check")
        if not await self.test_api_health():
            print("❌ API is not running. Please start the autonomous engine API first.")
            return
        
        # Test 2: n8n Integration Setup
        print("\n🔧 Test 2: n8n Integration Setup")
        n8n_url = "http://localhost:5678"
        if await self.setup_n8n_integration(n8n_url):
            print("✅ n8n integration configured successfully")
        else:
            print("⚠️  n8n integration setup failed (n8n might not be running)")
        
        # Test 3: Development Planning
        print("\n📋 Test 3: Development Planning")
        requirement = "Create a REST API for a blog system with user authentication"
        plan = await self.plan_development(requirement)
        
        if plan.get("success"):
            print("✅ Development plan created successfully")
            print(f"📝 Plan includes {len(plan.get('plan', {}).get('tasks', []))} tasks")
        else:
            print("❌ Development planning failed")
            return
        
        # Test 4: Application Building
        print("\n🏗️  Test 4: Application Building")
        build_result = await self.build_application(plan.get("plan", {}))
        
        if build_result.get("success"):
            print("✅ Application built successfully")
            print(f"📁 Project directory: {build_result.get('result', {}).get('project_directory', 'Unknown')}")
        else:
            print("❌ Application build failed")
            return
        
        # Test 5: Create n8n Pipeline
        print("\n🔄 Test 5: Create n8n Pipeline")
        pipeline_result = await self.create_development_pipeline(requirement)
        
        if pipeline_result.get("success"):
            print("✅ n8n development pipeline created successfully")
            print(f"🆔 Workflow ID: {pipeline_result.get('workflow_id', 'Unknown')}")
        else:
            print("⚠️  n8n pipeline creation failed (n8n might not be running)")
        
        # Test 6: Get Statistics
        print("\n📊 Test 6: Get Workflow Statistics")
        stats = await self.get_workflow_statistics()
        
        if stats.get("success"):
            print("✅ Workflow statistics retrieved successfully")
            print(f"📈 Total workflows: {stats.get('statistics', {}).get('total_workflows', 0)}")
            print(f"🚀 Development workflows: {stats.get('statistics', {}).get('development_workflows', 0)}")
        else:
            print("⚠️  Statistics retrieval failed")
        
        print("\n🎉 n8n Integration Demo Completed!")
        print("\n💡 Next Steps:")
        print("1. Open n8n at: http://localhost:5678")
        print("2. View the created development workflows")
        print("3. Monitor autonomous development progress")
        print("4. Customize workflows for your specific needs")

async def main():
    """Main demo function."""
    demo = N8nIntegrationDemo()
    
    async with demo:
        await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
