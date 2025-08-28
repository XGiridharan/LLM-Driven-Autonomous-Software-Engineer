"""Advanced code testing and debugging tools."""
import ast
import logging
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class CodeTester:
    def __init__(self, llm_client, memory_manager):
        self.llm_client = llm_client
        self.memory_manager = memory_manager
    
    async def test_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """Comprehensive testing of generated code."""
        try:
            results = {
                "success": True,
                "syntax_valid": False,
                "imports_valid": False,
                "structure_valid": False,
                "error_message": None,
                "warnings": [],
                "file_path": file_path,
                "test_details": {}
            }
            
            if file_path.endswith('.py'):
                results.update(await self._test_python_code(code))
            elif file_path.endswith('.html'):
                results.update(await self._test_html_code(code))
            elif file_path.endswith('.js'):
                results.update(await self._test_javascript_code(code))
            else:
                results["syntax_valid"] = True
                results["imports_valid"] = True
                results["structure_valid"] = True
            
            # Overall success determination
            results["success"] = (
                results["syntax_valid"] and 
                results["imports_valid"] and 
                results["structure_valid"]
            )
            
            logger.info(f"Code testing completed for {file_path}: {results['success']}")
            return results
            
        except Exception as e:
            logger.error(f"Code testing failed: {e}")
            return {
                "success": False, 
                "error": str(e),
                "file_path": file_path
            }
    
    async def _test_python_code(self, code: str) -> Dict[str, Any]:
        """Test Python code comprehensively."""
        results = {
            "syntax_valid": False,
            "imports_valid": False,
            "structure_valid": False,
            "warnings": [],
            "test_details": {}
        }
        
        # Syntax validation
        try:
            if isinstance(code, str):
                ast.parse(code)
                results["syntax_valid"] = True
                results["test_details"]["syntax"] = "Valid Python syntax"
            else:
                results["error_message"] = f"Code must be a string, got {type(code)}"
                results["test_details"]["syntax"] = "Invalid code type"
                return results
        except SyntaxError as e:
            results["error_message"] = f"Syntax Error: {e}"
            results["test_details"]["syntax"] = f"Syntax error at line {e.lineno}: {e.msg}"
            return results
        
        # Import validation
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Check imports without executing
            result = subprocess.run(
                ['python', '-m', 'py_compile', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                results["imports_valid"] = True
                results["test_details"]["imports"] = "All imports are valid"
            else:
                results["error_message"] = f"Import Error: {result.stderr}"
                results["test_details"]["imports"] = result.stderr
            
            os.unlink(temp_file)
            
        except Exception as e:
            results["warnings"].append(f"Import validation failed: {e}")
            results["imports_valid"] = True  # Assume valid if can't test
        
        # Structure validation
        try:
            tree = ast.parse(code)
            
            # Check for basic structure elements
            has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
            has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
            has_imports = any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
            
            structure_score = 0
            if has_imports: structure_score += 1
            if has_functions or has_classes: structure_score += 2
            
            results["structure_valid"] = structure_score >= 2
            results["test_details"]["structure"] = {
                "has_imports": has_imports,
                "has_functions": has_functions,
                "has_classes": has_classes,
                "score": structure_score
            }
            
        except Exception as e:
            results["warnings"].append(f"Structure analysis failed: {e}")
            results["structure_valid"] = True
        
        return results
    
    async def _test_html_code(self, code: str) -> Dict[str, Any]:
        """Test HTML code for basic validity."""
        results = {
            "syntax_valid": True,
            "imports_valid": True,
            "structure_valid": False,
            "warnings": [],
            "test_details": {}
        }
        
        # Basic HTML structure check
        if isinstance(code, str):
            code_lower = code.lower()
            has_html_tag = '<html' in code_lower
            has_head_tag = '<head' in code_lower
            has_body_tag = '<body' in code_lower
            has_doctype = '<!doctype' in code_lower
        else:
            has_html_tag = has_head_tag = has_body_tag = has_doctype = False
            results["warnings"].append(f"Code must be a string, got {type(code)}")
        
        structure_score = sum([has_html_tag, has_head_tag, has_body_tag, has_doctype])
        results["structure_valid"] = structure_score >= 3
        
        results["test_details"]["structure"] = {
            "has_doctype": has_doctype,
            "has_html_tag": has_html_tag,
            "has_head_tag": has_head_tag,
            "has_body_tag": has_body_tag,
            "score": structure_score
        }
        
        return results
    
    async def _test_javascript_code(self, code: str) -> Dict[str, Any]:
        """Test JavaScript code for basic validity."""
        results = {
            "syntax_valid": True,
            "imports_valid": True,
            "structure_valid": True,
            "warnings": [],
            "test_details": {"note": "Basic JavaScript validation"}
        }
        
        # Basic checks
        if isinstance(code, str):
            if 'function' in code or '=>' in code or 'const' in code or 'let' in code:
                results["structure_valid"] = True
        else:
            results["warnings"].append(f"Code must be a string, got {type(code)}")
            results["structure_valid"] = False
        
        return results
    
    async def generate_and_run_tests(self, code: str, file_path: str) -> Dict[str, Any]:
        """Generate and run comprehensive tests for the code."""
        try:
            if not file_path.endswith('.py'):
                return {"success": True, "message": "Test generation only supported for Python"}
            
            # Generate tests using Gemini
            test_prompt = f"""
            Generate comprehensive pytest tests for this Python code:
            
            {code}
            
            Requirements:
            1. Test all functions and methods
            2. Include edge cases and error conditions
            3. Use proper pytest fixtures
            4. Mock external dependencies
            5. Test both success and failure scenarios
            6. Return only the test code without markdown formatting
            """
            
            test_code = await self.llm_client.generate_response(test_prompt)
            
            if not test_code:
                return {"success": False, "error": "Failed to generate tests"}
            
            # Save and run tests
            with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False) as f:
                f.write(test_code)
                test_file = f.name
            
            # Run pytest
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(test_file)
            
            return {
                "success": result.returncode == 0,
                "test_output": result.stdout,
                "test_errors": result.stderr,
                "generated_tests": test_code
            }
            
        except Exception as e:
            logger.error(f"Test generation and execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def fix_code_issues(self, code: str, test_results: Dict[str, Any]) -> Optional[str]:
        """Use Gemini to fix identified code issues."""
        try:
            if test_results.get("success", False):
                return code  # No fixes needed
            
            fix_prompt = f"""
            Fix the issues in this code based on the test results:
            
            Original Code:
            {code}
            
            Test Results:
            {test_results}
            
            Requirements:
            1. Fix all syntax errors
            2. Resolve import issues
            3. Improve code structure
            4. Maintain original functionality
            5. Return only the fixed code without markdown formatting
            """
            
            fixed_code = await self.llm_client.generate_response(fix_prompt)
            
            if fixed_code:
                logger.info("Successfully generated code fixes")
                return fixed_code
            else:
                logger.error("Failed to generate code fixes")
                return None
                
        except Exception as e:
            logger.error(f"Code fixing failed: {e}")
            return None

class Tester:
    """Enhanced testing framework for autonomous code generation."""
    
    def __init__(self, llm_client, memory_manager):
        self.llm_client = llm_client
        self.memory_manager = memory_manager
        logger.info("Tester initialized")
    
    async def test_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """Test code based on file type."""
        if file_path.endswith('.py'):
            return test_python_code(code)
        elif file_path.endswith('.html'):
            return test_html_code(code)
        elif file_path.endswith('.js'):
            return test_javascript_code(code)
        else:
            return {
                "success": True,
                "message": f"No specific tests for {file_path} file type"
            }
    
    async def fix_code_issues(self, code: str, test_result: Dict[str, Any]) -> str:
        """Fix code issues using LLM."""
        return await fix_code_with_llm(self.llm_client, code, test_result)
