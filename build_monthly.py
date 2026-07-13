import json
from collections import defaultdict
from pull_trades import pull_trades, get_prop_value


def build_monthly(pages):
    months = defaultdict(lambda: {"pnl": 0, "wins": 0, "losses": 0, "trades": 0})

    for page in pages:
        props = page["properties"]
        date = get_prop_value(props.get("Date", {}))
        pnl = get_prop_value(props.get("P&L ($)", {}))
        outcome = get_prop_value(props.get("Outcome", {}))

        if date is None or pnl is None:
            continue

        month_key = date[:7]
        months[month_key]["pnl"] += pnl
        months[month_key]["trades"] += 1
        if outcome == "Win":
            months[month_key]["wins"] += 1
        elif outcome == "Loss":
            months[month_key]["losses"] += 1

    result = []
    for month_key in sorted(months.keys()):
        m = months[month_key]
        decided = m["wins"] + m["losses"]
        win_rate = round((m["wins"] / decided) * 100, 1) if decided > 0 else 0
        result.append({
            "month": month_key,
            "pnl": round(m["pnl"], 2),
            "trades": m["trades"],
            "win_rate": win_rate,
        })

    return result


def main():
    pages = pull_trades()
    result = build_monthly(pages)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
