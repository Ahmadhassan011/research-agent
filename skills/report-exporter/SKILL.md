---
name: report-exporter
description: Export the finished research report in a specific output format — JSON, HTML, or plain text. Use when the user requests a format other than the default markdown report.
---

## Instructions

Convert the completed research report into the requested format.

### JSON Format

```json
{
  "title": "Report title",
  "summary": "2-3 sentence overview",
  "findings": [
    {
      "topic": "Sub-topic heading",
      "details": "Body text with key information",
      "sources": ["Source 1", "Source 2"]
    }
  ],
  "sources": [
    "Source 1 — description",
    "Source 2 — description"
  ]
}
```

### HTML Format

Wrap the report in semantic HTML:
- `<h1>` for the title
- `<h2>` for each finding section
- `<p>`, `<ul>`, `<li>` for body content
- Include a `<footer>` with the source list

### Plain Text Format

Strip all markdown formatting. Use:
- `===` for title underline
- `---` for section separation
- Simple indented lists with `*`

## Guidelines

- Preserve all content — do not truncate or summarize further during export.
- Maintain the same structure: summary, findings (by sub-topic), sources.
- If no format is specified, default to markdown (the standard report format).
