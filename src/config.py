import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.environ.get("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model="qwen/qwq-32b:free",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
)
