"""Deployment automation tools."""
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Deployer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def prepare_deployment(self, project_dir: Path, project_context: Optional[str] = None) -> Dict[str, Any]:
        """Prepare comprehensive deployment files for the project."""
        try:
            logger.info(f"Preparing deployment for project: {project_dir}")
            
            # Generate smart requirements.txt based on project context
            requirements = await self._generate_requirements(project_dir, project_context)
            requirements_file = project_dir / "requirements.txt"
            requirements_file.write_text(requirements)
            
            # Generate optimized Dockerfile
            dockerfile_content = await self._generate_dockerfile(project_context)
            dockerfile = project_dir / "Dockerfile"
            dockerfile.write_text(dockerfile_content)
            
            # Generate docker-compose.yml for development
            compose_content = await self._generate_docker_compose(project_context)
            compose_file = project_dir / "docker-compose.yml"
            compose_file.write_text(compose_content)
            
            # Generate deployment scripts
            await self._generate_deployment_scripts(project_dir)
            
            # Generate health check endpoint if not exists
            await self._ensure_health_check(project_dir)
            
            return {
                "success": True,
                "files_created": ["requirements.txt", "Dockerfile", "docker-compose.yml", "deploy.sh"],
                "message": "Deployment files prepared successfully"
            }
            
        except Exception as e:
            logger.error(f"Deployment preparation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Deployment preparation failed: {e}"
            }
    
    async def _generate_requirements(self, project_dir: Path, context: Optional[str]) -> str:
        """Generate smart requirements.txt based on project analysis."""
        prompt = f"""
        Analyze the following project and generate a comprehensive requirements.txt file.
        
        Project context: {context or 'FastAPI web application'}
        
        Include all necessary dependencies with appropriate versions for:
        - Web framework (FastAPI)
        - Database (SQLAlchemy, asyncpg for PostgreSQL or aiosqlite for SQLite)
        - Authentication and security
        - Testing frameworks
        - Development tools
        - Any other dependencies based on the project context
        
        Return ONLY the requirements.txt content, one package per line with versions.
        """
        
        requirements = await self.llm_client.generate_response(prompt)
        
        # Fallback to basic requirements if generation fails
        if not requirements or "error" in requirements.lower():
            requirements = """fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.23
aiosqlite>=0.19.0
pydantic>=2.5.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pytest>=7.4.3
pytest-asyncio>=0.21.1
httpx>=0.25.2"""
        
        return requirements
    
    async def _generate_dockerfile(self, context: Optional[str]) -> str:
        """Generate optimized Dockerfile."""
        prompt = f"""
        Generate an optimized Dockerfile for a FastAPI application.
        
        Project context: {context or 'FastAPI web application'}
        
        Requirements:
        - Use Python 3.11 slim image for smaller size
        - Multi-stage build for optimization
        - Non-root user for security
        - Proper caching of dependencies
        - Health check
        - Expose port 8000
        
        Return ONLY the Dockerfile content.
        """
        
        dockerfile = await self.llm_client.generate_response(prompt)
        
        # Fallback Dockerfile
        if not dockerfile or "error" in dockerfile.lower():
            dockerfile = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]"""
        
        return dockerfile
    
    async def _generate_docker_compose(self, context: Optional[str]) -> str:
        """Generate docker-compose.yml for development."""
        compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - .:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:"""
        
        return compose
    
    async def _generate_deployment_scripts(self, project_dir: Path):
        """Generate deployment scripts."""
        # Deploy script
        deploy_script = """#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t my-app .

echo "Starting application..."
docker-compose up -d

echo "Application deployed successfully!"
echo "Access your app at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"""
        
        deploy_file = project_dir / "deploy.sh"
        deploy_file.write_text(deploy_script)
        deploy_file.chmod(0o755)
        
        # Stop script
        stop_script = """#!/bin/bash
echo "Stopping application..."
docker-compose down
echo "Application stopped."""
        
        stop_file = project_dir / "stop.sh"
        stop_file.write_text(stop_script)
        stop_file.chmod(0o755)
    
    async def _ensure_health_check(self, project_dir: Path):
        """Ensure health check endpoint exists in main.py."""
        main_file = project_dir / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            if "/health" not in content:
                # Add health check endpoint
                health_endpoint = "\n\n@app.get(\"/health\", tags=[\"Health\"])\nasync def health_check():\n    return {\"status\": \"healthy\"}"
                content += health_endpoint
                main_file.write_text(content)
    
    async def deploy_to_cloud(self, project_dir: Path, platform: str = "docker") -> Dict[str, Any]:
        """Deploy application to cloud platform."""
        try:
            logger.info(f"Deploying to {platform}...")
            
            if platform == "docker":
                return await self._deploy_docker(project_dir)
            elif platform == "heroku":
                return await self._deploy_heroku(project_dir)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
        except Exception as e:
            logger.error(f"Cloud deployment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _deploy_docker(self, project_dir: Path) -> Dict[str, Any]:
        """Deploy using Docker."""
        try:
            # Build image
            result = subprocess.run(
                ["docker", "build", "-t", "my-app", "."],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Docker build failed: {result.stderr}"
                }
            
            # Start with docker-compose
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Docker deployment failed: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": "Application deployed successfully with Docker",
                "url": "http://localhost:8000",
                "docs_url": "http://localhost:8000/docs"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _deploy_heroku(self, project_dir: Path) -> Dict[str, Any]:
        """Deploy to Heroku (placeholder for future implementation)."""
        return {
            "success": False,
            "error": "Heroku deployment not yet implemented"
        }
