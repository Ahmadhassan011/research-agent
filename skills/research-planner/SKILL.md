---
name: research-planner
description: Decompose a broad or complex research query into structured sub-questions. Prioritize which information to gather first and identify the most promising search terms before the agent begins searching.
---

## Instructions

When given a research query, produce a research plan with these sections:

1. **Core Question** — Restate the user's main question in one sentence.

2. **Sub-Questions** — Break the query into 3–6 specific sub-questions that together answer the core question. Each sub-question should be independently searchable.

3. **Suggested Search Terms** — For each sub-question, list 1–3 search queries to try first. Vary the phrasing to cover different angles.

4. **Priority Order** — Number the sub-questions by priority:
   - High priority first (foundational facts, definitions, current state)
   - Lower priority later (nuances, comparisons, edge cases)
   - Mark as "optional" any sub-questions that can be skipped if time or results are limited.

5. **Success Criteria** — Briefly state what would constitute a sufficient answer for each sub-question (e.g., "at least 2 independent sources with current data").

Return the plan to the caller so they can begin executing searches.
