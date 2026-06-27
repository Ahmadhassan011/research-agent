import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from deepagents import create_deep_agent
from src.config import llm
from src.tools import internet_search

research_instructions = Path("prompts/system_prompt.md").read_text()

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

agent = create_deep_agent(
    model=llm,
    tools=[internet_search],
    system_prompt=research_instructions,
    checkpointer=checkpointer,
)
