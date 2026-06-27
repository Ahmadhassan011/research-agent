import re


def extract_text(content: str | list) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict) and "text" in c:
                parts.append(c["text"])
        return "\n".join(parts)
    return str(content)


def strip_markdown(text: str) -> str:
    return re.sub(r"[_*\[\]()~`>#!|{}=]", "", text)
