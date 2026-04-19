---
description: default dev workflow
---

name: Terroir Dev Workflow

steps:
  1. Understand the task from the user prompt
  2. Read relevant files before making changes
  3. Make changes in small, testable increments
  4. After changes, verify the app still runs with: streamlit run app.py
  5. Do not modify requirements.txt unless explicitly asked

teaching_mode:
  - After every non-trivial change, add a short comment block explaining WHY
    this approach was chosen, not just WHAT it does
  - If there are alternative approaches, briefly mention them and the tradeoffs
  - When using a library feature that might be unfamiliar, add a one-liner
    explaining what it does
  - If a pattern is reusable beyond this project, flag it with: # PATTERN: ...