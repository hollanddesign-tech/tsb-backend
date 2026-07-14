"""
Computes per-setup stats (win rate, avg R multiple, times used) directly
from Trades data, matching each trade's "Setup" relation to a Setups
page ID — rather than trusting the Setups database's own rollup/formula
fields, which returned unreliable values via the API.
"""

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from pull_trades import pull_trades, pull_database, get_prop_value

load_dotenv()

SETUPS_DB_ID = os.environ.get("SETUPS_DB_ID", "your_setups_database_id_here")


def build_setups():
    setup_pages = pull_database(SETUPS_DB_ID)
    setup_names = {}
    for page in setup_pages:
        name = get_prop_value(page["properties"].get("Name", {}))
        setup_names[page["id"]] = name

    stats = defaultdict(lambda: {"wins": 0, "losses": 0, "trades": 0, "r_sum": 0.0})

    trades = pull_trades()
    for page in trades:
        props = page["properties"]
        setup_ids = get_prop_value(props.get("Setup", {})) or []
        outcome = get_prop_value(props.get("Outcome", {}))
        r_multiple = get_prop_value(props.get("R Multiple", {})) or 0

        for setup_id in setup_ids:
            s = stats[setup_id]
            s["trades"] += 1
            s["r_sum"] += r_multiple
            if outcome == "Win":
                s["wins"] += 1
            elif outcome == "Loss":
                s["losses"] += 1

    result = []
    for setup_id, s in stats.items():
        decided = s["wins"] + s["losses"]
        win_rate = round((s["wins"] / decided) * 100, 1) if decided > 0 else 0
        avg_r = round(s["r_sum"] / s["trades"], 2) if s["trades"] > 0 else 0

        result.append({
            "name": setup_names.get(setup_id, "Unknown Setup"),
            "win_rate": win_rate,
            "avg_r": avg_r,
            "times_used": s["trades"],
        })

    result.sort(key=lambda s: s["times_used"], reverse=True)
    return result


def main():
    result = build_setups()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
