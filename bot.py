import os
import re
import hashlib
import asyncio
import random
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from src.agent import agent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)
OUTPUT_DIR = Path("output")

# ── Casual intent detection ──────────────────────────────────────────────

CASUAL_RESPONSES = {
    "greeting": [
        "Hello! Send me a research question and I'll investigate it for you.",
        "Hi there! I'm a research agent. Give me a topic to look into.",
        "Hey! I can search the web and write reports. What do you want to research?",
    ],
    "thanks": [
        "You're welcome! Let me know if you need more research.",
        "Happy to help. Send me another topic anytime.",
        "Glad I could help! Anything else you want me to look into?",
    ],
    "farewell": [
        "Goodbye! Come back when you need more research.",
        "See you later! I'll be here when you need research done.",
    ],
    "how_are_you": [
        "I'm operational and ready to research. What can I investigate for you?",
        "Doing well! Ready to search the web. What's your topic?",
    ],
    "who_are_you": [
        "I'm a research agent. I search the internet for information and write structured reports. Send me a question and I'll get to work.",
    ],
    "default": [
        "I'm a research bot. I take questions, search the web, and write reports. Try me with a research topic.",
    ],
}

GREETING_WORDS = {"hi", "hello", "hey", "yo", "sup", "howdy"}
THANKS_WORDS = {"thanks", "thank", "ty", "thx"}
FAREWELL_WORDS = {"bye", "goodbye", "cya", "later"}


def classify_intent(text: str) -> tuple[str, str | None]:
    clean = text.strip().lower()
    words = set(clean.rstrip("?!.").split())

    if words & FAREWELL_WORDS:
        return "casual", "farewell"
    if words & GREETING_WORDS:
        return "casual", "greeting"
    if words & THANKS_WORDS:
        return "casual", "thanks"
    if (
        words & {"how", "howzit", "wassup"}
        and {"are", "you", "u", "it", "going"} & words
    ):
        return "casual", "how_are_you"
    if words & {"who", "what"} and {"are", "you", "is", "do", "can"} & words:
        return "casual", "who_are_you"
    if words & {"nice", "good"} and {"bot", "meet"} & words:
        return "casual", "default"

    return "research", None


def pick_response(category: str) -> str:
    return random.choice(CASUAL_RESPONSES.get(category, CASUAL_RESPONSES["default"]))


def strip_markdown(text: str) -> str:
    return re.sub(r"[_*\[\]()~`>#+\-!|{}=]", "", text)


def extract_search_queries(msg) -> list[str]:
    queries = []
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        for tc in msg.tool_calls:
            args = tc.get("args", {})
            if "query" in args:
                queries.append(args["query"])
    return queries


# ── Agent runner with streaming status ───────────────────────────────────


def stream_agent(
    user_input: str,
    status_queue: asyncio.Queue,
    loop: asyncio.AbstractEventLoop,
):
    thread_id = hashlib.sha256(user_input.encode()).hexdigest()[:16]
    config = {"configurable": {"thread_id": thread_id}}
    search_count = 0
    final_parts = []

    def emit(kind: str, text: str):
        loop.call_soon_threadsafe(status_queue.put_nowait, (kind, text))

    try:
        for event in agent.stream({"messages": user_input}, config):
            for node, output in event.items():
                if output is None or not isinstance(output, dict):
                    continue
                msgs = output.get("messages", [])
                if not msgs:
                    continue
                last = msgs[-1]

                if node == "model" and hasattr(last, "tool_calls") and last.tool_calls:
                    for q in extract_search_queries(last):
                        emit("search", q)

                if node == "tools":
                    search_count += 1

                if node == "model" and hasattr(last, "content") and last.content:
                    if search_count == 0:
                        final_parts.append(last.content)
                    else:
                        emit("writing", "✍️ Writing report...")
                        final_parts.append(last.content)

        emit(
            "done",
            "\n\n".join(final_parts) if final_parts else "No response generated.",
        )

    except Exception as e:
        logger.exception("Stream agent failed")
        emit("error", str(e))


# ── Telegram handlers ────────────────────────────────────────────────────


async def start(update: Update, _context):
    await update.message.reply_text(
        "I'm a research agent. Send me a topic and I'll search the web and write a report."
    )


async def handle_message(update: Update, context):
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id

    intent, category = classify_intent(user_input)
    if intent == "casual":
        await update.message.reply_text(pick_response(category or "default"))
        return

    status_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    status_msg = await update.message.reply_text("⏳ Starting research...")
    search_messages = []
    wrote_report = False
    final_text = None

    async def run():
        await loop.run_in_executor(
            executor, stream_agent, user_input, status_queue, loop
        )

    asyncio.create_task(run())

    while True:
        kind, text = await status_queue.get()

        if kind == "search":
            label = strip_markdown(text)[:80]
            search_messages.append(label)
            await status_msg.edit_text(f"🔍 Searching: {label}")
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        elif kind == "writing" and not wrote_report:
            wrote_report = True
            await status_msg.edit_text("✍️ Writing report...")
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        elif kind == "done":
            final_text = text
            break

        elif kind == "error":
            await status_msg.edit_text(f"❌ Error: {text}")
            return

    await status_msg.delete()

    if not final_text:
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"report_{timestamp}.md"

    file_path.write_text(final_text)

    MAX_LEN = 4000
    if len(final_text) > MAX_LEN:
        for i in range(0, len(final_text), MAX_LEN):
            await update.message.reply_text(final_text[i : i + MAX_LEN])
    else:
        await update.message.reply_text(final_text)

    with open(file_path, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=file_path.name,
            caption="📄 Full report",
        )


# ── Entry point ──────────────────────────────────────────────────────────


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_from_botfather":
        print("Set TELEGRAM_BOT_TOKEN in .env first.")
        return

    proxy = os.environ.get("PROXY_URL")
    if proxy:
        request = HTTPXRequest(proxy_url=proxy)
        app = Application.builder().token(token).request(request).build()
        print(f"  Using proxy: {proxy}")
    else:
        app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running ...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
