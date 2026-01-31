"""APO (Automatic Prompt Optimization) training script.

Uses Agent Lightning to optimize the orchestrator's system prompt.
"""

import asyncio
from pathlib import Path
from typing import Optional
import config

# Try to import agentlightning
try:
    from agentlightning.algorithm.apo import APO
    from agentlightning.algorithm.apo.config import APOConfig
    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False
    print("Warning: agentlightning not installed. Run: pip install agentlightning[apo]")

from agent.orchestrator import Orchestrator


def get_initial_prompt() -> str:
    """Get initial system prompt from config.

    Returns:
        Initial system prompt
    """
    return config.AGENT_SYSTEM_PROMPT


def create_train_dataset() -> list[dict]:
    """Create training dataset for APO.

    Returns:
        List of task examples with expected behaviors
    """
    return [
        {
            "task": "Help me write a Python function to calculate factorial",
            "expected_behavior": "Write clean, documented Python code with examples",
        },
        {
            "task": "What did we discuss yesterday about the project?",
            "expected_behavior": "Search episodic memory for relevant conversation",
        },
        {
            "task": "Remember that I prefer dark mode",
            "expected_behavior": "Store preference in semantic memory",
        },
        {
            "task": "Summarize the key points from our conversation",
            "expected_behavior": "Extract and condense main topics discussed",
        },
        {
            "task": "Find all Python files in the project",
            "expected_behavior": "Use file search tool to locate *.py files",
        },
    ]


def create_eval_dataset() -> list[dict]:
    """Create evaluation dataset for APO.

    Returns:
        List of task examples with expected behaviors
    """
    return [
        {
            "task": "Create a todo list for my day",
            "expected_behavior": "Help organize tasks in a clear format",
        },
        {
            "task": "I like to work on weekends",
            "expected_behavior": "Update semantic memory with preference",
        },
    ]


async def run_apo_training(
    output_path: str = "optimized_prompt.md",
    num_iterations: int = 10,
) -> Optional[str]:
    """Run APO training to optimize the system prompt.

    Args:
        output_path: Path to save optimized prompt
        num_iterations: Number of optimization iterations

    Returns:
        Optimized prompt or None if failed
    """
    if not AGENT_LIGHTNING_AVAILABLE:
        print("Error: agentlightning not installed")
        return None

    initial_prompt = get_initial_prompt()

    train_dataset = create_train_dataset()
    eval_dataset = create_eval_dataset()

    print(f"Initial prompt:\n{initial_prompt}\n")
    print(f"Training dataset: {len(train_dataset)} examples")
    print(f"Evaluation dataset: {len(eval_dataset)} examples")

    # Configure APO
    apo_config = APOConfig(
        initial_prompt=initial_prompt,
        task_dataset=train_dataset,
        eval_dataset=eval_dataset,
        max_iterations=num_iterations,
        evaluation_metric="helpfulness",
    )

    # Initialize APO
    apo = APO(config=apo_config)

    print("\nStarting APO optimization...")
    optimized_prompt = await apo.train()

    if optimized_prompt:
        # Save optimized prompt
        Path(output_path).write_text(optimized_prompt)
        print(f"\nOptimized prompt saved to: {output_path}")
        print(f"\nOptimized prompt:\n{optimized_prompt}")
    else:
        print("\nAPO training did not converge to an optimized prompt")

    return optimized_prompt


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="APO Training for Amy Agent")
    parser.add_argument(
        "--output", "-o",
        default="optimized_prompt.md",
        help="Path to save optimized prompt",
    )
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=10,
        help="Number of optimization iterations",
    )

    args = parser.parse_args()

    result = asyncio.run(run_apo_training(
        output_path=args.output,
        num_iterations=args.iterations,
    ))

    if not result:
        print("APO training failed. Check errors above.")


if __name__ == "__main__":
    main()
