"""The agent graph.

A single ReAct loop. The LangGraph server supplies persistence per thread, so the
graph is compiled without a checkpointer of its own.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

# Absolute imports: the LangGraph server loads this file by path, so it has no
# parent package of its own and relative imports would fail.
from GeoAgent.configuration import load_chat_model
from GeoAgent.prompts import SYSTEM_PROMPT
from GeoAgent.tools import TOOLS

graph = create_react_agent(
    load_chat_model(),
    tools=TOOLS,
    prompt=SYSTEM_PROMPT,
    name="GeoAgent",
)
