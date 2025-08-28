"""
Code generation tools for the autonomous software engineer
"""
import logging
try:
    from config.settings import settings
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from config.settings import settings
from typing import Optional, Dict, Any

from core.gemini_client import GeminiClient
from core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Generates code using Gemini AI based on requirements and context."""
    
    def __init__(self, gemini_client: GeminiClient, memory_manager: MemoryManager):
        """Initialize the code generator."""
        self.llm_client = gemini_client
        self.memory_manager = memory_manager
    
    async def generate_backend_code(self, context: str) -> Optional[str]:
        """
        Generate backend code (FastAPI) based on context.
        
        Args:
            context: Context about what needs to be built
            
        Returns:
            Generated Python code or None if failed
        """
        try:
            prompt = f"""
            Generate a complete FastAPI backend application based on this context:
            
            {context}
            
            Requirements:
            1. Use FastAPI framework
            2. Include proper error handling
            3. Add input validation with Pydantic
            4. Include comprehensive logging
            5. Add CORS middleware
            6. Include health check endpoint
            7. Use async/await patterns
            8. Add proper documentation strings
            
            Return only the Python code, no explanations.
            """
            
            code = await self.llm_client.generate_response(prompt)
            
            if code:
                logger.info("Successfully generated backend code")
                return code
            else:
                logger.error("Failed to generate backend code")
                return None
                
        except Exception as e:
            logger.error(f"Error generating backend code: {e}")
            return None
    
    async def generate_frontend_code(self, context: str) -> Optional[str]:
        """
        Generate frontend code (HTML/CSS/JS) based on context.
        
        Args:
            context: Context about what needs to be built
            
        Returns:
            Generated HTML code or None if failed
        """
        try:
            prompt = f"""
            Generate a complete HTML frontend application based on this context:
            
            {context}
            
            Requirements:
            1. Use modern HTML5
            2. Include responsive CSS
            3. Add interactive JavaScript
            4. Use Bootstrap or modern CSS framework
            5. Include proper form validation
            6. Add loading states and error handling
            7. Make it mobile-friendly
            8. Include proper accessibility features
            
            Return only the HTML code with embedded CSS and JavaScript without markdown formatting, no explanations.
            """
            
            code = await self.llm_client.generate_response(prompt)
            
            if code:
                logger.info("Successfully generated frontend code")
                return code
            else:
                logger.error("Failed to generate frontend code")
                return None
                
        except Exception as e:
            logger.error(f"Error generating frontend code: {e}")
            return None
    
    async def generate_database_models(self, context: str) -> Optional[str]:
        """
        Generate database models and schema based on context.
        
        Args:
            context: Context about what needs to be built
            
        Returns:
            Generated Python models code or None if failed
        """
        try:
            prompt = f"""
            Generate database models using SQLAlchemy based on this context:
            
            {context}
            
            Requirements:
            1. Use SQLAlchemy ORM
            2. Include proper relationships
            3. Add data validation
            4. Include database migrations setup
            5. Add proper indexes
            6. Include CRUD operations
            7. Add proper error handling
            8. Use async SQLAlchemy if possible
            
            Return only the Python code, no explanations.
            """
            
            code = await self.llm_client.generate_response(prompt)
            
            if code:
                logger.info("Successfully generated database models")
                return code
            else:
                logger.error("Failed to generate database models")
                return None
                
        except Exception as e:
            logger.error(f"Error generating database models: {e}")
            return None
    
    async def generate_tests(self, code: str, language: str = "python") -> Optional[str]:
        """
        Generate test code for existing code.
        
        Args:
            code: The code to test
            language: Programming language of the code
            
        Returns:
            Generated test code or None if failed
        """
        try:
            prompt = f"""
            Generate comprehensive tests for this {language} code:
            
            {code}
            
            Requirements:
            1. Use pytest for Python or appropriate testing framework
            2. Test all functions and methods
            3. Include edge cases and error conditions
            4. Add proper test documentation
            5. Use mocking where appropriate
            6. Include integration tests
            7. Add performance tests if relevant
            8. Ensure high test coverage
            
            Return only the test code without markdown formatting, no explanations.
            """
            
            tests = await self.llm_client.generate_response(prompt)
            
            if tests:
                logger.info("Successfully generated test code")
                return tests
            else:
                logger.error("Failed to generate test code")
                return None
                
        except Exception as e:
            logger.error(f"Error generating test code: {e}")
            return None
    
    async def generate_documentation(self, code: str, language: str = "python") -> Optional[str]:
        """
        Generate documentation for existing code.
        
        Args:
            code: The code to document
            language: Programming language of the code
            
        Returns:
            Generated documentation or None if failed
        """
        try:
            prompt = f"""
            Generate comprehensive documentation for this {language} code:
            
            {code}
            
            Requirements:
            1. Include function/method descriptions
            2. Document parameters and return values
            3. Add usage examples
            4. Include setup and installation instructions
            5. Add troubleshooting section
            6. Include API documentation if applicable
            7. Add code architecture overview
            8. Include contribution guidelines
            
            Return only the documentation without markdown formatting, no explanations.
            """
            
            docs = await self.llm_client.generate_response(prompt)
            
            if docs:
                logger.info("Successfully generated documentation")
                return docs
            else:
                logger.error("Failed to generate documentation")
                return None
                
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return None
    
    async def refactor_code(self, code: str, language: str = "python", improvements: str = "") -> Optional[str]:
        """
        Refactor existing code to improve quality.
        
        Args:
            code: The code to refactor
            language: Programming language of the code
            improvements: Specific improvements to make
            
        Returns:
            Refactored code or None if failed
        """
        try:
            prompt = f"""
            Refactor this {language} code to improve quality:
            
            {code}
            
            Improvements to make:
            {improvements or "General code quality improvements"}
            
            Requirements:
            1. Maintain functionality
            2. Improve readability
            3. Follow best practices
            4. Optimize performance
            5. Reduce complexity
            6. Improve error handling
            7. Add type hints if applicable
            8. Follow PEP 8 or language-specific style guides
            
            Return only the refactored code without markdown formatting, no explanations.
            """
            
            refactored = await self.llm_client.generate_response(prompt)
            
            if refactored:
                logger.info("Successfully refactored code")
                return refactored
            else:
                logger.error("Failed to refactor code")
                return None
                
        except Exception as e:
            logger.error(f"Error refactoring code: {e}")
            return None
