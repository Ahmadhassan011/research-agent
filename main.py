import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path

from src.agent import agent
from src.utils import extract_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
MAX_RETRIES = 3
RETRY_DELAY = 5


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
            remaining = MAX_RETRIES - attempt

            if remaining == 0:
                raise

            delay = RETRY_DELAY * (2 ** (attempt - 1))
            reason = str(e).split("\n")[0][:80]
            logger.warning(
                "[%s/%s] %s — retrying in %ss ...", attempt, MAX_RETRIES, reason, delay
            )
            time.sleep(delay)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    user_input = input("Enter your query: ")
    thread_id = hashlib.sha256(user_input.encode()).hexdigest()[:16]

    logger.info("Invoking agent ...\n")

    try:
        result = run_with_recovery(user_input, thread_id)
    except Exception as e:
        logger.error("Failed after %s attempts: %s", MAX_RETRIES, e)
        return

    content = ""
    for msg in reversed(result["messages"]):
        if msg.type == "ai" and msg.content:
            raw = extract_text(msg.content)
            content = raw.strip()
            break

    print(content)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"report_{timestamp}.md"
    output_path.write_text(content)
    logger.info("Report saved to %s", output_path)


if __name__ == "__main__":
    main()
