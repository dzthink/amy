"""Markdown storage helpers for todos and news topics."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _data_root() -> Path:
    override = os.getenv("AMY_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    # storage.py -> agent_core -> src -> agent -> repo root
    return Path(__file__).resolve().parents[4] / "data"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _read_list(path: Path) -> list[str]:
    if not path.exists():
        return []

    items: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- ["):
            closing = line.find("]")
            if closing != -1:
                item = line[closing + 1 :].strip()
                if item:
                    items.append(item)
            continue
        if line.startswith("- "):
            item = line[2:].strip()
            if item:
                items.append(item)
    return items


def _write_list(path: Path, header: str, items: Iterable[str], checkbox: bool) -> None:
    cleaned = [item.strip() for item in items if item and item.strip()]
    lines = [f"# {header}", ""]
    if cleaned:
        if checkbox:
            lines.extend([f"- [ ] {item}" for item in cleaned])
        else:
            lines.extend([f"- {item}" for item in cleaned])
    content = "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")


def read_todos() -> list[str]:
    root = _data_root() / "todos"
    path = root / "todos.md"
    return _read_list(path)


def write_todos(todos: Iterable[str]) -> None:
    root = _data_root() / "todos"
    _ensure_dir(root)
    path = root / "todos.md"
    _write_list(path, "Todos", todos, checkbox=True)


def read_news_topics() -> list[str]:
    root = _data_root() / "news"
    path = root / "topics.md"
    return _read_list(path)


def write_news_topics(topics: Iterable[str]) -> None:
    root = _data_root() / "news"
    _ensure_dir(root)
    path = root / "topics.md"
    _write_list(path, "News Topics", topics, checkbox=False)
