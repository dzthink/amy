#!/usr/bin/env python3
"""CLI interface for Amy - Personal AI Agent."""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import structlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")

from agent.orchestrator import Orchestrator

logger = structlog.get_logger(__name__)


def check_api_key() -> bool:
    """Check if Anthropic API key is configured.

    Returns:
        True if API key is available
    """
    api_key = __import__("os").getenv("ANTHROPIC_API_KEY", "")
    return bool(api_key)


async def run_cli():
    """Run the interactive CLI."""
    print("=" * 50)
    print("  Amy - Personal AI Agent")
    print("  Type 'quit' or 'exit' to exit")
    print("  Type '/help' for commands")
    print("=" * 50)
    print()

    # Check API key
    if not check_api_key():
        print("ERROR: ANTHROPIC_API_KEY not found in .env file.")
        print("Please create .env file with:")
        print('  ANTHROPIC_API_KEY="your-api-key"')
        sys.exit(1)

    # Initialize orchestrator
    try:
        orchestrator = Orchestrator()
        print("Amy is ready! How can I help you today?\n")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

    # Simple conversation history
    conversation = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() == "/help":
            print("""
Available commands:
  /help     - Show this help message
  /memory   - Show current memory context
  /clear    - Clear conversation history
  /quit     - Exit the CLI
            """)
            continue

        if user_input.lower() == "/memory":
            context = orchestrator._get_memory_context()
            if context:
                print(f"\nMemory Context:\n{context}")
            else:
                print("\nNo memory context available.")
            continue

        if user_input.lower() == "/clear":
            conversation = []
            print("\nConversation history cleared.")
            continue

        # Process message
        print()
        try:
            result = await orchestrator.run(
                message=user_input,
                conversation_history=conversation,
                stream=True,
            )

            # Extract response
            if result and "messages" in result:
                response = result["messages"][-1].content
                if isinstance(response, list):
                    response = "".join(
                        c.get("text", "")
                        for c in response
                        if isinstance(c, dict)
                    )

                print(f"Amy: {response}")

                # Add to conversation
                conversation.append(
                    {"role": "user", "content": user_input}
                )
                conversation.append(
                    {"role": "assistant", "content": response}
                )

        except Exception as e:
            print(f"Error: {e}")
            logger.error("agent_error", error=str(e))


def main():
    """Main entry point."""
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(0),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
