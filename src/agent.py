import os
import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from deepagents import create_deep_agent
from src.config import llm
from src.tools import internet_search

research_instructions = Path("prompts/system_prompt.md").read_text()

checkpoint_path = os.environ.get("CHECKPOINT_DB_PATH", "checkpoints.db")
conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

agent = create_deep_agent(
    model=llm,
    tools=[internet_search],
    system_prompt=research_instructions,
    checkpointer=checkpointer,
    skills=["./skills"],
)
