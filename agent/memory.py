"""Memory System for Amy Agent.

Manages semantic and episodic memory stored in markdown files.
"""

import os
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class MemorySystem:
    """Manages semantic and episodic memory for the agent."""

    def __init__(
        self,
        semantic_file: str = "memory/semantic_memory.md",
        episodic_dir: str = "memory/episodic",
    ):
        """Initialize memory system.

        Args:
            semantic_file: Path to semantic memory markdown file
            episodic_dir: Directory for episodic memory files
        """
        self.semantic_file = Path(semantic_file)
        self.episodic_dir = Path(episodic_dir)

        # Ensure directories exist
        self.episodic_dir.mkdir(parents=True, exist_ok=True)
        if not self.semantic_file.exists():
            self.semantic_file.parent.mkdir(parents=True, exist_ok=True)
            self._init_semantic_memory()

    def _init_semantic_memory(self) -> None:
        """Initialize semantic memory file with header."""
        content = """# Semantic Memory

This file stores general knowledge and facts about the user.

## User Profile

- **Name**: (to be filled)
- **Preferences**: (to be filled)
- **Goals**: (to be filled)
- **Background**: (to be filled)

## Knowledge Base

### Preferences
-

### Skills
-

### Projects
-

## Learning Notes

"""
        self.semantic_file.write_text(content)
        logger.info("Initialized semantic memory", path=str(self.semantic_file))

    def _get_episodic_filename(self, d: Optional[date] = None) -> str:
        """Get filename for episodic memory.

        Args:
            d: Date for the episodic memory (default: today)

        Returns:
            Filename in YYYY-MM-DD.md format
        """
        if d is None:
            d = date.today()
        return f"{d.isoformat()}.md"

    def read_semantic_memory(self) -> str:
        """Read all semantic memory.

        Returns:
            Semantic memory content as string
        """
        if not self.semantic_file.exists():
            return ""
        return self.semantic_file.read_text()

    def write_semantic_memory(self, content: str, append: bool = True) -> None:
        """Write to semantic memory.

        Args:
            content: Content to write
            append: If True, append to existing content
        """
        if append and self.semantic_file.exists():
            existing = self.semantic_file.read_text()
            content = f"{existing}\n\n{content}"
        self.semantic_file.write_text(content)
        logger.info("Updated semantic memory", path=str(self.semantic_file))

    def read_episodic_memory(self, d: Optional[date] = None) -> str:
        """Read episodic memory for a specific day.

        Args:
            d: Date to read (default: today)

        Returns:
            Episodic memory content or empty string if not found
        """
        filename = self._get_episodic_filename(d)
        filepath = self.episodic_dir / filename
        if not filepath.exists():
            return ""
        return filepath.read_text()

    def write_episodic_memory(
        self, content: str, d: Optional[date] = None, append: bool = True
    ) -> None:
        """Write to episodic memory for a specific day.

        Args:
            content: Content to write
            d: Date to write to (default: today)
            append: If True, append to existing content
        """
        filename = self._get_episodic_filename(d)
        filepath = self.episodic_dir / filename

        if append and filepath.exists():
            existing = filepath.read_text()
            content = f"{existing}\n\n{content}"

        # Add header if new file
        if not filepath.exists():
            header = f"# {d.isoformat() if d else date.today().isoformat()}\n\n"
            content = header + content

        filepath.write_text(content)
        logger.info("Updated episodic memory", path=str(filepath))

    def get_recent_episodic_memories(
        self, days: int = 7, max_entries: int = 10
    ) -> list[str]:
        """Get recent episodic memories from last N days.

        Args:
            days: Number of days to look back
            max_entries: Maximum number of entries to return

        Returns:
            List of episodic memory entries
        """
        memories = []
        today = date.today()

        for i in range(days):
            d = today.fromordinal(today.toordinal() - i)
            content = self.read_episodic_memory(d)
            if content.strip():
                memories.append(content)

            if len(memories) >= max_entries:
                break

        return memories

    def search_memory(self, query: str) -> list[str]:
        """Search across all memories.

        Args:
            query: Search query

        Returns:
            List of matching memory entries
        """
        # Simple text-based search
        query_lower = query.lower()
        results = []

        # Search semantic memory
        semantic = self.read_semantic_memory()
        if query_lower in semantic.lower():
            results.append(f"## Semantic Memory Match\n\n{semantic}")

        # Search episodic memories (last 30 days)
        for i in range(30):
            d = date.today().fromordinal(date.today().toordinal() - i)
            episodic = self.read_episodic_memory(d)
            if query_lower in episodic.lower():
                results.append(f"## {d.isoformat()}\n\n{episodic}")

        return results

    def add_conversation_turn(self, role: str, content: str) -> None:
        """Add a conversation turn to episodic memory.

        Args:
            role: Role (user/assistant)
            content: Message content
        """
        timestamp = datetime.now().isoformat()
        entry = f"### [{timestamp}] {role.upper()}\n\n{content}"
        self.write_episodic_memory(entry, append=True)
