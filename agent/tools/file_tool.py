"""File operations tool."""

from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger(__name__)


class FileTool:
    """Tool for file operations."""

    def __init__(self, base_path: str = "."):
        """Initialize file tool.

        Args:
            base_path: Base path for file operations
        """
        self.base_path = Path(base_path)

    @tool
    def read_file(self, path: str) -> str:
        """Read a file's contents.

        Args:
            path: Relative path to the file

        Returns:
            File contents or error message
        """
        try:
            filepath = self.base_path / path
            if not filepath.exists():
                return f"Error: File not found: {path}"
            return filepath.read_text()
        except Exception as e:
            return f"Error reading file {path}: {e}"

    @tool
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file.

        Args:
            path: Relative path to the file
            content: Content to write

        Returns:
            Success or error message
        """
        try:
            filepath = self.base_path / path
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
            logger.info("Wrote file", path=path)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file {path}: {e}"

    @tool
    def list_directory(self, path: str = ".") -> str:
        """List contents of a directory.

        Args:
            path: Relative path to directory

        Returns:
            Directory listing
        """
        try:
            dirpath = self.base_path / path
            if not dirpath.exists() or not dirpath.is_dir():
                return f"Error: Directory not found: {path}"

            items = []
            for item in sorted(dirpath.iterdir()):
                item_type = "DIR" if item.is_dir() else "FILE"
                items.append(f"[{item_type}] {item.name}")

            return "\n".join(items) if items else "(empty directory)"
        except Exception as e:
            return f"Error listing directory {path}: {e}"

    @tool
    def create_directory(self, path: str) -> str:
        """Create a directory.

        Args:
            path: Relative path for the new directory

        Returns:
            Success or error message
        """
        try:
            dirpath = self.base_path / path
            dirpath.mkdir(parents=True, exist_ok=True)
            logger.info("Created directory", path=path)
            return f"Successfully created directory: {path}"
        except Exception as e:
            return f"Error creating directory {path}: {e}"
