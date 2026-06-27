FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY .python-version ./

RUN pip install uv && uv sync --no-dev --frozen

COPY . .

CMD ["uv", "run", "bot.py"]
