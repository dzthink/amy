"""Summarize skill."""

from langchain_core.tools import tool
import structlog

logger = structlog.get_logger(__name__)


class SummarizeSkill:
    """Skill for summarizing content."""

    def __init__(self, max_length: int = 200):
        """Initialize summarize skill.

        Args:
            max_length: Maximum summary length
        """
        self.max_length = max_length

    @tool
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text content.

        Args:
            text: Text to summarize
            max_length: Maximum summary length

        Returns:
            Summary of the text
        """
        if not text.strip():
            return "Empty text provided."

        # Simple extractive summarization
        sentences = text.replace("\n", " ").split(". ")
        if len(sentences) <= 2:
            return text[:max_length] + "..." if len(text) > max_length else text

        # Take first sentence and key points
        summary = sentences[0]
        if len(summary) > max_length:
            return summary[:max_length] + "..."

        # Add second sentence if available
        if len(sentences) > 1:
            summary += ". " + sentences[1]
            if len(summary) > max_length:
                return summary[:max_length] + "..."

        return summary + "..."

    @tool
    def extract_key_points(self, text: str, max_points: int = 5) -> str:
        """Extract key points from text.

        Args:
            text: Text to analyze
            max_points: Maximum number of key points

        Returns:
            Key points as bullet list
        """
        if not text.strip():
            return "Empty text provided."

        # Simple extraction - split by sentences and filter
        sentences = [
            s.strip()
            for s in text.replace("\n", " ").split(". ")
            if len(s.strip()) > 20
        ]

        # Take first N substantial sentences
        key_points = sentences[:max_points]
        if not key_points:
            return "No key points found."

        return "\n".join(f"- {point}" for point in key_points)
