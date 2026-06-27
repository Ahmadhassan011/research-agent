import time
import hashlib
from datetime import datetime
from pathlib import Path
from src.agent import agent

OUTPUT_DIR = Path("output")
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries


def run_with_recovery(user_input: str, thread_id: str) -> dict:
    config = {"configurable": {"thread_id": thread_id}}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if attempt == 1:
                result = agent.invoke({"messages": user_input}, config)
            else:
                result = agent.invoke(None, config)

            return result

        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()
            remaining = MAX_RETRIES - attempt

            if remaining == 0:
                raise

            delay = RETRY_DELAY * (2 ** (attempt - 1))
            reason = "rate limit" if is_rate_limit else str(e).split("\n")[0][:80]
            print(f"  [{attempt}/{MAX_RETRIES}] {reason} — retrying in {delay}s ...")
            time.sleep(delay)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    user_input = input("Enter your query: ")

    thread_id = hashlib.sha256(user_input.encode()).hexdigest()[:16]

    print("Invoking agent ...\n")

    try:
        result = run_with_recovery(user_input, thread_id)
    except Exception as e:
        print(f"Failed after {MAX_RETRIES} attempts: {e}")
        return

    content = ""
    for msg in result["messages"]:
        if msg.type == "ai" and msg.content:
            content += msg.content + "\n\n"

    print(content)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"report_{timestamp}.md"
    output_path.write_text(content.strip())
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()
