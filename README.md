# DeepResearch Agent

[![Python version](https://img.shields.io/badge/Python-3.13-3c873a?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq_Llama_3.3_70B-FF6600?style=flat-square&logo=groq&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

A research agent powered by deepagents and Groq (Llama 3.3 70B) that searches the web and writes structured reports, with CLI and Telegram interfaces.

[Features](#features) • [Prerequisites](#prerequisites) • [Installation](#installation) • [Usage](#usage) • [Deployment](#deployment)

## Features

- DuckDuckGo web search for information gathering
- Structured reports with summary, findings, and sources
- CLI and Telegram bot interfaces
- Crash recovery via SQLite checkpointing
- Skill system (planner, extractor, evaluator, exporter)
- Proxy support for restricted networks

## Prerequisites

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- [Groq API key](https://console.groq.com/keys)
- Telegram bot token via [@BotFather](https://t.me/botfather) (optional)
- Proxy if Telegram API is blocked in your region (optional)

## Installation

```bash
git clone https://github.com/Ahmadhassan011/research-agent.git
cd deepagents_001
uv sync
cp .env.example .env  # set GROQ_API_KEY and TELEGRAM_BOT_TOKEN
```

## Usage

**CLI mode:**

```bash
uv run main.py
```

Enter your question when prompted. Reports save to `output/report_<timestamp>.md`.

**Telegram bot:**

```bash
uv run bot.py
```

The bot shows live status (`🔍 Searching`, `✍️ Writing report...`) and sends the report as text and `.md` document.

> [!TIP]
> Casual messages (greetings, thanks) are handled immediately without invoking the research agent.

## Deployment

**Railway** — Nixpacks builder, set env vars in dashboard:

```bash
railway up
```

**Docker:**

```bash
docker build -t deepresearch-agent .
docker run -d --env-file .env deepresearch-agent
```
