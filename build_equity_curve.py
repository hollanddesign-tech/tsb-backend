"""
Builds equity curve + drawdown data from your Trades database.

Takes the same pulled trade data as pull_trades.py, sorts it oldest-to-newest,
then walks through it maintaining:
  - a running equity balance (starting balance + cumulative P&L)
  - the highest balance seen so far (the "peak")
  - drawdown = how far current equity has fallen below that peak

This is the exact calculation Notion formulas can't do (no "look at all
previous rows" logic) — which is why it lives here in Python instead.

Outputs a JSON array like:
  [{"date": "2026-07-06T09:15:00", "equity": 100300.0, "drawdown": 0.0}, ...]
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_your_token_here")
TRADES_DB_ID = os.environ.get("TRADES_DB_ID", "b2ca8c6b72034499b17038e07cb878c6")

STARTING_BALANCE = float(os.environ.get("STARTING_BALANCE", "100000"))

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


def build_equity_curve(pages):
    trades = []
    for page in pages:
        props = page["properties"]
        date = get_prop_value(props.get("Date", {}))
        pnl = get_prop_value(props.get("P&L ($)", {}))
        name = get_prop_value(props.get("Name", {}))
        if date is None or pnl is None:
            continue
        trades.append({"date": date, "pnl": pnl, "name": name})

    trades.sort(key=lambda t: t["date"])

    equity = STARTING_BALANCE
    peak = STARTING_BALANCE
    curve = []

    for t in trades:
        equity += t["pnl"]
        peak = max(peak, equity)
        drawdown = equity - peak

        curve.append({
            "date": t["date"],
            "trade": t["name"],
            "pnl": t["pnl"],
            "equity": round(equity, 2),
            "peak": round(peak, 2),
            "drawdown": round(drawdown, 2),
        })

    return curve


def main():
    pages = pull_trades()
    curve = build_equity_curve(pages)

    print(json.dumps(curve, indent=2))

    if curve:
        final = curve[-1]
        max_dd = min(c["drawdown"] for c in curve)
        print(f"\n--- Summary ---")
        print(f"Starting balance: ${STARTING_BALANCE:,.2f}")
        print(f"Final equity:     ${final['equity']:,.2f}")
        print(f"Max drawdown:     ${max_dd:,.2f}")


if __name__ == "__main__":
    main()
