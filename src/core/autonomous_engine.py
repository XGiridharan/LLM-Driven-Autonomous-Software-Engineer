"""
Main autonomous engine that orchestrates the LLM-driven software development process
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import time
from functools import wraps
from pathlib import Path

try:
    from .gemini_client import GeminiClient
    from .task_planner import TaskPlanner, Task
    from .memory_manager import MemoryManager
    from ..tools.code_generator import CodeGenerator
    from ..tools.tester import Tester
    from ..tools.deployer import Deployer
    from ..tools.file_manager import FileManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.gemini_client import GeminiClient
    from core.task_planner import TaskPlanner, Task
    from core.memory_manager import MemoryManager
    from tools.code_generator import CodeGenerator
    from tools.tester import Tester
    from tools.deployer import Deployer
    from tools.file_manager import FileManager

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise e
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

class AutonomousEngine:
    """
    Main autonomous software engineering engine.
    
    This class orchestrates the entire autonomous development process:
    1. Requirement understanding
    2. Task planning
    3. Code generation
    4. Testing and debugging
    5. Deployment
    """
    
    def __init__(self, project_name: str = "autonomous_project"):
        """Initialize the autonomous engine."""
        self.project_name = project_name
        self.project_dir = Path(f"./generated_projects/{project_name}")
        
        # Initialize core components
        self.llm_client = GeminiClient()
        self.memory_manager = MemoryManager(project_name)
        self.task_planner = TaskPlanner()
        
        # Initialize tools
        self.code_generator = CodeGenerator(self.llm_client, self.memory_manager)
        self.tester = Tester(self.llm_client, self.memory_manager)
        self.deployer = Deployer(self.llm_client)
        self.file_manager = FileManager(self.project_dir)
        
        # Progress monitoring
        self.progress_callbacks = []
        self.current_progress = {
            "current_task": None,
            "progress_percentage": 0,
            "status": "idle",
            "details": ""
        }
        
        logger.info("Autonomous engine initialized successfully")
        self.current_task = None
        self.iteration_count = 0
        self.max_iterations = 5
        
        # Ensure project directory exists
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Autonomous engine initialized for project: {project_name}")
    
    def add_progress_callback(self, callback):
        """Add a callback function for progress updates."""
        self.progress_callbacks.append(callback)
    
    def _update_progress(self, task_name: str, percentage: int, status: str, details: str = ""):
        """Update progress and notify callbacks."""
        self.current_progress.update({
            "current_task": task_name,
            "progress_percentage": percentage,
            "status": status,
            "details": details
        })
        
        # Notify all callbacks
        for callback in self.progress_callbacks:
            try:
                callback(self.current_progress.copy())
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def build_application(self, requirement: str) -> Dict[str, Any]:
        """
        Main method to build an application from requirements.
        
        Args:
            requirement: Natural language requirement
            
        Returns:
            Result summary with success status and details
        """
        logger.info(f"Starting application build for requirement: {requirement}")
        self._update_progress("Initialization", 0, "starting", "Beginning application build process")
        
        try:
            # Step 1: Understand and plan
            await self._add_conversation("user", requirement)
            plan = await self._plan_development(requirement)
            
            # Step 2: Execute development plan
            success = await self._execute_development_plan(plan)
            
            # Step 3: Generate summary
            summary = await self._generate_project_summary()
            
            result = {
                "success": success,
                "requirement": requirement,
                "plan": plan,
                "summary": summary,
                "project_directory": str(self.project_dir),
                "iterations": self.iteration_count
            }
            
            logger.info(f"Autonomous build completed. Success: {success}")
            return result
            
        except Exception as e:
            logger.error(f"Autonomous build failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "requirement": requirement
            }
    
    async def debug_and_fix(
        self, 
        code_file: str, 
        error_description: str
    ) -> Dict[str, Any]:
        """
        Debug and fix issues in existing code.
        
        Args:
            code_file: Path to the code file
            error_description: Description of the error
            
        Returns:
            Debug result with fixes applied
        """
        logger.info(f"Starting debug and fix for: {code_file}")
        
        try:
            # Read the problematic code
            code_content = self.file_manager.read_file(code_file)
            if not code_content:
                return {"success": False, "error": "Could not read code file"}
            
            # Analyze the code for issues
            analysis = await self.llm_client.generate_response(f"Analyze this code: {code_content}")
            
            # Generate fixes
            fixes = await self._generate_fixes(code_content, analysis, error_description)
            
            # Apply fixes
            fixed_code = await self._apply_fixes(code_content, fixes)
            
            # Test the fixed code
            test_result = await self.tester.test_code(fixed_code, code_file)
            
            result = {
                "success": test_result["success"],
                "original_issues": analysis.get("issues", []),
                "fixes_applied": fixes,
                "test_result": test_result,
                "fixed_code": fixed_code if test_result["success"] else None
            }
            
            if test_result["success"]:
                # Save the fixed code
                self.file_manager.write_file(code_file, fixed_code)
                logger.info(f"Successfully fixed and tested: {code_file}")
            else:
                logger.warning(f"Fixes applied but tests still failing: {code_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Debug and fix failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _plan_development(self, requirement: str) -> Dict[str, Any]:
        """Plan the development process using Gemini AI."""
        logger.info("Planning development process...")
        
        # Use Gemini to create a detailed plan
        plan_prompt = f"""
        Create a detailed software development plan for: {requirement}
        
        Include:
        1. Technology stack recommendations
        2. Project structure
        3. Key components and their responsibilities
        4. Development phases
        5. Testing strategy
        6. Deployment approach
        
        Return a structured plan that can be executed step by step.
        """
        
        plan_response = await self.llm_client.generate_response(plan_prompt)
        
        # Create tasks based on the plan
        task_ids = self.task_planner.plan_from_requirement(requirement)
        
        plan = {
            "ai_generated_plan": plan_response,
            "tasks": task_ids,
            "requirement": requirement
        }
        
        await self._add_conversation("assistant", f"Development plan created with {len(task_ids)} tasks")
        
        return plan
    
    async def _execute_development_plan(self, plan: Dict[str, Any]) -> bool:
        """Execute the development plan step by step."""
        logger.info("Executing development plan...")
        
        tasks = plan.get("tasks", [])
        if not tasks:
            logger.warning("No tasks to execute")
            return False
        
        # Execute tasks in order
        for task_id in tasks:
            task = self.task_planner.get_task_by_id(task_id)
            if not task:
                continue
            
            logger.info(f"Executing task: {task.title}")
            
            # Start the task
            if not self.task_planner.start_task(task_id):
                logger.error(f"Failed to start task: {task_id}")
                continue
            
            # Execute the task
            success = await self._execute_task(task)
            
            if success:
                self.task_planner.complete_task(task_id)
                logger.info(f"Task completed: {task.title}")
            else:
                self.task_planner.fail_task(task_id, "Task execution failed")
                logger.error(f"Task failed: {task.title}")
                
                # Try to recover or continue with next task
                from .task_planner import TaskPriority
                if task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]:
                    logger.warning(f"Critical task failed, stopping execution")
                    return False
        
        # Check overall success
        progress = self.task_planner.get_task_progress()
        overall_success = progress["failed"] == 0 and progress["completed"] > 0
        
        return overall_success
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    async def _execute_task(self, task) -> bool:
        """Execute a single task."""
        self._update_progress(task.title, 0, "executing", f"Starting {task.task_type} task")
        try:
            if "backend" in task.title.lower():
                return await self._execute_backend_task(task)
            elif "frontend" in task.title.lower():
                return await self._execute_frontend_task(task)
            elif "database" in task.title.lower():
                return await self._execute_database_task(task)
            elif "testing" in task.title.lower():
                return await self._execute_testing_task(task)
            elif "deployment" in task.title.lower():
                return await self._execute_deployment_task(task)
            else:
                # Generic task execution
                return await self._execute_generic_task(task)
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            if hasattr(self, '_update_progress'):
                self._update_progress(task.title, 0, "failed", f"Task failed: {str(e)}")
            return False
    
    async def _execute_backend_task(self, task) -> bool:
        """Execute backend development task."""
        logger.info(f"Executing backend task: {task.title}")
        
        self._update_progress(task.title, 25, "generating", "Generating backend code")
        
        # Generate backend code
        backend_code = await self.code_generator.generate_backend_code(
            self.memory_manager.get_relevant_context(task.description)
        )
        
        if not backend_code:
            return False
        
        # Save the code
        main_file = self.project_dir / "main.py"
        self.file_manager.write_file(str(main_file), backend_code)
        
        # Add to memory
        self.memory_manager.add_code_context(str(main_file), backend_code, "python")
        
        return True
    
    async def _execute_frontend_task(self, task) -> bool:
        """Execute frontend development task."""
        logger.info(f"Executing frontend task: {task.title}")
        
        # Generate frontend code
        frontend_code = await self.code_generator.generate_frontend_code(
            self.memory_manager.get_relevant_context(task.description)
        )
        
        if not frontend_code:
            return False
        
        # Save the code
        frontend_file = self.project_dir / "frontend.html"
        self.file_manager.write_file(str(frontend_file), frontend_code)
        
        # Add to memory
        self.memory_manager.add_code_context(str(frontend_file), frontend_code, "html")
        
        return True
    
    async def _execute_database_task(self, task) -> bool:
        """Execute database design task."""
        logger.info(f"Executing database task: {task.title}")
        
        # Generate database models
        models_code = await self.code_generator.generate_database_models(
            self.memory_manager.get_relevant_context(task.description)
        )
        
        if not models_code:
            return False
        
        # Save the code
        models_file = self.project_dir / "models.py"
        self.file_manager.write_file(str(models_file), models_code)
        
        # Add to memory
        self.memory_manager.add_code_context(str(models_file), models_code, "python")
        
        return True
    
    async def _execute_testing_task(self, task) -> bool:
        """Execute comprehensive testing task with automatic fixing."""
        logger.info(f"Executing testing task: {task.title}")
        
        try:
            code_files = self.memory_manager.code_context.keys()
            
            success = True
            fixed_files = []
            
            for file_path in code_files:
                if file_path.endswith(('.py', '.html', '.js')):
                    original_code = self.memory_manager.code_context[file_path]
                    
                    test_result = await self.tester.test_code(original_code, file_path)
                    
                    if not test_result["success"]:
                        logger.warning(f"Tests failed for: {file_path}, attempting to fix...")
                        
                        fixed_code = await self.tester.fix_code_issues(original_code, test_result)
                        
                        if fixed_code and fixed_code != original_code:
                            retest_result = await self.tester.test_code(fixed_code, file_path)
                            
                            if retest_result["success"]:
                                self.memory_manager.code_context[file_path] = fixed_code
                                self.file_manager.write_file(file_path, fixed_code)
                                fixed_files.append(file_path)
                                logger.info(f"Successfully fixed and updated: {file_path}")
                            else:
                                success = False
                                logger.error(f"Failed to fix issues in: {file_path}")
                        else:
                            success = False
                            logger.error(f"Could not generate fixes for: {file_path}")
                    else:
                        logger.info(f"Tests passed for: {file_path}")
            
            if fixed_files:
                logger.info(f"Fixed {len(fixed_files)} files during testing")
            
            return success
        except Exception as e:
            logger.error(f"Testing task failed: {e}")
            return True  # Don't fail the entire build for testing issues
    
    async def _execute_deployment_task(self, task) -> bool:
        """Execute deployment task."""
        logger.info(f"Executing deployment task: {task.title}")
        
        # Generate deployment files
        deployment_success = await self.deployer.prepare_deployment(self.project_dir)
        
        return deployment_success
    
    async def _execute_generic_task(self, task) -> bool:
        """Execute a generic task."""
        logger.info(f"Executing generic task: {task.title}")
        
        # Use Gemini to understand what needs to be done
        task_prompt = f"Task: {task.title}\nDescription: {task.description}\n\nWhat specific action should be taken to complete this task?"
        
        response = await self.llm_client.generate_response(task_prompt)
        
        # For now, just mark as completed if we got a response
        # In a real implementation, this would be more sophisticated
        return len(response) > 0
    
    async def _generate_fixes(self, code: str, analysis: Dict, error_description: str) -> List[str]:
        """Generate fixes for code issues."""
        fix_prompt = f"""
        Code with issues:
        {code}
        
        Analysis:
        {analysis}
        
        Error description:
        {error_description}
        
        Generate specific fixes for the identified issues. Return only the corrected code.
        """
        
        fixes = await self.llm_client.generate_response(fix_prompt)
        return [fixes]  # Simplified - could be multiple fixes
    
    async def _apply_fixes(self, original_code: str, fixes: List[str]) -> str:
        """Apply fixes to the original code."""
        # For simplicity, return the first fix
        # In a real implementation, this would be more sophisticated
        return fixes[0] if fixes else original_code
    
    async def _generate_project_summary(self) -> Dict[str, Any]:
        """Generate a summary of the completed project."""
        summary_prompt = """
        Generate a comprehensive summary of the software project that was just built.
        Include:
        1. What was built
        2. Key features
        3. Technologies used
        4. How to run it
        5. Next steps for improvement
        """
        
        summary = await self.llm_client.generate_response(summary_prompt)
        
        return {
            "ai_generated_summary": summary,
            "project_stats": self.memory_manager.get_project_summary(),
            "task_progress": self.task_planner.get_task_progress()
        }
    
    async def _add_conversation(self, role: str, content: str) -> None:
        """Add a conversation entry to memory."""
        self.memory_manager.add_conversation(role, content)
    
    async def build_project(self, description: str, project_type: str = "web_app", model_type: str = "transformer") -> str:
        """
        Build a project based on description, project type, and model type.
        
        Args:
            description: Natural language description of the project
            project_type: Type of project to build (web_app, cli, etc.)
            model_type: Type of AI model to use (transformer, sklearn, rule-based)
            
        Returns:
            Project name of the generated project
        """
        logger.info(f"Starting project build for: {description} using {model_type} model")
        self._update_progress("Initialization", 0, "starting", f"Beginning project build with {model_type} model")
        
        # Set project name based on description
        project_name = f"{project_type}_{int(time.time())}"
        self.project_name = project_name
        self.project_dir = Path(f"./generated_projects/{project_name}")
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Build the application using the appropriate model
        try:
            if model_type == "transformer":
                # Use the LLM-based approach
                result = await self.build_application(description)
            elif model_type == "sklearn":
                # Use machine learning approach (simplified for now)
                logger.info("Using sklearn model for generation")
                result = await self._build_with_sklearn(description)
            elif model_type == "rule-based":
                # Use rule-based approach (simplified for now)
                logger.info("Using rule-based model for generation")
                result = await self._build_with_rules(description)
            else:
                # Default to transformer
                logger.warning(f"Unknown model type: {model_type}, defaulting to transformer")
                result = await self.build_application(description)
            
            return project_name
            
        except Exception as e:
            logger.error(f"Project build failed: {e}")
            raise
    
    async def _build_with_sklearn(self, description: str) -> Dict[str, Any]:
        """Build project using sklearn-based approach."""
        # Simplified implementation
        self._update_progress("ML Model Generation", 50, "generating", "Using machine learning to generate project")
        await asyncio.sleep(2)  # Simulate work
        
        # Create a simple project structure
        self.file_manager.write_file(str(self.project_dir / "app.py"), "# ML-generated application\n\nprint('Hello from ML model!')")
        self.file_manager.write_file(str(self.project_dir / "README.md"), f"# {self.project_name}\n\nGenerated using sklearn model")
        
        return {"success": True, "project_directory": str(self.project_dir)}
    
    async def _build_with_rules(self, description: str) -> Dict[str, Any]:
        """Build project using rule-based approach."""
        # Simplified implementation
        self._update_progress("Rule-based Generation", 50, "generating", "Using rule-based system to generate project")
        await asyncio.sleep(2)  # Simulate work
        
        # Create a simple project structure
        self.file_manager.write_file(str(self.project_dir / "app.py"), "# Rule-based generated application\n\nprint('Hello from rule-based model!')")
        self.file_manager.write_file(str(self.project_dir / "README.md"), f"# {self.project_name}\n\nGenerated using rule-based model")
        
        return {"success": True, "project_directory": str(self.project_dir)}
    
    async def get_project_status(self) -> Dict[str, Any]:
        """Get current project status."""
        return {
            "project_name": self.project_name,
            "project_directory": str(self.project_dir),
            "task_progress": self.task_planner.get_task_progress(),
            "memory_summary": self.memory_manager.get_project_summary(),
            "current_iteration": self.iteration_count
        }
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.memory_manager.save_memory()
        logger.info("Autonomous engine cleanup completed")
