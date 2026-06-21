# Regulatory Diff Tracker

A lightweight tool that monitors public regulatory pages (CFPB) for changes and summarizes what changed in plain English — automatically, using Claude.

## Why this exists

Fintech PMs spend a surprising amount of time watching regulatory pages for updates that could affect product decisions — new rules, disclosure requirements, deadline changes. This tool automates that watch and turns raw page diffs into actionable summaries.

## What it does

1. Fetches content from tracked CFPB regulatory pages
2. Compares against the last saved snapshot
3. If anything changed, generates a plain-English summary using Claude (Anthropic)
4. Logs all changes with timestamps to `change_log.json`

## Pages tracked (default)

- [CFPB Regulatory Agenda](https://www.consumerfinance.gov/rules-policy/regulatory-agenda/)
- [CFPB Recent Final Rules](https://www.consumerfinance.gov/rules-policy/final-rules/)

You can add any public URL to the `PAGES` list in `tracker.py`.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python tracker.py
```

## Output example

```
Checking: CFPB Recent Final Rules
  ! Change detected — summarizing with Claude...

  Summary:
  • A new final rule was added related to medical debt credit reporting
  • Effective date listed as Q3 2025 — product teams building credit decisioning flows should review
  • No changes to existing BNPL or open banking rules in this update
```

## Extending it

- Add a cron job or GitHub Action to run this daily
- Pipe summaries to Slack or email
- Add more regulatory sources (FTC, OCC, state-level)

