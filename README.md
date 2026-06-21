# Regulatory Diff Tracker

A lightweight tool that monitors public regulatory pages (CFPB) for changes and summarizes what changed in plain English — automatically, using Claude.

## Why this exists

Fintech PMs in Southeast Asia spend a surprising amount of time watching MAS regulatory pages for updates that could affect product decisions — new rules, disclosure requirements, deadline changes. This tool automates that watch and turns raw page diffs into actionable summaries.

## What it does

1. Fetches content from tracked MAS (Monetary Authority of Singapore) regulatory pages
2. Compares against the last saved snapshot
3. If anything changed, generates a plain-English summary using Claude (Anthropic)
4. Logs all changes with timestamps to `change_log.json`

## Pages tracked (default)

- [MAS Regulations and Financial Stability](https://www.mas.gov.sg/regulation)
- [MAS News and Publications](https://www.mas.gov.sg/news)
- [MAS Consumer Guidance](https://www.mas.gov.sg/consumer-guidance)

You can add any public URL to the `PAGES` list in `tracker.py`.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python3 tracker.py
```

## Output example

```
Checking: MAS News and Publications
  ! Change detected — summarizing with Claude...

  Summary:
  • MAS issued updated guidelines on AI risk management for financial institutions
  • New requirements around consumer data disclosure for digital lending platforms
  • Effective Q3 2026 — product teams building credit decisioning flows should review
```

## Extending it

- Add a cron job or GitHub Action to run this daily
- Pipe summaries to Slack or email
- Add more regional sources (Bank Negara Malaysia, OJK Indonesia, RBI India)

