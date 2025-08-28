"""File system management tools."""
import logging
from pathlib import Path
from typing import Optional

class FileManager:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read a file and return its contents."""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                return file_path.read_text()
            return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file."""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return True
        except Exception as e:
            logging.error(f"Error writing file {file_path}: {e}")
            return False
