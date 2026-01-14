import argparse
import sys

from .agent import build_agent


def _extract_response(result):
    messages = result.get("messages", [])
    if messages:
        last = messages[-1]
        return last.content if hasattr(last, "content") else last.get("content")
    return result


def _run_interactive(agent):
    print("Ami interactive mode. Type 'exit' or 'quit' to leave.")
    while True:
        try:
            user_message = input("> ").strip()
        except EOFError:
            print()
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit"}:
            break

        result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
        print(_extract_response(result))


def _run_once(agent, prompt_parts):
    user_message = " ".join(prompt_parts)
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    print(_extract_response(result))


def main():
    parser = argparse.ArgumentParser(description="Run ami (minimal Deep Agents flow).")
    parser.add_argument("prompt", nargs="*", help="User message for ami")
    args = parser.parse_args()

    agent = build_agent()

    if args.prompt:
        _run_once(agent, args.prompt)
    else:
        _run_interactive(agent)


if __name__ == "__main__":
    main()
