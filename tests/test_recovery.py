"""End-to-end checkpoint recovery test with a mock LLM."""

import time
import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_core.outputs import ChatGeneration, ChatResult

# --- Mock LLM that crashes once then recovers ---
call_count = 0


class MockLLM(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        global call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated API failure (rate limit)")
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content="Final answer from recovered run.")
                )
            ]
        )

    @property
    def _llm_type(self):
        return "mock"

    def bind_tools(self, tools, **kwargs):
        return self


# --- Setup ---
conn = sqlite3.connect(":memory:", check_same_thread=False)
checkpointer = SqliteSaver(conn)

mock_llm = MockLLM()

agent = create_deep_agent(
    model=mock_llm,
    tools=[],
    system_prompt="You are a helpful assistant.",
    checkpointer=checkpointer,
)

thread_id = "recovery-test-1"
config = {"configurable": {"thread_id": thread_id}}

# --- Step 1: First invoke crashes ---
print("=== Step 1: Invoke crashes ===")
try:
    agent.invoke({"messages": "hello"}, config)
except Exception as e:
    print(f"  Crashed: {e}")

state = agent.get_state(config)
print(f"  Checkpoint exists: {state is not None}")
print(f"  Next node after crash: {state.next}")

# --- Step 2: Resume from checkpoint ---
print("\n=== Step 2: Resume from checkpoint ===")
result = agent.invoke(None, config)

for msg in result["messages"]:
    if msg.type == "ai" and msg.content:
        print(f"  Output: {msg.content}")

# --- Step 3: Verify checkpoint data is in DB ---
print("\n=== Step 3: Checkpoint DB contents ===")
cursor = conn.execute("SELECT thread_id, checkpoint FROM checkpoints LIMIT 1")
row = cursor.fetchone()
print(f"  Thread ID in DB: {row[0]}")
print(
    f"  Checkpoint data size: {len(row[1])} bytes" if row[1] else "  No checkpoint data"
)

cursor = conn.execute("SELECT COUNT(*) FROM writes")
writes = cursor.fetchone()[0]
print(f"  Writes stored: {writes}")

print("\n✅ Recovery test passed")
