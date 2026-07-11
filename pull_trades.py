import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_your_token_here")
TRADES_DB_ID = os.environ.get("TRADES_DB_ID", "b2ca8c6b72034499b17038e07cb878c6")

NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


def get_prop_value(prop):
    ptype = prop.get("type")
    if ptype == "title":
        return "".join(t["plain_text"] for t in prop["title"])
    if ptype == "select":
        return prop["select"]["name"] if prop["select"] else None
    if ptype == "number":
        return prop["number"]
    if ptype == "date":
        return prop["date"]["start"] if prop["date"] else None
    if ptype == "checkbox":
        return prop["checkbox"]
    if ptype == "formula":
        f = prop["formula"]
        return f.get(f["type"])
    if ptype == "relation":
        return [r["id"] for r in prop["relation"]]
    if ptype == "rollup":
        r = prop["rollup"]
        if r["type"] == "array":
            return [get_prop_value(item) if isinstance(item, dict) and "type" in item else item for item in r["array"]]
        return r.get(r["type"])
    return None


def pull_trades():
    url = f"https://api.notion.com/v1/databases/{TRADES_DB_ID}/query"
    all_results = []
    payload = {"page_size": 100}
    while True:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        all_results.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return all_results


def main():
    pages = pull_trades()
    print(f"Pulled {len(pages)} trades\n")
    for page in pages:
        props = page["properties"]
        name = get_prop_value(props.get("Name", {}))
        direction = get_prop_value(props.get("Direction", {}))
        pnl = get_prop_value(props.get("P&L ($)", {}))
        outcome = get_prop_value(props.get("Outcome", {}))
        r_multiple = get_prop_value(props.get("R Multiple", {}))
        session = get_prop_value(props.get("Session", {}))
        date = get_prop_value(props.get("Date", {}))
        print(f"{name:20} | {direction:6} | {date} | "
              f"P&L: ${pnl:>8.2f} | R: {r_multiple:>5.2f} | "
              f"{outcome:10} | {session}")


if __name__ == "__main__":
    main()
