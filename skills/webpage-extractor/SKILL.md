---
name: webpage-extractor
description: Fetch and extract full text content from a given URL. Use when search results only provide snippets and you need the complete article or page content to analyze.
---

## Instructions

1. Call the `internet_search` tool with the specific URL to fetch its content. Alternatively, use any available tool that can read a URL and return its content.
2. Extract the main body text from the response, filtering out navigation, ads, and boilerplate.
3. Return the cleaned text to the caller so it can be used in analysis or included in the report.

## Guidelines

- Preserve headings, lists, and important structure in the extracted content.
- If the URL is unreachable or returns an error, report that clearly — do not fabricate the content.
- Note the approximate length of the extracted content (e.g., "~1,200 words").
- If the page requires authentication or a paywall blocks access, say so.
