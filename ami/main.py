import argparse
import sys

from .agent import build_agent


def main():
    parser = argparse.ArgumentParser(description="Run ami (minimal Deep Agents flow).")
    parser.add_argument("prompt", nargs="*", help="User message for ami")
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a prompt, e.g.: python -m ami '你好，帮我规划本周学习任务'", file=sys.stderr)
        sys.exit(1)

    agent = build_agent()
    user_message = " ".join(args.prompt)
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    # LangGraph returns a message list in state; print the last assistant message.
    messages = result.get("messages", [])
    if messages:
        last = messages[-1]
        content = last.content if hasattr(last, "content") else last.get("content")
        print(content)
    else:
        print(result)


if __name__ == "__main__":
    main()
