"""Main autonomous engine that orchestrates the LLM-driven software development process"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import time
from functools import wraps
from pathlib import Path

from src.core.autonomous_engine import AutonomousEngine as CoreAutonomousEngine

logger = logging.getLogger(__name__)

class AutonomousEngine(CoreAutonomousEngine):
    """Wrapper for the core AutonomousEngine class"""
    
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