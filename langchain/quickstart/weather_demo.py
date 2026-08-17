"""Deep Agents + DeepSeek quickstart：天气查询 tool-calling 演示。

运行：
    uv run python quickstart/weather_demo.py
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, TypedDict

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class ChatMessage(TypedDict):
    role: Literal["user"]
    content: str


class AgentInput(TypedDict):
    messages: list[ChatMessage]


class AgentOutput(TypedDict):
    messages: list[BaseMessage]


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def _last_text(messages: list[BaseMessage]) -> str:
    last: BaseMessage = messages[-1]
    content: str | list[str | dict[str, object]] = last.content
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and "text" in block:
            parts.append(str(block["text"]))
    return "".join(parts)


def main() -> None:
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise SystemExit(
            "未找到 DEEPSEEK_API_KEY。请复制 .env.example 为 .env 并填入 Key。"
        )

    agent = create_deep_agent(
        model="deepseek:deepseek-v4-flash",
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
    )

    payload: AgentInput = {
        "messages": [
            {"role": "user", "content": "what is the weather in sf"},
        ]
    }
    result: AgentOutput = agent.invoke(payload)
    print(f"result: {result}\n\n")

    print(_last_text(result["messages"]))


if __name__ == "__main__":
    main()
