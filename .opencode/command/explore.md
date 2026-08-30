---
description: No-stakes brainstorming. Shape an idea before any spec is written. Creates NO files — just conversation.
---
# Command: explore

## Usage
`/explore [description-of-idea]` — `$ARGUMENTS` is any idea the user wants to explore.

## What it does
No-stakes brainstorming. Helps the user shape an idea before any spec is written. Creates NO files — just conversation.

## Execution Flow

1. **Greet + explain**: "Let's explore your idea. I'll ask some questions to help shape it. No files will be created — just thinking out loud."

2. **Ask what**: "What are you thinking about building? Describe the problem or feature." If `$ARGUMENTS` was provided, start from it.

3. **Probe context**: Read relevant project files (existing code, AGENTS.md, constitution). Ask targeted questions based on what you find.

4. **Identify constraints**: "What must we NOT break? Any preferred libraries or approaches?"

5. **Summarize**: "Here's what I understand: [summary]. Ready for /propose, or keep refining?"

## Constraints
- Do NOT create any files or write any code
- Stay conversational
