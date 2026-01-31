"""Search tool."""

from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger(__name__)


class SearchTool:
    """Tool for searching files and content."""

    def __init__(self, base_path: str = "."):
        """Initialize search tool.

        Args:
            base_path: Base path for search operations
        """
        self.base_path = Path(base_path)

    @tool
    def search_files(
        self, pattern: str, path: Optional[str] = None
    ) -> str:
        """Search for files matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "*.py")
            path: Base path for search (default: current directory)

        Returns:
            List of matching files
        """
        try:
            search_path = self.base_path / (path or ".")
            matches = list(search_path.glob(pattern))
            if not matches:
                return f"No files found matching: {pattern}"
            return "\n".join(str(m.relative_to(self.base_path)) for m in matches)
        except Exception as e:
            return f"Error searching for {pattern}: {e}"

    @tool
    def grep(
        self,
        query: str,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> str:
        """Search for text in files.

        Args:
            query: Search query
            path: Base path for search
            file_type: File extension filter (e.g., "py", "md")
            case_sensitive: Whether search is case-sensitive

        Returns:
            Matching lines with file paths
        """
        try:
            search_path = self.base_path / (path or ".")
            results = []

            # Determine extensions to search
            extensions = []
            if file_type:
                extensions = [f".{file_type}"]

            for filepath in search_path.rglob("*"):
                if filepath.is_file():
                    if extensions and filepath.suffix not in extensions:
                        continue

                    try:
                        content = filepath.read_text()
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if (case_sensitive and query in line) or (
                                not case_sensitive and query.lower() in line.lower()
                            ):
                                rel_path = filepath.relative_to(self.base_path)
                                results.append(f"{rel_path}:{i}: {line.rstrip()}")
                    except Exception:
                        continue

            if not results:
                return f"No matches found for: {query}"
            return "\n".join(results[:50])  # Limit results
        except Exception as e:
            return f"Error searching for '{query}': {e}"
