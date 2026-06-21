import os
import json
import hashlib
import difflib
import datetime
import requests
from bs4 import BeautifulSoup
import anthropic

PAGES = [
    {
        "name": "CFPB Regulatory Agenda",
        "url": "https://www.consumerfinance.gov/rules-policy/regulatory-agenda/",
    },
    {
        "name": "CFPB Recent Final Rules",
        "url": "https://www.consumerfinance.gov/rules-policy/final-rules/",
    },
]

SNAPSHOT_DIR = "snapshots"
LOG_FILE = "change_log.json"


def fetch_page_text(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def page_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_snapshot(name: str):
    path = os.path.join(SNAPSHOT_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_snapshot(name: str, text: str, hash_: str):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    path = os.path.join(SNAPSHOT_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"hash": hash_, "text": text, "captured_at": datetime.datetime.utcnow().isoformat()}, f)


def compute_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=3))
    return "\n".join(diff[:200])  # cap at 200 lines to keep prompt reasonable


def summarize_diff(page_name: str, diff_text: str) -> str:
    client = anthropic.Anthropic()
    prompt = f"""You are a regulatory analyst assistant helping a fintech Product Manager understand what changed on a government regulatory page.

Page: {page_name}

Here is the diff (lines starting with + were added, lines starting with - were removed):

{diff_text}

Write a concise plain-English summary (3-5 bullet points) of what changed and why it might matter to a fintech lending or consumer finance product team. Be specific — name rules, deadlines, or product areas if visible in the diff."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def load_log() -> list:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return []


def append_log(entry: dict):
    log = load_log()
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def run():
    print(f"Running regulatory diff tracker — {datetime.datetime.utcnow().isoformat()}\n")

    for page in PAGES:
        name = page["name"].replace(" ", "_").lower()
        url = page["url"]
        print(f"Checking: {page['name']}")

        try:
            current_text = fetch_page_text(url)
        except Exception as e:
            print(f"  ✗ Failed to fetch: {e}\n")
            continue

        current_hash = page_hash(current_text)
        snapshot = load_snapshot(name)

        if snapshot is None:
            save_snapshot(name, current_text, current_hash)
            print(f"  → First snapshot saved. No diff yet.\n")
            continue

        if snapshot["hash"] == current_hash:
            print(f"  ✓ No changes detected.\n")
            continue

        print(f"  ! Change detected — summarizing with Claude...")
        diff_text = compute_diff(snapshot["text"], current_text)
        summary = summarize_diff(page["name"], diff_text)

        entry = {
            "page": page["name"],
            "url": url,
            "detected_at": datetime.datetime.utcnow().isoformat(),
            "summary": summary,
        }
        append_log(entry)
        save_snapshot(name, current_text, current_hash)

        print(f"\n  Summary:\n")
        for line in summary.splitlines():
            print(f"    {line}")
        print()

    print("Done.")


if __name__ == "__main__":
    run()
