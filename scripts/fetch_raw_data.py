import requests
import json
import logging

OWNER = ""
REPO = ""
BASE_URL = "https://api.github.com"
TOKEN = ""  # assigned locally
OUTPUT_FILE = f"data/raw/raw_data_{REPO}.jsonl"
HEADERS = {"Authorization": f"token {TOKEN}"}
MAX_COMMENTS = 5
page = 1

total_written = 0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

while True:
    # Searching for the bugs with linked PRs (= real bug that was fixed via PR)
    search_url = f"{BASE_URL}/search/issues"
    q = f"repo:{OWNER}/{REPO} is:issue label:bug linked:pr"
    params = {"q": q, "per_page": 100, "page": page}

    logging.info(f"search params {params}")
    resp = requests.get(search_url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    issues_resp = resp.json()

    items = issues_resp.get("items", [])
    logging.info(f"[SEARCH] page={page}, items_on_page={len(items)}")

    if not items:
        break

    records_to_write = []

    for issue in items:
        issue_number = issue["number"]
        issue_labels = [lbl.get("name") for lbl in issue.get("labels", [])]
        issue_created_at = issue.get("created_at")
        logging.info(f"issue number {issue_number}")

        comments_url = f"{BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments"
        comments_resp = requests.get(
            comments_url,
            headers=HEADERS,
            params={"per_page": MAX_COMMENTS},
            timeout=30,
        )
        comments_resp.raise_for_status()
        comments = comments_resp.json()

        issue_comments = [comment.get("body") for comment in comments if comment.get("body")]

        current_data = {
            "repo": f"{OWNER}/{REPO}",
            "issue_number": issue_number,
            "issue_title": issue["title"],
            "issue_body": issue.get("body"),
            "issue_created_at": issue_created_at,
            "issue_labels": issue_labels,
            "issue_comments": issue_comments,
        }

        records_to_write.append(current_data)
        logging.info(f"records_to_write={len(records_to_write)}")
    # Create raw data file for particular repo
    if records_to_write:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
            for rec in records_to_write:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        total_written += len(records_to_write)

    page += 1
    logging.info(f"[SEARCH] next_page={page}, total_written={total_written}")

logging.info("Done.")
