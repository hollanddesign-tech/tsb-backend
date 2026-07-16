import json
from collections import defaultdict
from pull_trades import pull_trades, get_prop_value

def build_daily(pages):
    days = defaultdict(lambda: {"pnl": 0, "wins": 0, "losses": 0, "trades": 0})
    for page in pages:
        props = page["properties"]
        date = get_prop_value(props.get("Date", {}))
        pnl = get_prop_value(props.get("P&L ($)", {}))
        outcome = get_prop_value(props.get("Outcome", {}))
        if date is None or pnl is None:
            continue
        day_key = date[:10]
        days[day_key]["pnl"] += pnl
        days[day_key]["trades"] += 1
        if outcome == "Win":
            days[day_key]["wins"] += 1
        elif outcome == "Loss":
            days[day_key]["losses"] += 1

    result = []
    for day_key in sorted(days.keys()):
        d = days[day_key]
        decided = d["wins"] + d["losses"]
        win_rate = round((d["wins"] / decided) * 100, 1) if decided > 0 else 0

        if d["pnl"] > 0:
            outcome_label = "win"
        elif d["pnl"] < 0:
            outcome_label = "loss"
        else:
            outcome_label = "neutral"

        result.append({
            "day": day_key,
            "date": day_key,
            "pnl": round(d["pnl"], 2),
            "trades": d["trades"],
            "win_rate": win_rate,
            "outcome": outcome_label,
        })
    return result

def main():
    pages = pull_trades()
    result = build_daily(pages)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
