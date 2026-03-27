import re
import os
import json
import glob
import logging

import pandas as pd

RAW_DIR = "data/raw"
OUT_PARQUET = "data/processed/bugs.parquet"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Build the final normalized text for one dataset record.
def build_text_all(rec: dict) -> str:
    issue_title = (rec.get("issue_title") or "").strip()
    issue_body_raw = rec.get("issue_body") or ""
    issue_comments_raw = rec.get("issue_comments") or []

    issue_body_clean = issue_body_raw
    issue_body_clean = remove_tags(issue_body_clean)
    issue_body_clean = remove_logs_and_traces(issue_body_clean)
    issue_body_clean = normalize_whitespace(issue_body_clean)
    issue_body_clean = trim_text(issue_body_clean, 5000)

    comment_chunks = []

    for comment in issue_comments_raw:
        if not comment:
            continue

        comment_clean = comment
        comment_clean = remove_tags(comment_clean)
        comment_clean = remove_logs_and_traces(comment_clean)
        comment_clean = normalize_whitespace(comment_clean)
        comment_clean = trim_text(comment_clean, 3000)

        if comment_clean:
            comment_chunks.append(f'"{comment_clean}"')

    chunks = []

    if issue_title:
        chunks.append(f"[TITLE] {issue_title}")
    if issue_body_clean:
        chunks.append(f"[ISSUE]\n{issue_body_clean}")
    if comment_chunks:
        chunks.append(f"[ISSUE_COMMENTS] {', '.join(comment_chunks)}")

    return "\n".join(chunks).strip().lower()


# Remove markdown images, markdown links, and HTML tags.
def remove_tags(text: str) -> str:
    md_img_re = re.compile(r"!\[[^\]]*\]\([^)]+\)")
    md_link_re = re.compile(r"\[([^\]]+)\]\([^)]+\)")
    tag_re = re.compile(r"<[^>]+>")

    # Remove markdown images.
    text = md_img_re.sub("", text)
    # Keep only visible text from markdown links.
    text = md_link_re.sub(r"\1", text)
    # Remove HTML tags.
    text = tag_re.sub("", text)

    return text


# Remove stack traces, log lines, URLs, and other noisy technical fragments.
def remove_logs_and_traces(text: str) -> str:
    patterns = [
        # Remove JS/TS stack frames with function names.
        re.compile(r"^\s*at\s+\S.+\(([^)]+):\d+(?::\d+)?\)\s*$", re.MULTILINE),

        # Remove JS/TS stack frames without function names.
        re.compile(r"^\s*at\s+\S+:\d+(?::\d+)?\s*$", re.MULTILINE),

        # Remove C# stack frames with file path and line number.
        re.compile(r"^\s*at\s+[\w\.]+\s+.*\s+in\s+.*:line\s+\d+\s*$", re.MULTILINE),

        # Remove log lines with standard log levels.
        re.compile(
            r"^\s*(?:\[[^\]]*\]\s*)?(DEBUG|INFO|WARN|WARNING|ERROR|TRACE|FATAL)\b.*$",
            re.MULTILINE,
        ),

        # Remove timestamped log lines.
        re.compile(
            r"^\s*\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+\-]\d{2}:\d{2})?\s+\S.*$",
            re.MULTILINE,
        ),

        # Remove URLs.
        re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE),

        # Remove standalone hexadecimal addresses.
        re.compile(r"^\s*0x[0-9a-fA-F]+\b.*$", re.MULTILINE),

        # Remove long horizontal separators made of ASCII characters.
        re.compile(r"^[\-\=_]{20,}\s*$", re.MULTILINE),

        # Remove long horizontal separators made of box-drawing characters.
        re.compile(r"^[\u2500-\u257F]{5,}.*$", re.MULTILINE),
    ]

    for pattern in patterns:
        text = pattern.sub("", text)

    return text


# Normalize line endings, trim trailing spaces, and collapse empty lines.
def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"(?:\n\s*){3,}", "\n\n", text)
    return text.strip()


# Iterate through non-empty JSONL lines.
def iterate_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                yield json.loads(line_str)


# Trim text softly by cutting at the first newline after the limit.
def trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    newline_pos = text.find("\n", limit)
    cut = text[:newline_pos] if newline_pos != -1 else text[:limit]
    return cut.strip()


jsonl_files = glob.glob(os.path.join(RAW_DIR, "*.jsonl"))

rows = []

for fp in jsonl_files:
    logging.info(f"Start processing {fp}")

    for rec in iterate_jsonl(fp):
        text = build_text_all(rec)
        if len(text) < 300:
            continue
        rows.append(
            {
                "repo": str(rec.get("repo", "")).strip(),
                "issue_number": str(rec.get("issue_number","")).strip(),
                "text": text,
            }
        )

    logging.info(
        f"file {fp} is processed. Current size of resulting file {len(rows)}"
    )

df = pd.DataFrame(rows, columns=["repo", "issue_number", "text"])
df.to_parquet(OUT_PARQUET, index=False)
